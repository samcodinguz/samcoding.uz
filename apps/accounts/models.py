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

    last_activity = models.DateTimeField(null=True, blank=True)

    def is_profile_complete(self):
        return all([
            self.first_name,
            self.last_name,
            self.email,
            self.has_usable_password(),
        ])
    
    def is_online(self):
        if not self.last_activity:
            return False
        return timezone.now() - self.last_activity <= timedelta(minutes=1)

    def last_seen(self):
        if not self.last_activity:
            return "Kirilmagan"

        now = timezone.now()
        diff = now - self.last_activity
        seconds = diff.total_seconds()

        minutes = int(seconds // 60)
        hours   = int(seconds // 3600)
        days    = int(seconds // 86400)

        if minutes < 1:
            return "Hozir saytda"

        if minutes < 60:
            return f"{minutes} daqiqa oldin"

        if hours < 24:
            return f"{hours} soat oldin"

        if days < 7:
            return f"{days} kun oldin"

        weeks = days // 7
        if weeks < 4:
            return f"{weeks} hafta oldin"

        months = days // 30
        if months < 12:
            return f"{months} oy oldin"

        years = days // 365
        return f"{years} yil oldin"

    def __str__(self):
        return self.username

class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)