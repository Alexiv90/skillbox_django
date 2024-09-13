from django.contrib.auth.models import User

from django.core.management import BaseCommand

from shopapp.models import Order, Product



class Command(BaseCommand):
    """
    Update the order
    """
    def handle(self, *args, **options):
        order = Order.objects.first()
        if not order:
            self.stdout.write(self.style.WARNING('No order found.'))
            return
        products = Product.objects.all()

        for product in products:
            order.products.add(product)

        order.save()
        self.stdout.write(self.style.SUCCESS(f'Succesfully added products {order.products.all()} to order {order}'))