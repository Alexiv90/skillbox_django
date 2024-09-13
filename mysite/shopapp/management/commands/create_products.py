from django.core.management import BaseCommand

from shopapp.models import Product

class Command(BaseCommand):
    """
    Creates products.
    """

    def handle(self, *args, **options):
        self.stdout.write('Creating products')
        products_name = [
            "Laptop",
            "Desktop",
            "Smartphone",
        ]
        for product_name in products_name:
            product, created = Product.objects.get_or_create(name=product_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product {product.name} with ID {product.id}'))
            else:
                self.stdout.write(self.style.ERROR(f'Product {product.name} with ID {product.id} already exists'))



        self.stdout.write(self.style.SUCCESS('Successfully created products'))