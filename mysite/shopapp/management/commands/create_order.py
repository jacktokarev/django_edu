from django.core.management import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Order

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        self.stdout.write("Создается заказ")
        user = User.objects.get(username="admin")
        order = Order.objects.get_or_create(
            delivery_address="ул. Южная, д.65",
            promocode="12RF34TY",
            user=user,
        )
        self.stdout.write(f"Создан заказ {order}")
