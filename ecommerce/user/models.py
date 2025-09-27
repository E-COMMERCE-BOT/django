from django.db import models

class User(models.Model):
    tg_id = models.PositiveBigIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    surname = models.CharField(max_length=50, null=True, blank=True)
    phone = models. CharField(max_length=16, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or ''} {self.lastname or ''} {self.surname or ''}".strip() or str(self.tg_id)
