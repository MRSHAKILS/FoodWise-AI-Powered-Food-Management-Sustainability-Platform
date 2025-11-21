#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from food.views import consumption_analysis_dashboard
from food.services import ConsumptionAnalyzer

User = get_user_model()
user = User.objects.first()

if user:
    print(f"Testing with user: {user.username}\n")
    
    # Create a fake request
    factory = RequestFactory()
    request = factory.get('/food/analysis/')
    request.user = user
    
    # Call analyzer directly
    analyzer = ConsumptionAnalyzer(user)
    ai_results = analyzer.get_ai_insights()
    
    print("=== AI RESULTS FROM get_ai_insights() ===")
    print(f"Keys: {list(ai_results.keys())}")
    
    # Check heatmap fallback
    if 'raw_heatmap' not in ai_results:
        print("⚠️  No raw_heatmap in AI results, using fallback...")
        ai_results['raw_heatmap'] = analyzer._get_weekly_heatmap_data()
        print(f"Fallback heatmap keys: {list(ai_results['raw_heatmap'].keys())}")
    
    print(f"\n=== HEATMAP DATA (first 2 days) ===")
    heatmap = ai_results.get('raw_heatmap', {})
    for day in list(heatmap.keys())[:2]:
        print(f"{day}: {heatmap[day]}")
    
    print(f"\n=== TEMPLATE CONTEXT ===")
    context = {
        'trends': ai_results.get('trends', []),
        'imbalances': ai_results.get('imbalances', []),
        'waste_predictions': ai_results.get('waste_predictions', []),
        'heatmap_data': ai_results.get('raw_heatmap', {}),
        'has_api_key': False
    }
    
    print(f"Trends count: {len(context['trends'])}")
    print(f"Imbalances count: {len(context['imbalances'])}")
    print(f"Waste predictions count: {len(context['waste_predictions'])}")
    print(f"Heatmap keys: {list(context['heatmap_data'].keys())}")
    
    # Show JSON serialization
    print(f"\n=== HEATMAP JSON (for template) ===")
    heatmap_json = json.dumps(context['heatmap_data'])
    print(f"JSON length: {len(heatmap_json)} chars")
    print(f"First 200 chars: {heatmap_json[:200]}")
    
    print("\n✓ Context ready for template!")
else:
    print("No users found")
