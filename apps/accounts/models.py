from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from apps.locations.models import Region, District

class CustomUser(AbstractUser):
    # You can add additional fields here if needed
    class ShirtSize(models.TextChoices):
        XS = "XS", "XS"
        S = "S", "S"
        M = "M", "M"
        L = "L", "L"
        XL = "XL", "XL"
        XXL = "XXL", "XXL"

    shirt_size = models.CharField(
        max_length=5,
        choices=ShirtSize.choices,
        blank=True,
        null=True
    )

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    school = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    tg_link = models.URLField(max_length=200, null=True, blank=True)
    gh_link = models.URLField(max_length=200, null=True, blank=True)
    cf_link = models.URLField(max_length=200, null=True, blank=True)
    fb_link = models.URLField(max_length=200, null=True, blank=True)

    def is_profile_complete(self):
        return all([
            self.first_name,
            self.last_name,
            self.email,
            self.has_usable_password(),
        ])

    def __str__(self):
        return self.username

class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)