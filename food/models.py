from django.db import models
from django.conf import settings
from django.utils import timezone


class FoodItemDatabase(models.Model):
    """Master database of common food items with typical properties"""
    CATEGORY_CHOICES = [
        ('fruit', 'Fruit'),
        ('dairy', 'Dairy'),
        ('grain', 'Grain'),
        ('vegetable', 'Vegetable'),
        ('protein', 'Protein'),
        ('snacks', 'Snacks'),
        ('beverages', 'Beverages'),
        ('other', 'Other'),
    ]
    
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('liter', 'Liter'),
        ('ml', 'Milliliter'),
        ('dozen', 'Dozen'),
        ('piece', 'Piece'),
        ('loaf', 'Loaf'),
        ('bunch', 'Bunch'),
        ('500g', '500g'),
    ]
    
    item_name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    typical_expiration_days = models.IntegerField(help_text='How many days item typically lasts')
    sample_cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, help_text='Average cost')
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')
    nutritional_info = models.JSONField(
        null=True, 
        blank=True,
        help_text='JSON format: {"calories": 100, "protein": 5, "carbs": 20, "fat": 2}'
    )
    storage_instructions = models.TextField(blank=True, help_text='How to store properly')
    image_url = models.URLField(max_length=500, blank=True, help_text='Placeholder image URL')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['item_name']
        verbose_name = 'Food Item Database Entry'
        verbose_name_plural = 'Food Items Database'
    
    def __str__(self):
        return f"{self.item_name} ({self.category})"


class FoodItem(models.Model):
    """Inventory management for food items"""
    CATEGORY_CHOICES = [
        ('vegetable', 'Vegetable'),
        ('fruit', 'Fruit'),
        ('dairy', 'Dairy'),
        ('meat', 'Meat'),
        ('grain', 'Grain'),
        ('beverage', 'Beverage'),
        ('snack', 'Snack'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='units')  # units, kg, liters, etc.
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    purchase_date = models.DateField(default=timezone.now)
    expiration_date = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Food Item'
        verbose_name_plural = 'Food Items'
    
    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"
    
    @property
    def is_expired(self):
        if self.expiration_date:
            return timezone.now().date() > self.expiration_date
        return False
    
    @property
    def days_until_expiration(self):
        if self.expiration_date:
            delta = self.expiration_date - timezone.now().date()
            return delta.days
        return None


class ConsumptionLog(models.Model):
    """Track daily food usage"""
    CATEGORY_CHOICES = [
        ('vegetable', 'Vegetable'),
        ('fruit', 'Fruit'),
        ('dairy', 'Dairy'),
        ('meat', 'Meat'),
        ('grain', 'Grain'),
        ('beverage', 'Beverage'),
        ('snack', 'Snack'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='consumption_logs')
    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='units')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    consumption_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-consumption_date', '-created_at']
        verbose_name = 'Consumption Log'
        verbose_name_plural = 'Consumption Logs'
    
    def __str__(self):
        return f"{self.item_name} - {self.quantity} {self.unit} on {self.consumption_date}"