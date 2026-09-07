from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.urls import reverse
from .utils import set_slug

# Create your models here.

User = get_user_model()

PRICE_SCALE = 1000

class Category(models.Model):
    title = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='category_images')
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('products:category-detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            set_slug(self, self.title)
        super().save(*args, **kwargs)

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.PositiveIntegerField()
    category = models.ManyToManyField(Category, related_name='category_products')
    is_available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()

    STATUS_CHOICES = (
        ('P', 'Published'),
        ('D', 'Draft'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.title

    def get_main_image(self):
        main_image = self.images.filter(is_main=True).first()
        if main_image:
            return main_image.image.url
        return None

    def sync_stock(self):
        if self.variants.exists():
            self.stock = self.variants.aggregate(total=models.Sum('stock'))['total'] or 0
            self.save(update_fields=['stock'])

    def save(self, *args, **kwargs):
        if not self.slug:
            set_slug(self, self.title)
        super().save(*args, **kwargs)

class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    option = models.CharField(max_length=32)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'option'],
                name='unique_product_option'
            )
        ]
    
class OptionValue(models.Model):
    option = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=32)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['value', 'option'],
                name='unique_option_value'
            )
        ]

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images')
    alt_text = models.CharField(max_length=64, blank=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_main=True),
                name='unique_main_image',
            )
        ]

    def save(self, *args, **kwargs):
        if self.is_main:
            with transaction.atomic():
                ProductImage.objects.filter(product=self.product, is_main=True).exclude(pk=self.pk).update(is_main=False)
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)
        
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    price_modifier = models.IntegerField()
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['product', 'price_modifier']
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'

    def __str__(self):
        return f"{self.product}'s variant"

    def get_final_price(self):
        return self.product.price + self.price_modifier

    def get_stock_display(self):
        return self.stock if self.stock > 0 else 'unavailable'

class VariantOption(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='options')
    option = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name='variant_options')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['variant', 'option'],
                name='unique_variant_option',
            )
        ]

    def save(self, *args, **kwargs):
        if self.variant.product != self.option.product:
            raise ValueError('invalid option')
        super().save(*args, **kwargs)

class VariantOptionValue(models.Model):
    variant_option = models.OneToOneField(VariantOption, on_delete=models.CASCADE, related_name='value')
    value = models.ForeignKey(OptionValue, on_delete=models.CASCADE, related_name='variant_values')

    def save(self, *args, **kwargs):
        if self.variant_option.option != self.value.option:
            raise ValueError('invalid value')
        super().save(*args, **kwargs)