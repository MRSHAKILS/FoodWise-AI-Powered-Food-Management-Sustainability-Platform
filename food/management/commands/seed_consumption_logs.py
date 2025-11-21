from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from food.models import ConsumptionLog
from users.models import User
import json
import os


class Command(BaseCommand):
    help = 'Seeds consumption logs from consumption_log.json for a specific user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to add consumption logs for',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username to add consumption logs for',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email to add consumption logs for',
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

        # Load consumption log data from JSON
        json_path = os.path.join('llms', 'consumption_log.json')
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'❌ File not found: {json_path}'))
            return

        with open(json_path, 'r') as f:
            data = json.load(f)

        consumption_logs = data.get('consumption_logs', [])
        
        if not consumption_logs:
            self.stdout.write(self.style.ERROR('❌ No consumption logs found in JSON'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'Starting to seed consumption logs for user: {user.username} (ID: {user.id})'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))

        created_count = 0
        skipped_count = 0

        for log_data in consumption_logs:
            item_name = log_data.get('item_name', 'Unknown Item')
            quantity = log_data.get('quantity', 0)
            unit = log_data.get('unit', 'units')
            category = log_data.get('category', 'Other').lower()
            consumption_date_str = log_data.get('consumption_date', str(timezone.now().date()))
            
            # Parse consumption date
            try:
                consumption_date = datetime.strptime(consumption_date_str, '%Y-%m-%d').date()
            except ValueError:
                consumption_date = timezone.now().date()

            # Map categories to ConsumptionLog category choices
            category_mapping = {
                'fruit': 'fruit',
                'dairy': 'dairy',
                'dairy/poultry': 'dairy',
                'grain': 'grain',
                'grain/snack': 'grain',
                'vegetable': 'vegetable',
                'fish/meat': 'meat',
                'meat': 'meat',
                'beverage': 'beverage',
                'snack': 'snack',
                'spice': 'other',
                'oil/fat': 'other',
                'dry good': 'other',
            }
            
            mapped_category = category_mapping.get(category, 'other')

            # Create consumption log
            consumption_log = ConsumptionLog.objects.create(
                user=user,
                item_name=item_name,
                quantity=quantity,
                unit=unit,
                category=mapped_category,
                consumption_date=consumption_date,
                notes='Sample consumption data'
            )
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created: {consumption_log.item_name} - {consumption_log.quantity} {consumption_log.unit} '
                    f'on {consumption_log.consumption_date}'
                )
            )

        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'Consumption logs seeding completed for {user.username}!'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} logs'))
        self.stdout.write(self.style.SUCCESS(f'Total consumption logs for user: {ConsumptionLog.objects.filter(user=user).count()}'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}'))
