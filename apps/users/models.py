from django.db import models


class User(models.Model):
    tg_id = models.PositiveBigIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=50, blank=True)
    lastname = models.CharField(max_length=50, blank=True)
    surname = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=16, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        full_name = " ".join(
            part
            for part in (self.name, self.lastname, self.surname)
            if part
        )
        return full_name or str(self.tg_id)
