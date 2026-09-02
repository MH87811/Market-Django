from django import forms
from .models import *


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ('name', 'value', 'price_modifier', 'stock')

    # def __init__(self, *args, **kwargs):
    #     self.product = kwargs.pop('product', None)
    #     super().__init__(*args, **kwargs)
    #
    # def save(self, commit=True):
    #     variant = super().save(commit=False)
    #     variant.product = self.product
    #     if commit:
    #         variant.save()
    #     return variant

ProductVariantFormset = forms.inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=3,
    can_delete=True,
)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('title', 'description', 'price', 'category', 'is_available')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        product = super().save(commit=False)
        product.user = self.user
        if commit:
            product.save()
            self.save_m2m()
        return product