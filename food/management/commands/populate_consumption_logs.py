from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from food.models import ConsumptionLog
from users.models import User


class Command(BaseCommand):
    help = 'Populate sample consumption logs for testing AI features'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='vlad',
            help='Username to add consumption logs for (default: vlad)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of history to create (default: 30)'
        )

    def handle(self, *args, **options):
        username = options['username']
        days = options['days']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return
        
        # Sample food items with realistic consumption patterns
        food_items = [
            # Fruits
            {'name': 'Apple', 'category': 'fruit', 'unit': 'pieces', 'freq': 0.7},
            {'name': 'Banana', 'category': 'fruit', 'unit': 'pieces', 'freq': 0.6},
            {'name': 'Orange', 'category': 'fruit', 'unit': 'pieces', 'freq': 0.5},
            {'name': 'Grapes', 'category': 'fruit', 'unit': 'grams', 'freq': 0.3},
            
            # Vegetables
            {'name': 'Carrot', 'category': 'vegetable', 'unit': 'pieces', 'freq': 0.5},
            {'name': 'Broccoli', 'category': 'vegetable', 'unit': 'grams', 'freq': 0.4},
            {'name': 'Spinach', 'category': 'vegetable', 'unit': 'grams', 'freq': 0.4},
            {'name': 'Tomato', 'category': 'vegetable', 'unit': 'pieces', 'freq': 0.6},
            {'name': 'Lettuce', 'category': 'vegetable', 'unit': 'grams', 'freq': 0.3},
            
            # Dairy
            {'name': 'Milk', 'category': 'dairy', 'unit': 'ml', 'freq': 0.8},
            {'name': 'Yogurt', 'category': 'dairy', 'unit': 'grams', 'freq': 0.5},
            {'name': 'Cheese', 'category': 'dairy', 'unit': 'grams', 'freq': 0.4},
            
            # Meat & Protein
            {'name': 'Chicken Breast', 'category': 'meat', 'unit': 'grams', 'freq': 0.5},
            {'name': 'Ground Beef', 'category': 'meat', 'unit': 'grams', 'freq': 0.3},
            {'name': 'Salmon', 'category': 'meat', 'unit': 'grams', 'freq': 0.2},
            {'name': 'Eggs', 'category': 'meat', 'unit': 'pieces', 'freq': 0.7},
            
            # Grains
            {'name': 'Rice', 'category': 'grain', 'unit': 'grams', 'freq': 0.6},
            {'name': 'Bread', 'category': 'grain', 'unit': 'slices', 'freq': 0.8},
            {'name': 'Pasta', 'category': 'grain', 'unit': 'grams', 'freq': 0.4},
            {'name': 'Oatmeal', 'category': 'grain', 'unit': 'grams', 'freq': 0.3},
            
            # Snacks
            {'name': 'Potato Chips', 'category': 'snack', 'unit': 'grams', 'freq': 0.3},
            {'name': 'Cookies', 'category': 'snack', 'unit': 'pieces', 'freq': 0.2},
            {'name': 'Dark Chocolate', 'category': 'snack', 'unit': 'grams', 'freq': 0.2},
        ]
        
        # Quantity ranges based on unit type
        quantity_ranges = {
            'pieces': (1, 3),
            'grams': (50, 300),
            'ml': (100, 500),
            'slices': (1, 4),
        }
        
        created_count = 0
        today = timezone.now().date()
        
        for day in range(days):
            date = today - timedelta(days=day)
            
            # Each day, consume 3-8 items
            daily_items = random.randint(3, 8)
            consumed_today = set()
            
            for _ in range(daily_items):
                # Select items based on frequency
                available_items = [item for item in food_items if item['name'] not in consumed_today]
                if not available_items:
                    break
                
                # Weight selection by frequency
                weights = [item['freq'] for item in available_items]
                selected = random.choices(available_items, weights=weights, k=1)[0]
                consumed_today.add(selected['name'])
                
                # Determine quantity
                min_qty, max_qty = quantity_ranges[selected['unit']]
                quantity = random.randint(min_qty, max_qty)
                
                # Create consumption log
                ConsumptionLog.objects.create(
                    user=user,
                    item_name=selected['name'],
                    quantity=quantity,
                    unit=selected['unit'],
                    category=selected['category'],
                    consumption_date=date,
                    notes=f'Sample data for {date}'
                )
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Created {created_count} consumption logs for user "{username}" over {days} days'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'You can now test the consumption analysis at: /food/ai/consumption-analysis/'
        ))
