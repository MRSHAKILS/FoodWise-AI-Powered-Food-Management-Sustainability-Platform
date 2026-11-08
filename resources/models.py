from django.db import models
from django.db.models import Q


class Resource(models.Model):
    """Educational resources for sustainability, waste reduction, and food management"""
    
    CATEGORY_CHOICES = [
        ('waste_reduction', 'Waste Reduction'),
        ('budget_tips', 'Budget Tips'),
        ('meal_planning', 'Meal Planning'),
        ('storage_tips', 'Storage Tips'),
        ('nutrition', 'Nutrition'),
        ('sustainability', 'Sustainability'),
    ]
    
    TYPE_CHOICES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('infographic', 'Infographic'),
        ('guide', 'Guide'),
        ('tip', 'Tip'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(
        help_text='Description between 100-500 characters'
    )
    url = models.URLField(
        max_length=500,
        blank=True,
        help_text='External link to full resource'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='sustainability'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='article'
    )
    tags = models.JSONField(
        default=list,
        help_text='Array of keyword strings for searching'
    )
    relevant_food_categories = models.JSONField(
        default=list,
        help_text='Array of food categories: dairy, vegetable, fruit, grain, protein, all'
    )
    read_time = models.IntegerField(
        null=True,
        blank=True,
        help_text='Estimated minutes to read/watch'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['title']
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


def json_list_contains_any(field, values):
    """Q matching Resources whose JSON list `field` contains any of `values`.

    SQLite does not support JSONField `__contains`, so membership is checked in Python.
    """
    wanted = set(values)
    ids = [
        pk for pk, items in Resource.objects.values_list('id', field)
        if isinstance(items, list) and wanted.intersection(items)
    ]
    return Q(id__in=ids)
