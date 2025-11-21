#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from food.services import ConsumptionAnalyzer
import json

User = get_user_model()
user = User.objects.first()

if user:
    analyzer = ConsumptionAnalyzer(user)
    
    # Generate full report
    report = analyzer.generate_report()
    
    print('=== FULL REPORT KEYS ===')
    print(list(report.keys()))
    
    print('\n=== HEATMAP ===')
    print(f'Type: {type(report["heatmap"]).__name__}')
    print(f'Keys: {list(report["heatmap"].keys())}')
    
    print('\n=== WEEKLY TRENDS ===')
    print(f'Count: {len(report["weekly_trends"])}')
    if report["weekly_trends"]:
        print(f'First trend: {report["weekly_trends"][0]}')
    
    print('\n=== IMBALANCES ===')
    print(f'Count: {len(report["imbalances"])}')
    if report["imbalances"]:
        print(f'First imbalance: {report["imbalances"][0]}')
    
    print('\n=== FLAGS ===')
    print(f'Flag keys: {list(report["flags"].keys())}')
    
    print('\n✓ Full report working!')
else:
    print('No users found')
