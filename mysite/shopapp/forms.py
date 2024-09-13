from django import forms
from django.core import validators
from .models import Product, Order
from django.contrib.auth.models import Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = 'name',


# class ProductForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     price = forms.DecimalField(min_value=1, max_value=100_000, decimal_places=2)
#     description = forms.CharField(
#         label='Product description',
#         widget=forms.Textarea(attrs={'rows': '5', 'cols': '30'}),
#         validators=[validators.RegexValidator(
#             regex=r'great',
#             message='Field must contain world "great"',
#         )]
#     )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"
        widgets = {
            'description': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
        }
    images = forms.ImageField(
        widget=forms.ClearableFileInput(
            attrs={'allow_multiple_selected': True})
    )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "delivery_address", "promocode", "products", "user"
        widgets = {
            'delivery_address': forms.Textarea(attrs={'cols': 30, 'rows': 3, 'placeholder': 'Insert delivery address'}),
        }
        labels = {
            "delivery_address": ("Address for Delivery "),
        }
        help_texts = {
            "promocode": ("Some useful help text."),
        }

class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
