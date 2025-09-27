from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, null=False)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = models.TextField()
    photo = models.ImageField(upload_to='products/photos/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def is_available(self):
        return self.stock > 0

    def __str__(self):
        return self.name
