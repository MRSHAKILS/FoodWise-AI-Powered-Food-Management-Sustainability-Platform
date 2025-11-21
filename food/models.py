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
    
    @property
    def is_expiring_soon(self):
        """Check if item is expiring within 7 days"""
        if self.expiration_date:
            days_left = self.days_until_expiration
            if days_left is not None:
                return 0 <= days_left <= 7
        return False
    
    @property
    def is_low_stock(self):
        """Check if item quantity is below threshold (2 units)"""
        return float(self.quantity) <= 2.0


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


class Recipe(models.Model):
    """Recipe database for meal planning"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    name = models.CharField(max_length=255, help_text='Name of the recipe')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='lunch')
    description = models.TextField(blank=True, help_text='Brief description of the dish')
    
    # Ingredients stored as JSON: [{"item": "rice", "quantity": 200, "unit": "g", "category": "grain"}]
    ingredients = models.JSONField(
        help_text='List of ingredients with quantities'
    )
    
    # Nutrition per serving
    nutrition = models.JSONField(
        help_text='Nutritional values: {"calories": 500, "protein": 20, "carbs": 60, "fat": 15}'
    )
    
    estimated_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text='Estimated cost in BDT per serving'
    )
    
    servings = models.IntegerField(default=2, help_text='Number of servings this recipe makes')
    prep_time = models.IntegerField(help_text='Preparation time in minutes')
    
    # Tags for filtering: ["vegetarian", "quick", "budget-friendly", "bangladeshi"]
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text='Tags for filtering recipes'
    )
    
    cooking_instructions = models.TextField(blank=True, help_text='Step-by-step cooking instructions')
    image_url = models.URLField(max_length=500, blank=True, help_text='Recipe image URL')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
    
    def __str__(self):
        return f"{self.name} ({self.meal_type})"
    
    def get_total_cost(self):
        """Calculate total cost for all servings"""
        return self.estimated_cost * self.servings


class MealPlan(models.Model):
    """Weekly meal plan for users"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='meal_plans'
    )
    
    week_start = models.DateField(help_text='Start date of the week (Monday)')
    week_end = models.DateField(help_text='End date of the week (Sunday)')
    
    # Budget information
    budget_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text='User budget for the week in BDT'
    )
    actual_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        help_text='Actual calculated cost'
    )
    
    # Meal structure: {"monday": {"breakfast": recipe_id, "lunch": recipe_id, "dinner": recipe_id}, ...}
    meals = models.JSONField(
        help_text='Weekly meal schedule with recipe IDs'
    )
    
    # Shopping list: [{"item": "rice", "quantity": 2, "unit": "kg", "cost": 200, "in_inventory": False}]
    shopping_list = models.JSONField(
        default=list,
        blank=True,
        help_text='Items needed to be purchased'
    )
    
    # Nutrition summary for the week
    nutrition_summary = models.JSONField(
        default=dict,
        blank=True,
        help_text='Weekly nutrition totals and daily averages'
    )
    
    # Inventory items used
    inventory_used = models.JSONField(
        default=list,
        blank=True,
        help_text='List of inventory items prioritized in this plan'
    )
    
    is_active = models.BooleanField(default=True, help_text='Is this the current active meal plan')
    notes = models.TextField(blank=True, help_text='Additional notes or preferences')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-week_start', '-created_at']
        verbose_name = 'Meal Plan'
        verbose_name_plural = 'Meal Plans'
        unique_together = ['user', 'week_start']  # One plan per week per user
    
    def __str__(self):
        return f"Meal Plan for {self.user.username} - Week of {self.week_start}"
    
    @property
    def budget_remaining(self):
        """Calculate remaining budget"""
        return self.budget_limit - self.actual_cost
    
    @property
    def budget_percentage_used(self):
        """Calculate percentage of budget used"""
        if self.budget_limit > 0:
            return (self.actual_cost / self.budget_limit) * 100
        return 0
    
    @property
    def total_meals(self):
        """Count total meals in plan"""
        count = 0
        for day_meals in self.meals.values():
            count += len(day_meals)
        return count
