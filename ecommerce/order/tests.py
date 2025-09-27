"""Unit tests for core e-commerce models.

Covers basic creation, availability checks, order totals, auto-generated
order numbers, and error handling when querying non-existent objects.
"""

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from user.models import User
from product.models import Product, Category
from order.models import Order, OrderItem, Status, DeliveryType


class UserModelTest(TestCase):
    def test_create_user(self):
        """Ensure a user can be created successfully."""
        user = User.objects.create(tg_id=12345, name="Alex")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.name, "Alex")


class ProductModelTest(TestCase):
    def test_is_available(self):
        """Verify the is_available() method reflects stock correctly."""
        category = Category.objects.create(name="Clothes")
        product = Product.objects.create(
            name="T-Shirt",
            description="Desc",
            price=100,
            stock=2,
            category=category
        )
        self.assertTrue(product.is_available())
        product.stock = 0
        product.save()
        self.assertFalse(product.is_available())


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(tg_id=1, name="TestUser")
        self.status = Status.objects.create(name="Created", description="New order")
        self.delivery = DeliveryType.objects.create(
            name="Courier", description="Fast delivery", price=10
        )
        self.category = Category.objects.create(name="Tech")
        self.product = Product.objects.create(
            name="Phone",
            description="Smartphone",
            price=100,
            stock=5,
            category=self.category
        )

    def test_get_total(self):
        """Check get_total() = items subtotal + delivery price."""
        order = Order.objects.create(user=self.user, status=self.status, delivery_type=self.delivery)
        OrderItem.objects.create(order=order, product=self.product, quantity=2)
        self.assertEqual(order.get_total(), 210)  # 2 * 100 + 10 delivery

    def test_order_number_generated(self):
        """Ensure order number is generated with ORD- prefix."""
        order = Order.objects.create(user=self.user)
        self.assertTrue(order.number.startswith("ORD-"))


class ErrorHandlingTest(TestCase):
    def test_product_does_not_exist(self):
        """Expect ObjectDoesNotExist when querying a missing product."""
        with self.assertRaises(ObjectDoesNotExist):
            Product.objects.get(pk=999)
