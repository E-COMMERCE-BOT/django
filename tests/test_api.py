import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.catalog.models import Category, Product
from apps.orders.models import DeliveryType, OrderStatus

pytestmark = pytest.mark.django_db


@pytest.fixture
def headers(settings):
    settings.BOT_API_KEY = "test-key"
    return {"HTTP_X_BOT_API_KEY": "test-key"}


def test_create_user(client, headers):
    response = client.post(
        "/api/users/",
        {"tg_id": 123},
        content_type="application/json",
        **headers,
    )

    assert response.status_code == 201
    assert response.json()["tg_id"] == 123


def test_cart_checkout_flow(client, headers):
    category = Category.objects.create(name="Clothes")
    product = Product.objects.create(
        name="T-Shirt",
        description="Basic",
        photo=SimpleUploadedFile(
            "photo.jpg",
            b"fake-image",
            content_type="image/jpeg",
        ),
        price="19.99",
        stock=3,
        category=category,
    )
    delivery = DeliveryType.objects.create(
        name="Courier",
        description="Fast",
        price="5.00",
    )

    cart_response = client.get(
        "/api/orders/cart/?tg_id=100",
        **headers,
    )
    assert cart_response.status_code == 200
    cart_id = cart_response.json()["id"]

    add_response = client.post(
        f"/api/orders/{cart_id}/add_item/",
        {"product_id": product.id, "quantity": 2},
        content_type="application/json",
        **headers,
    )
    assert add_response.status_code == 200

    checkout_response = client.post(
        f"/api/orders/{cart_id}/checkout/",
        {"delivery_id": delivery.id},
        content_type="application/json",
        **headers,
    )
    assert checkout_response.status_code == 200
    assert checkout_response.json()["status"] == OrderStatus.CREATED

    product.refresh_from_db()
    assert product.stock == 1
