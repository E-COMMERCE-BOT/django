from django.db import models
from decimal import Decimal

from user.models import User
from product.models import Product

class Status(models.Model):
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.name
    
class DeliveryType(models.Model):
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=100, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Order(models.Model):
    number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    status = models.ForeignKey(Status, related_name='orders', on_delete=models.SET_NULL, null=True)
    delivery_type = models.ForeignKey(DeliveryType, related_name='orders', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        total = Decimal("0.00")
        for item in self.items.all():
            total += item.get_total()  # тут уже должен возвращаться Decimal
        if self.delivery_type:
            total += self.delivery_type.price
        return total
        
    
    def save(self, *args, **kwargs):
        if not self.number:
            super().save(*args, **kwargs)
            self.number = f"ORD-{self.id:06d}"
            return super().save(update_fields=['number'])
        return super().save(*args, **kwargs)

    def __str__(self):
         return f"{self.number} ({self.user})"


class OrderItem(models.Model): 
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"