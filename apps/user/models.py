from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    img = models.FileField(upload_to='user/', blank=True, null=True)

    def __str__(self):
        return self.username