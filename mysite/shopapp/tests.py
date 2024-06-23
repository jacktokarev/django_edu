from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User, Permission
from django.db.models import Model
from django.contrib.contenttypes.models import ContentType
from .models import Product, Order

# Create your tests here.

class ProductCreateViewTestCase(TestCase):
    
    fixtures = [
        "shopapp/fixtures/users-fixture.json",
        "shopapp/fixtures/groups-fixture.json",
        "shopapp/fixtures/permissions-fixture.json",
        "shopapp/fixtures/group-permissions-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = {"username": "Jack2", "password": "siteuser2"}
        cls.user = User.objects.get(username=cls.credentials["username"])
        add_permission_for_user(
            cls.user, 
            create_permission(
                Product, "Can add Продукт", "add_product"
            )
        )
        add_permission_for_user(
            cls.user, 
            create_permission(
                Product, "Can view Продукт", "view_product"
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()


    def setUp(self):
        self.client.login(**self.credentials)
        return super().setUp()

    def test_product_create_view(self):
        response = self.client.post(
            reverse_lazy("shopapp:product_create"), {
            "name": "Wear",
            "description": "bla-bla",
            "price": 1234,
            "discount": 10,            
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy("shopapp:products"))

    def tearDown(self):
        self.client.logout()
        return super().tearDown()


class ProductListViewTestCase(TestCase):
    
    fixtures = [
        "shopapp/fixtures/session-fixture.json",
        "shopapp/fixtures/logentry-fixture.json",
        "shopapp/fixtures/users-fixture.json",
        "shopapp/fixtures/groups-fixture.json",
        "shopapp/fixtures/products-fixture.json",
        "shopapp/fixtures/permissions-fixture.json",
        "shopapp/fixtures/group-permissions-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()      
        cls.user = User.objects.create_user(
            pk=111,
            username="testuser",
            email="email@example.com",
        )
        add_permission_for_user(cls.user, create_permission(Product, "Can view Продукт", "view_product"))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()


    def setUp(self):
        self.client.force_login(self.user)
        super().setUp()

    def test_products_list_view(self):
        response = self.client.get(reverse("shopapp:products"))
        for product in Product.objects.filter(archived=False).all():
            self.assertContains(response, product.name)
        self.assertTemplateUsed(response, "shopapp/products_list.html")

    def tearDown(self):
        self.client.logout()
        super().tearDown()

      
class OrderDetailsViewTestCase(TestCase):
    
    fixtures = [
        "shopapp/fixtures/users-fixture.json",
        "shopapp/fixtures/groups-fixture.json",
        "shopapp/fixtures/products-fixture.json",
        "shopapp/fixtures/orders-fixture.json",
        "shopapp/fixtures/permissions-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            pk=111,
            username="testuser",
            email="email@example.com",
        )
        add_permission_for_user(cls.user, create_permission(Order, "Can view Заказ", "view_order"))
        
    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()
        super().tearDownClass()


    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        products = Product.objects.filter(archived=False).all()
        self.order = Order(user=self.user, promocode="dsjfasgfjg", delivery_address="DejhghcbB st/12")
        self.order.save()
        self.order.products.set(products)
        self.order.save()

    def test_order_detail_view(self):
        response = self.client.get(reverse("shopapp:order_details", kwargs={"pk":self.order.pk}))
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context["order"].id, self.order.id)
    
    def tearDown(self) -> None:
        self.order.delete()
        self.client.logout()
        super().tearDown()


class OrderExportViewTestCase(TestCase):
    
    fixtures = [
        "shopapp/fixtures/users-fixture.json",
        "shopapp/fixtures/groups-fixture.json",
        "shopapp/fixtures/products-fixture.json",
        "shopapp/fixtures/orders-fixture.json",
        "shopapp/fixtures/permissions-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            pk=111,
            username="testuser",
            email="email@example.com",
        )
        
        cls.user.is_staff = True
        cls.user.save()
        # add_permission_for_user(cls.user, create_permission(Order, "Can view Заказ", "view_order"))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()


    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_export_orders_json(self):
        orders = Order.objects.order_by("pk").select_related("user").prefetch_related("products").all()
        expected_data = [
            {
                "id": order.pk,
                "promocode": order.promocode,
                "delivery_address": order.delivery_address,
                "user_id": order.user.id,
                "products": [product.id for product in order.products.all()],
            }
            for order in orders
        ]
        response = self.client.get(reverse("shopapp:orders_data_export"))
        self.assertEqual(response.status_code, 200)
        orders_data = response.json()
        self.assertEqual(orders_data["orders"], expected_data)
        

    def tearDown(self):
        self.client.logout()
        super().tearDown()

# ------------------------------------------------------------------------------------------------------------------

def create_permission(object: Model, name: str, codename: str) -> Permission:
    permission = Permission.objects.create(
        codename=codename,
        name=name,
        content_type=ContentType.objects.get_for_model(object),
    )
    return permission

def add_permission_for_user(user: User, permission: Permission) -> None:
    user.user_permissions.add(permission)
    user.save()
