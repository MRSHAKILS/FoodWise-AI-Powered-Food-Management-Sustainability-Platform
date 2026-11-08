"""
Management command to load dummy consumption and inventory data for testing.
This helps demonstrate the AI Consumption Pattern Analyzer functionality.

Usage: python manage.py load_dummy_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from food.models import ConsumptionLog, FoodItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Load dummy consumption logs and inventory data for testing AI Consumption Pattern Analyzer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to load data for (defaults to first user)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        clear_data = options.get('clear', False)

        # Get or create user
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found'))
                return
        else:
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
                return

        self.stdout.write(f'Loading dummy data for user: {user.username}')

        # Clear existing data if requested
        if clear_data:
            ConsumptionLog.objects.filter(user=user).delete()
            FoodItem.objects.filter(user=user).delete()
            self.stdout.write(self.style.WARNING('Cleared existing data'))

        today = timezone.now().date()

        # Load consumption logs (30 days of data with weekly patterns)
        self.load_consumption_logs(user, today)

        # Load inventory items (some expiring soon)
        self.load_inventory(user, today)

        self.stdout.write(self.style.SUCCESS(f'✓ Successfully loaded dummy data for {user.username}'))
        self.stdout.write(self.style.SUCCESS('Visit http://localhost:8000/food/analysis/ to see the AI analysis'))
        self.stdout.write(self.style.SUCCESS('Or access JSON API at http://localhost:8000/food/api/consumption-insights/'))

    def load_consumption_logs(self, user, today):
        """Create 30 days of consumption logs with realistic patterns."""
        
        logs_to_create = []
        
        # Pattern: Higher fruit/veg on weekdays, higher snacks on weekends
        for day_offset in range(30, 0, -1):
            consumption_date = today - timedelta(days=day_offset)
            day_of_week = consumption_date.weekday()  # 0=Monday, 6=Sunday
            is_weekend = day_of_week >= 5
            
            # Weekday pattern: More vegetables and balanced diet
            if not is_weekend:
                logs_to_create.extend([
                    ConsumptionLog(
                        user=user,
                        item_name='Spinach',
                        quantity=Decimal('0.3'),
                        unit='kg',
                        category='vegetable',
                        consumption_date=consumption_date,
                    ),
                    ConsumptionLog(
                        user=user,
                        item_name='Carrot',
                        quantity=Decimal('0.2'),
                        unit='kg',
                        category='vegetable',
                        consumption_date=consumption_date,
                    ),
                    ConsumptionLog(
                        user=user,
                        item_name='Chicken',
                        quantity=Decimal('0.15'),
                        unit='kg',
                        category='meat',
                        consumption_date=consumption_date,
                    ),
                    ConsumptionLog(
                        user=user,
                        item_name='Brown Rice',
                        quantity=Decimal('0.5'),
                        unit='cup',
                        category='grain',
                        consumption_date=consumption_date,
                    ),
                ])
                
                # 80% days include fruit
                if day_offset % 5 != 0:
                    logs_to_create.append(
                        ConsumptionLog(
                            user=user,
                            item_name='Apple',
                            quantity=Decimal('1'),
                            unit='piece',
                            category='fruit',
                            consumption_date=consumption_date,
                        )
                    )
            
            # Weekend pattern: More snacks and less vegetables
            else:
                logs_to_create.extend([
                    ConsumptionLog(
                        user=user,
                        item_name='Chips',
                        quantity=Decimal('0.1'),
                        unit='kg',
                        category='snack',
                        consumption_date=consumption_date,
                    ),
                    ConsumptionLog(
                        user=user,
                        item_name='Banana',
                        quantity=Decimal('2'),
                        unit='piece',
                        category='fruit',
                        consumption_date=consumption_date,
                    ),
                    ConsumptionLog(
                        user=user,
                        item_name='Pizza',
                        quantity=Decimal('2'),
                        unit='slice',
                        category='grain',
                        consumption_date=consumption_date,
                    ),
                ])
                
                # Only 40% of weekend days include vegetables
                if day_offset % 3 == 0:
                    logs_to_create.append(
                        ConsumptionLog(
                            user=user,
                            item_name='Broccoli',
                            quantity=Decimal('0.15'),
                            unit='kg',
                            category='vegetable',
                            consumption_date=consumption_date,
                        )
                    )
            
            # Dairy and beverages throughout
            logs_to_create.extend([
                ConsumptionLog(
                    user=user,
                    item_name='Milk',
                    quantity=Decimal('0.5'),
                    unit='liter',
                    category='dairy',
                    consumption_date=consumption_date,
                ),
                ConsumptionLog(
                    user=user,
                    item_name='Water',
                    quantity=Decimal('2'),
                    unit='liter',
                    category='beverage',
                    consumption_date=consumption_date,
                ),
            ])
        
        # Bulk create for efficiency
        ConsumptionLog.objects.bulk_create(logs_to_create)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(logs_to_create)} consumption logs'))

    def load_inventory(self, user, today):
        """Create inventory items with varied expiration dates."""
        
        items_to_create = [
            # Items expiring soon (3-5 days)
            FoodItem(
                user=user,
                name='Fresh Spinach',
                quantity=Decimal('0.5'),
                unit='kg',
                category='vegetable',
                purchase_date=today - timedelta(days=5),
                expiration_date=today + timedelta(days=2),  # Expires in 2 days
                price=Decimal('3.50'),
                notes='Leafy green - high waste risk',
            ),
            FoodItem(
                user=user,
                name='Milk',
                quantity=Decimal('2'),
                unit='liter',
                category='dairy',
                purchase_date=today - timedelta(days=7),
                expiration_date=today + timedelta(days=3),  # Expires in 3 days
                price=Decimal('4.00'),
                notes='Use for breakfast',
            ),
            FoodItem(
                user=user,
                name='Greek Yogurt',
                quantity=Decimal('1'),
                unit='kg',
                category='dairy',
                purchase_date=today - timedelta(days=2),
                expiration_date=today + timedelta(days=4),  # Expires in 4 days
                price=Decimal('5.50'),
            ),
            
            # Items expiring in 5-7 days
            FoodItem(
                user=user,
                name='Chicken Breast',
                quantity=Decimal('0.8'),
                unit='kg',
                category='meat',
                purchase_date=today - timedelta(days=1),
                expiration_date=today + timedelta(days=5),  # Expires in 5 days
                price=Decimal('12.00'),
                notes='Protein source',
            ),
            FoodItem(
                user=user,
                name='Broccoli',
                quantity=Decimal('0.6'),
                unit='kg',
                category='vegetable',
                purchase_date=today - timedelta(days=2),
                expiration_date=today + timedelta(days=5),  # Expires in 5 days
                price=Decimal('2.80'),
            ),
            
            # Items with longer shelf life
            FoodItem(
                user=user,
                name='Brown Rice',
                quantity=Decimal('2'),
                unit='kg',
                category='grain',
                purchase_date=today - timedelta(days=10),
                expiration_date=today + timedelta(days=60),  # Long shelf life
                price=Decimal('4.50'),
            ),
            FoodItem(
                user=user,
                name='Olive Oil',
                quantity=Decimal('1'),
                unit='liter',
                category='other',
                purchase_date=today - timedelta(days=30),
                expiration_date=today + timedelta(days=200),
                price=Decimal('15.00'),
            ),
            
            # Fruits (mixed expiration)
            FoodItem(
                user=user,
                name='Bananas',
                quantity=Decimal('1.2'),
                unit='kg',
                category='fruit',
                purchase_date=today - timedelta(days=1),
                expiration_date=today + timedelta(days=3),  # Expires in 3 days
                price=Decimal('2.00'),
            ),
            FoodItem(
                user=user,
                name='Apples',
                quantity=Decimal('1.5'),
                unit='kg',
                category='fruit',
                purchase_date=today - timedelta(days=3),
                expiration_date=today + timedelta(days=8),  # Expires in 8 days
                price=Decimal('3.50'),
            ),
            FoodItem(
                user=user,
                name='Oranges',
                quantity=Decimal('1'),
                unit='kg',
                category='fruit',
                purchase_date=today - timedelta(days=7),
                expiration_date=today + timedelta(days=10),  # Expires in 10 days
                price=Decimal('3.00'),
            ),
            
            # Snacks
            FoodItem(
                user=user,
                name='Chips',
                quantity=Decimal('0.5'),
                unit='kg',
                category='snack',
                purchase_date=today - timedelta(days=5),
                expiration_date=today + timedelta(days=30),
                price=Decimal('5.00'),
            ),
        ]
        
        FoodItem.objects.bulk_create(items_to_create)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(items_to_create)} inventory items'))
        
        # Print expiring items summary
        self.stdout.write('\n' + self.style.WARNING('Expiring Soon (3-7 days):'))
        expiring = FoodItem.objects.filter(
            user=user,
            expiration_date__lte=today + timedelta(days=7),
            expiration_date__gte=today
        )
        for item in expiring:
            days_left = (item.expiration_date - today).days
            self.stdout.write(f'  • {item.name} - {days_left} days left')
