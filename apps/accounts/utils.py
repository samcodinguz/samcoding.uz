import secrets
import hashlib
from django.urls import reverse
from django.conf import settings
from .models import PasswordResetToken
from django.core.mail import send_mail

def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    return all([has_upper, has_lower, has_digit, has_special])

def generate_reset_token(user):
    raw_token = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    PasswordResetToken.objects.filter(user=user).delete()

    PasswordResetToken.objects.create(
        user=user,
        token=token_hash
    )

    return raw_token


def send_password_reset_email(user):
    raw_token = generate_reset_token(user)

    reset_link = f"{settings.SITE_URL}{reverse('reset-confirm', args=[raw_token])}"

    send_mail(
        subject="Parolni tiklash",
        message=f"Parolni tiklash uchun havola:\n\n{reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )