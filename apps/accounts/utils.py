import os
import datetime
import random
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

def contribution(year=None):

    if year is None:
        year = datetime.date.today().year

    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)

    days = []

    first_weekday = start_date.weekday()
    days += [None] * first_weekday

    current = start_date
    while current <= end_date:

        count = [0] * 100 + [1] + [0] * 100 + [2] + [0] * 100 + [3] + [0] * 100 + [4] + [0] * 100
        count = count[random.randint(0, len(count) - 1)] 

        if count == 0:
            level = 0
        elif count == 1:
            level = 1
        elif count <= 3:
            level = 2
        else:
            level = 3

        days.append({
            "date": current,
            "count": count,
            "level": level
        })

        current += datetime.timedelta(days=1)

    # oxirini 7 ga to‘ldirish
    remainder = len(days) % 7
    if remainder:
        days += [None] * (7 - remainder)

    return days

def uid_filename(filename: str, length: int = 16) -> str:
    ext = os.path.splitext(filename)[1]
    random_name = secrets.token_hex(length // 2)
    return f"{random_name}{ext}"