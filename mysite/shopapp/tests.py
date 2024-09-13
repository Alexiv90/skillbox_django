from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from shopapp.utils import add_two_numbers
from shopapp.models import Product, Order
from django.urls import reverse
from string import ascii_letters
from random import choices
from django.conf import settings



class AddTwoNumbers(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(1, 2)
        self.assertEqual(result, 3)

class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()
    def test_product_create_view(self):
        response = self.client.post(
            reverse("shopapp:create_product"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "Test table",
                "discount": "10",
            }
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )

class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user('foo', 'myemail@test.com', 'bar')
        cls.product = Product.objects.create(name="Best product", created_by=User.objects.get(username='foo'))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.product.delete()
    #
    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )

        self.assertContains(response, self.product.name)

class ProductListViewTestCase(TestCase):
    fixtures = [
        'data.json'
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk
        )

class OrderListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Bobo', password='1234')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'auth-fixtures.json',
        'products-fixtures.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(
            reverse("shopapp:products-export")
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        product_data = response.json()
        self.assertEqual(
            product_data["products"],
            expected_data
        )

class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Leo', password='1234')
        permission_logentry = Permission.objects.get(
            codename='view_order'
        )
        cls.user.user_permissions.add(permission_logentry)


    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address="Test st 99",
            promocode="PROMO100",
            user=User.objects.get(username='Leo'),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()

    #
    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
        )
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context['order'].pk, self.order.pk)


class OrdersExportViewTestCase(TestCase):

    fixtures = [
        'auth-fixtures.json',
        'products-fixtures.json',
        'order-fixtures.json',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Leo',
                                            password='1234',
                                            is_staff=True
                                            )

    #
    def setUp(self):

        self.client.force_login(self.user)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()

    def test_get_orders_view(self):
        users_data = User.objects.order_by("pk").all()
        response = self.client.get(
            reverse("shopapp:orders-export")
        )
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()

        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "product_list": [p.pk for p in order.products.all()],
            }
            for order in orders
        ]
        order_data = response.json()
        # print(order_data)
        self.assertEqual(
            order_data["orders"],
            expected_data
        )

