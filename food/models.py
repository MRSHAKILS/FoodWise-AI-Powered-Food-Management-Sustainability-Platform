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


class MealPlan(models.Model):
    """AI-generated meal plans"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_plans')
    week_start_date = models.DateField()
    meals_data = models.JSONField(help_text='JSON format: [{day, meals: [{name, ingredients, cost, nutrients}]}]')
    shopping_list = models.JSONField(help_text='JSON format: [{item, quantity, estimatedCost}]')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2)
    nutrition_score = models.IntegerField(default=0, help_text='0-100 nutrition balance score')
    waste_reduction_estimate = models.CharField(max_length=255, blank=True)
    generated_by = models.CharField(max_length=50, default='AI', choices=[('AI', 'AI Generated'), ('Manual', 'Manual')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-week_start_date', '-created_at']
        verbose_name = 'Meal Plan'
        verbose_name_plural = 'Meal Plans'
    
    def __str__(self):
        return f"Meal Plan for {self.user.username} - Week of {self.week_start_date}"


class SDGScore(models.Model):
    """Track user's SDG impact score over time"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sdg_scores')
    score = models.IntegerField(default=0, help_text='Total SDG score (0-100)')
    waste_reduction_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nutrition_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    budget_efficiency_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    community_engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Metrics for calculation
    waste_reduced_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    waste_cost_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nutrition_balance = models.JSONField(null=True, blank=True)
    budget_data = models.JSONField(null=True, blank=True)
    
    # AI insights
    insights = models.TextField(blank=True, help_text='AI-generated weekly insights')
    recommendations = models.JSONField(default=list, help_text='Actionable recommendations')
    
    calculated_date = models.DateField(auto_now_add=True)
    week_number = models.IntegerField(help_text='ISO week number')
    year = models.IntegerField()
    
    class Meta:
        ordering = ['-calculated_date']
        verbose_name = 'SDG Score'
        verbose_name_plural = 'SDG Scores'
        unique_together = ['user', 'year', 'week_number']
    
    def __str__(self):
        return f"{self.user.username} - Week {self.week_number}/{self.year}: {self.score}/100"


class WasteLog(models.Model):
    """Track food waste for waste estimation model"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='waste_logs')
    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='units')
    category = models.CharField(max_length=20, choices=FoodItem.CATEGORY_CHOICES, default='other')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.CharField(
        max_length=20,
        choices=[
            ('expired', 'Expired'),
            ('spoiled', 'Spoiled'),
            ('excess', 'Excess Quantity'),
            ('quality', 'Poor Quality'),
            ('other', 'Other')
        ],
        default='expired'
    )
    waste_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-waste_date', '-created_at']
        verbose_name = 'Waste Log'
        verbose_name_plural = 'Waste Logs'
    
    def __str__(self):
        return f"Waste: {self.item_name} - {self.quantity} {self.unit} on {self.waste_date}"


class ChatSession(models.Model):
    """Store NourishBot chat sessions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    messages = models.JSONField(default=list, help_text='Chat history: [{role, content, timestamp}]')
    context_data = models.JSONField(null=True, blank=True, help_text='User context snapshot')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
    
    def __str__(self):
        return f"Chat {self.session_id} - {self.user.username}"
    
    def add_message(self, role, content):
        """Add a message to the chat history"""
        from datetime import datetime
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        self.save()
