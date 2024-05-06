from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager
from django.utils.translation import gettext_lazy as _
import datetime
from django.urls import reverse
import uuid
from django.utils import timezone


CURRENCIES = (
    ("EUR", "Euro"),
    ("USD", "US Dollar"),
    ("GBP", "British Pound Sterling"),
)

class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    currency = models.CharField(max_length=3, choices=CURRENCIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username", "currency"]
    objects = UserManager()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.first_name + " " + self.last_name
