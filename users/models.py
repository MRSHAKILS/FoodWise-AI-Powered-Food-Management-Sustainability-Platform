from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    full_name = models.CharField(max_length=255)
    household_size = models.IntegerField(default=1)
    dietary_preferences = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Monthly food budget limit")

    def __str__(self):
        return self.username
