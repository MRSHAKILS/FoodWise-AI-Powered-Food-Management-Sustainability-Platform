from django.core.management.base import BaseCommand
from food.models import FoodItemDatabase


class Command(BaseCommand):
    help = 'Seeds the FoodItemDatabase with 20+ common food items'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting to seed food items database...'))
        
        food_items = [
            {
                'item_name': 'Milk',
                'category': 'dairy',
                'typical_expiration_days': 7,
                'sample_cost_per_unit': 350,
                'unit': 'liter',
                'storage_instructions': 'Keep refrigerated at 4°C',
                'nutritional_info': {'calories': 150, 'protein': 8, 'carbs': 12, 'fat': 8}
            },
            {
                'item_name': 'Eggs',
                'category': 'protein',
                'typical_expiration_days': 21,
                'sample_cost_per_unit': 400,
                'unit': 'dozen',
                'storage_instructions': 'Store in refrigerator',
                'nutritional_info': {'calories': 70, 'protein': 6, 'carbs': 1, 'fat': 5}
            },
            {
                'item_name': 'Chicken Breast',
                'category': 'protein',
                'typical_expiration_days': 2,
                'sample_cost_per_unit': 800,
                'unit': 'kg',
                'storage_instructions': 'Keep frozen or use within 2 days',
                'nutritional_info': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6}
            },
            {
                'item_name': 'Rice (White)',
                'category': 'grain',
                'typical_expiration_days': 365,
                'sample_cost_per_unit': 200,
                'unit': 'kg',
                'storage_instructions': 'Store in cool, dry place',
                'nutritional_info': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3}
            },
            {
                'item_name': 'Bananas',
                'category': 'fruit',
                'typical_expiration_days': 5,
                'sample_cost_per_unit': 150,
                'unit': 'kg',
                'storage_instructions': 'Store at room temperature',
                'nutritional_info': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3}
            },
            {
                'item_name': 'Apples',
                'category': 'fruit',
                'typical_expiration_days': 30,
                'sample_cost_per_unit': 300,
                'unit': 'kg',
                'storage_instructions': 'Refrigerate for longer life',
                'nutritional_info': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2}
            },
            {
                'item_name': 'Tomatoes',
                'category': 'vegetable',
                'typical_expiration_days': 7,
                'sample_cost_per_unit': 100,
                'unit': 'kg',
                'storage_instructions': 'Store at room temperature',
                'nutritional_info': {'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2}
            },
            {
                'item_name': 'Potatoes',
                'category': 'vegetable',
                'typical_expiration_days': 30,
                'sample_cost_per_unit': 80,
                'unit': 'kg',
                'storage_instructions': 'Store in cool, dark place',
                'nutritional_info': {'calories': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1}
            },
            {
                'item_name': 'Onions',
                'category': 'vegetable',
                'typical_expiration_days': 30,
                'sample_cost_per_unit': 70,
                'unit': 'kg',
                'storage_instructions': 'Store in cool, dry place',
                'nutritional_info': {'calories': 40, 'protein': 1.1, 'carbs': 9, 'fat': 0.1}
            },
            {
                'item_name': 'Carrots',
                'category': 'vegetable',
                'typical_expiration_days': 21,
                'sample_cost_per_unit': 90,
                'unit': 'kg',
                'storage_instructions': 'Refrigerate in plastic bag',
                'nutritional_info': {'calories': 41, 'protein': 0.9, 'carbs': 10, 'fat': 0.2}
            },
            {
                'item_name': 'Bread (Whole Wheat)',
                'category': 'grain',
                'typical_expiration_days': 5,
                'sample_cost_per_unit': 60,
                'unit': 'loaf',
                'storage_instructions': 'Store in cool, dry place or freeze',
                'nutritional_info': {'calories': 247, 'protein': 13, 'carbs': 41, 'fat': 3.4}
            },
            {
                'item_name': 'Yogurt',
                'category': 'dairy',
                'typical_expiration_days': 14,
                'sample_cost_per_unit': 120,
                'unit': '500g',
                'storage_instructions': 'Keep refrigerated',
                'nutritional_info': {'calories': 59, 'protein': 10, 'carbs': 3.6, 'fat': 0.4}
            },
            {
                'item_name': 'Cheese (Cheddar)',
                'category': 'dairy',
                'typical_expiration_days': 30,
                'sample_cost_per_unit': 500,
                'unit': '500g',
                'storage_instructions': 'Wrap tightly and refrigerate',
                'nutritional_info': {'calories': 403, 'protein': 25, 'carbs': 1.3, 'fat': 33}
            },
            {
                'item_name': 'Lentils (Red)',
                'category': 'protein',
                'typical_expiration_days': 365,
                'sample_cost_per_unit': 180,
                'unit': 'kg',
                'storage_instructions': 'Store in airtight container',
                'nutritional_info': {'calories': 116, 'protein': 9, 'carbs': 20, 'fat': 0.4}
            },
            {
                'item_name': 'Pasta',
                'category': 'grain',
                'typical_expiration_days': 730,
                'sample_cost_per_unit': 150,
                'unit': '500g',
                'storage_instructions': 'Store in cool, dry place',
                'nutritional_info': {'calories': 371, 'protein': 13, 'carbs': 75, 'fat': 1.5}
            },
            {
                'item_name': 'Cooking Oil',
                'category': 'other',
                'typical_expiration_days': 180,
                'sample_cost_per_unit': 300,
                'unit': 'liter',
                'storage_instructions': 'Store in cool place away from light',
                'nutritional_info': {'calories': 884, 'protein': 0, 'carbs': 0, 'fat': 100}
            },
            {
                'item_name': 'Spinach',
                'category': 'vegetable',
                'typical_expiration_days': 5,
                'sample_cost_per_unit': 60,
                'unit': 'bunch',
                'storage_instructions': 'Refrigerate in plastic bag',
                'nutritional_info': {'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4}
            },
            {
                'item_name': 'Cucumber',
                'category': 'vegetable',
                'typical_expiration_days': 7,
                'sample_cost_per_unit': 40,
                'unit': 'kg',
                'storage_instructions': 'Refrigerate',
                'nutritional_info': {'calories': 15, 'protein': 0.7, 'carbs': 3.6, 'fat': 0.1}
            },
            {
                'item_name': 'Orange Juice',
                'category': 'beverages',
                'typical_expiration_days': 7,
                'sample_cost_per_unit': 200,
                'unit': 'liter',
                'storage_instructions': 'Keep refrigerated after opening',
                'nutritional_info': {'calories': 45, 'protein': 0.7, 'carbs': 10, 'fat': 0.2}
            },
            {
                'item_name': 'Butter',
                'category': 'dairy',
                'typical_expiration_days': 90,
                'sample_cost_per_unit': 350,
                'unit': '500g',
                'storage_instructions': 'Keep refrigerated',
                'nutritional_info': {'calories': 717, 'protein': 0.9, 'carbs': 0.1, 'fat': 81}
            },
        ]
        
        created_count = 0
        existing_count = 0
        
        for item_data in food_items:
            item, created = FoodItemDatabase.objects.get_or_create(
                item_name=item_data['item_name'],
                defaults={
                    'category': item_data['category'],
                    'typical_expiration_days': item_data['typical_expiration_days'],
                    'sample_cost_per_unit': item_data['sample_cost_per_unit'],
                    'unit': item_data['unit'],
                    'storage_instructions': item_data['storage_instructions'],
                    'nutritional_info': item_data.get('nutritional_info'),
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {item.item_name} ({item.category})')
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠ Already exists: {item.item_name}')
                )
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'Food items seeding completed!'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} items'))
        self.stdout.write(self.style.WARNING(f'Existing: {existing_count} items'))
        self.stdout.write(self.style.SUCCESS(f'Total: {created_count + existing_count} items'))
        self.stdout.write(self.style.SUCCESS('='*60))
