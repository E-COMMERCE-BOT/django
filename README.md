# E-Commerce Django API

Django REST Framework backend for a Telegram e-commerce bot.

## Features

- Telegram users identified by `tg_id`
- Bot-to-API authentication with `X-Bot-Api-Key`
- Nested product categories
- Product catalog with images and stock
- One active cart per user
- Transactional cart operations
- Transactional checkout with stock validation
- Delivery methods
- Order status management
- Django admin
- Automated tests and CI

## Setup

```bash
uv sync --extra dev
cp .env.example .env
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Tests and Quality

```bash
uv run pytest
uv run ruff format .
uv run ruff check . --fix
```

## API

Every request must include:

```text
X-Bot-Api-Key: <BOT_API_KEY>
```

Main endpoints:

```text
POST  /api/users/
GET   /api/users/{tg_id}/
PATCH /api/users/{tg_id}/

GET   /api/catalog/categories/
GET   /api/catalog/products/
POST  /api/catalog/products/
PATCH /api/catalog/products/{id}/

GET   /api/orders/cart/?tg_id={telegram_id}
POST  /api/orders/{id}/add_item/
POST  /api/orders/{id}/update_item/
POST  /api/orders/{id}/remove_item/
POST  /api/orders/{id}/checkout/
POST  /api/orders/{id}/set_status/

GET   /api/orders/deliveries/
```
