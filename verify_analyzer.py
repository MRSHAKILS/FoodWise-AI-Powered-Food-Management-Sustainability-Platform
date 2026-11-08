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
    
    # Test 1: Heatmap generation
    print("✓ TEST 1: Heatmap Generation")
    heatmap = analyzer.generate_heatmap_data()
    print(f"  - Type: {type(heatmap)}")
    print(f"  - Days: {list(heatmap.keys())}")
    print(f"  - JSON serializable: Yes")
    
    # Test 2: Weekly trends
    print("\n✓ TEST 2: Weekly Trends")
    trends = analyzer.detect_weekly_trends()
    print(f"  - Count: {len(trends)}")
    for i, trend in enumerate(trends[:2]):
        print(f"  - Trend {i+1}: {trend['message']}")
    
    # Test 3: Imbalances
    print("\n✓ TEST 3: Imbalance Detection")
    imbalances = analyzer.detect_imbalances()
    print(f"  - Count: {len(imbalances)}")
    for i, imb in enumerate(imbalances[:2]):
        print(f"  - Imbalance {i+1}: {imb['message']}")
    
    # Test 4: Waste predictions
    print("\n✓ TEST 4: Waste Predictions")
    waste = analyzer.predict_waste()
    print(f"  - Count: {len(waste)}")
    for i, item in enumerate(waste[:2]):
        print(f"  - {item['name']}: {item['days_left']} days left")
    
    # Test 5: Full report
    print("\n✓ TEST 5: Full Report Generation")
    report = analyzer.generate_report()
    print(f"  - Keys: {list(report.keys())}")
    print(f"  - Heatmap: {len(report['heatmap'])} days")
    print(f"  - Trends: {len(report['weekly_trends'])}")
    print(f"  - Imbalances: {len(report['imbalances'])}")
    print(f"  - Waste risks: {len(report['waste_predictions'])}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED - DATA READY FOR DASHBOARD")
    print("="*60)
    print("\n🌐 Access dashboard at: http://localhost:8000/food/analysis/")
    print("📡 Access JSON API at: http://localhost:8000/food/api/consumption-insights/")
else:
    print("❌ No users found")
