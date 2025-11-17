from django.contrib.auth.models import AbstractUser
from django.db import models

from authentication.choices import UserType


# Create your models here.
class UserProfile(AbstractUser):
    phone = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10)
    user_type = models.CharField(
        choices=UserType.choices, default=UserType.CUSTOMER.value
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
