from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from typing import Sequence
from shopapp.models import Order, Product

class Command(BaseCommand):
    """
    Creates orders.
    """
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating order with products')
        user = User.objects.get(username='admin')
        products: Sequence[Product] = Product.objects.all()
        order, created = Order.objects.get_or_create(
            delivery_address='Petrogradka st, 8',
            promocode='SALE2024',
            user=user,
        )

        for product in products:
            order.products.add(product)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created order ID {order.id}'))
        else:
            self.stdout.write(self.style.ERROR(f'Order with ID {order.id} already exists'))


        order.save()
        self.stdout.write(self.style.SUCCESS('Successfully created order'))