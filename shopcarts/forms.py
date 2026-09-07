from django import forms
from .models import *

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ('product', 'variant', 'quantity')

    def clean(self):
        cleaned_data = super().clean()

        product = cleaned_data.get('product')
        variant = cleaned_data.get('variant')

        if not product:
            return cleaned_data

        if variant and variant.product != product:
            raise forms.ValidationError('invalid variant')

        if product.variants.exists() and not variant:
            raise forms.ValidationError('please select a variant')

        return cleaned_data
