from django.core.management.base import BaseCommand
from resources.models import Resource


class Command(BaseCommand):
    help = 'Seeds the Resource database with 20+ educational resources'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting to seed resources database...'))
        
        resources_data = [
            {
                'title': 'How to Store Dairy Products Properly',
                'description': 'Learn the best practices for extending the shelf life of milk, cheese, and yogurt. Proper storage techniques can significantly reduce waste and save money on dairy products.',
                'category': 'storage_tips',
                'type': 'article',
                'tags': ['dairy', 'storage', 'refrigeration'],
                'relevant_food_categories': ['dairy'],
                'read_time': 5
            },
            {
                'title': 'Meal Planning on a Budget',
                'description': 'Weekly meal planning strategies to reduce waste and save money on groceries. Learn how to create efficient meal plans that work for your budget and lifestyle.',
                'category': 'budget_tips',
                'type': 'guide',
                'tags': ['budget', 'meal planning', 'savings'],
                'relevant_food_categories': ['all'],
                'read_time': 10
            },
            {
                'title': 'Vegetable Storage Guide',
                'description': 'Proper storage methods for different vegetables to keep them fresh longer. Visual guide showing optimal temperature, humidity, and storage containers for various vegetables.',
                'category': 'storage_tips',
                'type': 'infographic',
                'tags': ['vegetables', 'storage', 'freshness'],
                'relevant_food_categories': ['vegetable'],
                'read_time': 3
            },
            {
                'title': 'Reducing Food Waste at Home',
                'description': 'Simple techniques to minimize food waste in your household. Discover practical tips for using leftovers, proper storage, and creative cooking to reduce waste.',
                'category': 'waste_reduction',
                'type': 'article',
                'tags': ['waste reduction', 'sustainability'],
                'relevant_food_categories': ['all'],
                'read_time': 7
            },
            {
                'title': 'Understanding Food Expiration Dates',
                'description': 'Learn the difference between sell-by, use-by, and best-before dates. This comprehensive guide helps you understand what these dates really mean for food safety.',
                'category': 'waste_reduction',
                'type': 'guide',
                'tags': ['expiration', 'food safety'],
                'relevant_food_categories': ['all'],
                'read_time': 5
            },
            {
                'title': 'Freezing Food: What You Need to Know',
                'description': 'Complete guide to freezing different food types safely. Learn which foods freeze well, proper packaging techniques, and how long items can be stored frozen.',
                'category': 'storage_tips',
                'type': 'guide',
                'tags': ['freezing', 'storage', 'preservation'],
                'relevant_food_categories': ['all'],
                'read_time': 8
            },
            {
                'title': 'Protein on a Budget',
                'description': 'Affordable protein sources and how to use them efficiently. Discover budget-friendly alternatives to expensive meat and ways to maximize protein intake.',
                'category': 'budget_tips',
                'type': 'article',
                'tags': ['protein', 'budget', 'nutrition'],
                'relevant_food_categories': ['protein'],
                'read_time': 6
            },
            {
                'title': 'Composting Kitchen Scraps',
                'description': 'How to start composting to reduce organic waste. Step-by-step video tutorial on setting up and maintaining a home composting system for kitchen scraps.',
                'category': 'waste_reduction',
                'type': 'video',
                'tags': ['composting', 'waste reduction', 'sustainability'],
                'relevant_food_categories': ['all'],
                'read_time': 12
            },
            {
                'title': 'Ripening and Storing Fruits',
                'description': 'Tips for ripening fruits and keeping them fresh. Learn which fruits ripen after picking, optimal storage conditions, and how to prevent premature spoiling.',
                'category': 'storage_tips',
                'type': 'article',
                'tags': ['fruits', 'ripening', 'storage'],
                'relevant_food_categories': ['fruit'],
                'read_time': 5
            },
            {
                'title': 'Batch Cooking for Busy Families',
                'description': 'Save time and reduce waste with batch cooking techniques. Learn how to prepare multiple meals at once and store them properly for the week ahead.',
                'category': 'meal_planning',
                'type': 'guide',
                'tags': ['batch cooking', 'meal prep', 'efficiency'],
                'relevant_food_categories': ['all'],
                'read_time': 10
            },
            {
                'title': 'Understanding Nutritional Labels',
                'description': 'How to read and understand food nutrition labels. Decode the information on food packaging to make healthier choices and understand serving sizes.',
                'category': 'nutrition',
                'type': 'article',
                'tags': ['nutrition', 'labels', 'health'],
                'relevant_food_categories': ['all'],
                'read_time': 6
            },
            {
                'title': 'Storing Grains and Dry Foods',
                'description': 'Best practices for storing rice, pasta, and other dry goods. Quick tips on containers, locations, and shelf life for pantry staples.',
                'category': 'storage_tips',
                'type': 'tip',
                'tags': ['grains', 'storage', 'pantry'],
                'relevant_food_categories': ['grain'],
                'read_time': 4
            },
            {
                'title': 'Seasonal Eating Guide',
                'description': 'Why eating seasonal produce is better for budget and environment. Comprehensive guide to seasonal fruits and vegetables and their environmental benefits.',
                'category': 'sustainability',
                'type': 'guide',
                'tags': ['seasonal', 'sustainability', 'budget'],
                'relevant_food_categories': ['fruit', 'vegetable'],
                'read_time': 8
            },
            {
                'title': 'Leftover Transformation Ideas',
                'description': 'Creative ways to use leftovers and reduce waste. Turn yesterday\'s dinner into today\'s delicious meal with these innovative recipe ideas.',
                'category': 'waste_reduction',
                'type': 'article',
                'tags': ['leftovers', 'recipes', 'waste reduction'],
                'relevant_food_categories': ['all'],
                'read_time': 7
            },
            {
                'title': 'Shopping List Strategies',
                'description': 'How to create efficient shopping lists that reduce waste. Strategic planning techniques to buy only what you need and stick to your budget.',
                'category': 'meal_planning',
                'type': 'guide',
                'tags': ['shopping', 'planning', 'waste reduction'],
                'relevant_food_categories': ['all'],
                'read_time': 5
            },
            {
                'title': 'Portion Control Basics',
                'description': 'Understanding portion sizes to avoid overcooking and waste. Learn proper serving sizes for different food groups and family members.',
                'category': 'nutrition',
                'type': 'article',
                'tags': ['portions', 'nutrition', 'waste reduction'],
                'relevant_food_categories': ['all'],
                'read_time': 6
            },
            {
                'title': 'Herb and Spice Storage',
                'description': 'Keeping herbs and spices fresh and flavorful. Quick tips on proper containers and storage locations to maximize shelf life.',
                'category': 'storage_tips',
                'type': 'tip',
                'tags': ['herbs', 'spices', 'storage'],
                'relevant_food_categories': ['other'],
                'read_time': 3
            },
            {
                'title': 'Budget-Friendly Vegetarian Meals',
                'description': 'Nutritious vegetarian meal ideas that won\'t break the bank. Discover affordable plant-based proteins and delicious recipes for every budget.',
                'category': 'budget_tips',
                'type': 'guide',
                'tags': ['vegetarian', 'budget', 'recipes'],
                'relevant_food_categories': ['vegetable', 'protein'],
                'read_time': 9
            },
            {
                'title': 'First In, First Out (FIFO) Method',
                'description': 'Organize your pantry and fridge to reduce expiration waste. Simple rotation system to ensure older items are used before newer purchases.',
                'category': 'waste_reduction',
                'type': 'tip',
                'tags': ['organization', 'FIFO', 'waste reduction'],
                'relevant_food_categories': ['all'],
                'read_time': 4
            },
            {
                'title': 'Hydration and Nutrition Basics',
                'description': 'Understanding daily nutritional needs and staying hydrated. Essential guide to balanced nutrition, water intake, and healthy eating habits.',
                'category': 'nutrition',
                'type': 'article',
                'tags': ['nutrition', 'health', 'hydration'],
                'relevant_food_categories': ['all'],
                'read_time': 7
            },
        ]
        
        created_count = 0
        existing_count = 0
        
        for resource_data in resources_data:
            resource, created = Resource.objects.get_or_create(
                title=resource_data['title'],
                defaults={
                    'description': resource_data['description'],
                    'category': resource_data['category'],
                    'type': resource_data['type'],
                    'tags': resource_data['tags'],
                    'relevant_food_categories': resource_data['relevant_food_categories'],
                    'read_time': resource_data['read_time'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {resource.title} ({resource.get_category_display()})')
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠ Already exists: {resource.title}')
                )
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'Resources seeding completed!'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} resources'))
        self.stdout.write(self.style.WARNING(f'Existing: {existing_count} resources'))
        self.stdout.write(self.style.SUCCESS(f'Total: {created_count + existing_count} resources'))
        self.stdout.write(self.style.SUCCESS('='*60))
