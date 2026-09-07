from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.constraints import UniqueConstraint
from django.contrib.auth import get_user_model
import uuid

# Create your models here.

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s cart"

    def calculate_total_price(self):
        return sum((item.get_total_price() * item.quantity) for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='cart_items')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.PROTECT, related_name='cart_items', blank=True, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.product} x {self.quantity}'

    def get_total_price(self):
        return (self.product.price if not self.variant else self.variant.get_final_price()) * self.quantity

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['cart', 'product', 'variant'],
                name='unique_product_variant_per_cart',
            )
        ]