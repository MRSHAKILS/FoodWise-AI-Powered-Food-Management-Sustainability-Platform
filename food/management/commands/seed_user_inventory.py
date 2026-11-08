from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from food.models import FoodItem
from users.models import User
import json
import os


class Command(BaseCommand):
    help = 'Seeds food inventory from food_data.json for a specific user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to add inventory for',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username to add inventory for',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email to add inventory for',
        )

    def handle(self, *args, **options):
        # Find user
        user = None
        if options.get('user_id'):
            try:
                user = User.objects.get(id=options['user_id'])
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ User with ID {options["user_id"]} not found'))
                return
        elif options.get('username'):
            try:
                user = User.objects.get(username=options['username'])
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ User with username "{options["username"]}" not found'))
                return
        elif options.get('email'):
            try:
                user = User.objects.get(email=options['email'])
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ User with email "{options["email"]}" not found'))
                return
        else:
            # Get the first user if no specific user specified
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('❌ No users found in database'))
                return
            self.stdout.write(self.style.WARNING(f'⚠ No user specified, using first user: {user.username} (ID: {user.id})'))

        # Load food data from JSON
        json_path = os.path.join('llms', 'food_data.json')
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'❌ File not found: {json_path}'))
            return

        with open(json_path, 'r') as f:
            data = json.load(f)

        food_items = data.get('food_items', [])
        
        if not food_items:
            self.stdout.write(self.style.ERROR('❌ No food items found in JSON'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'Starting to seed inventory for user: {user.username} (ID: {user.id})'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))

        created_count = 0
        skipped_count = 0
        
        today = timezone.now().date()

        for item_data in food_items:
            item_name = item_data.get('item_name', 'Unknown Item')
            category = item_data.get('category', 'Other').lower()
            quantity = item_data.get('quantity', 1)
            unit = item_data.get('unit', 'pcs')
            typical_expiration_days = item_data.get('typical_expiration_days', 7)
            cost = item_data.get('sample_cost_per_unit', 0)

            # Map categories to FoodItem category choices
            category_mapping = {
                'fruit': 'fruit',
                'dairy': 'dairy',
                'dairy/poultry': 'dairy',
                'grain': 'grain',
                'grain/snack': 'grain',
                'fish/meat': 'meat',
                'vegetable': 'vegetable',
                'spice': 'other',
                'oil/fat': 'other',
                'dry good': 'other',
            }
            
            mapped_category = category_mapping.get(category, 'other')
            
            # Calculate expiration date
            expiration_date = today + timedelta(days=typical_expiration_days)
            
            # Check if item already exists for this user
            existing = FoodItem.objects.filter(user=user, name=item_name).exists()
            
            if existing:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'⚠ Skipped (already exists): {item_name}'))
                continue

            # Create food item
            food_item = FoodItem.objects.create(
                user=user,
                name=item_name,
                quantity=quantity,
                unit=unit,
                category=mapped_category,
                purchase_date=today,
                expiration_date=expiration_date,
                price=cost,
                notes=f'Auto-seeded from food_data.json'
            )
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created: {food_item.name} - {food_item.quantity} {food_item.unit} '
                    f'(Expires: {food_item.expiration_date})'
                )
            )

        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'Inventory seeding completed for {user.username}!'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} items'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count} items (already existed)'))
        self.stdout.write(self.style.SUCCESS(f'Total items in user inventory: {FoodItem.objects.filter(user=user).count()}'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}'))
