from django.core.management import BaseCommand
from shopapp.models import Product

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        self.stdout.write("Создается продукт")
        product=Product.objects.get_or_create(
            name="Брюки",
            description="Описание брюк....",
            price=8234.52,
            discount=12,
        )
        self.stdout.write(f"Создан продукт {product}")
