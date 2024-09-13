from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return f"products/product_{instance.pk}/preview/{filename}"

class Product(models.Model):
    """
    Модель Product представляет товар,
    который можно купить в магазине

    Заказы тут: :model:`shopapp.Order`
    """
    class Meta:
        ordering = ['name', 'price']
        # db_table = 'product'
        verbose_name_plural =  _('Products')
        verbose_name = _('Product')

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    discount = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    preview = models.ImageField(upload_to=product_preview_directory_path, null=True, blank=True)

    # @property
    # def description_short(self)->str:
    #     if len(self.description) < 50:
    #         return self.description
    #     else:
    #         return self.description[:50] + '...'

    def get_absolute_url(self):
        return reverse('shopapp:product_details', kwargs={'pk': self.pk})

    def __str__(self) ->str:
        return f"Product(pk={self.pk}, name={self.name})"


def product_image_directory_path(instance: "Product", filename: str) -> str:
    return f"products/product_{instance.pk}/images/{filename}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)

class Order(models.Model):
    class Meta:
        verbose_name_plural = _('Orders')
        verbose_name = _('Order')

    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    receipt = models.FileField(null=True, upload_to="orders/receipts")

    def get_absolute_url(self):
        return reverse('shopapp:order_details', kwargs={'pk': self.pk})
