from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date

class FoodCategory(models.TextChoices):
    FRUIT = 'FRUIT', 'Fruit'
    VEGETABLE = 'VEG', 'Vegetable'
    DAIRY = 'DAIRY', 'Dairy'
    MEAT = 'MEAT', 'Meat'
    GRAIN = 'GRAIN', 'Grain'
    SNACK = 'SNACK', 'Snack'
    OTHER = 'OTHER', 'Other'

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=FoodCategory.choices)
    average_shelf_life_days = models.IntegerField(default=7)

    def __str__(self):
        return self.name

class PantryItem(models.Model):
    """Items currently in the user's inventory (potential waste)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1.0)
    unit = models.CharField(max_length=20, default='units')
    purchase_date = models.DateField()
    
    @property
    def expiry_date(self):
        return self.purchase_date + timedelta(days=self.food_item.average_shelf_life_days)

    def __str__(self):
        return f"{self.food_item.name} (Bought: {self.purchase_date})"

class ConsumptionLog(models.Model):
    """Record of what was actually eaten (pattern analysis)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.FloatField()
    date_consumed = models.DateField(default=date.today)

    def __str__(self):
        return f"Consumed {self.food_item.name} on {self.date_consumed}"