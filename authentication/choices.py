from django.db import models


class UserType(models.TextChoices):
    """Choices for the User Type."""

    CUSTOMER = "customer", "Customer"
    ADMIN = "admin", "Admin"
