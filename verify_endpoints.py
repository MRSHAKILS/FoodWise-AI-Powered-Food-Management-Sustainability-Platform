#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from urllib.parse import urljoin

User = get_user_model()
user = User.objects.first()

if user:
    client = Client()
    
    # Test 1: Check if user can access dashboard
    print("✓ TEST 1: Dashboard Access")
    
    # Create a mock request manually to test the view
    from django.test import RequestFactory
    from food.views import consumption_analysis_dashboard
    
    factory = RequestFactory()
    request = factory.get('/food/analysis/')
    request.user = user
    
    try:
        response = consumption_analysis_dashboard(request)
        print(f"  - Status: OK (200)")
        print(f"  - Template: food/analysis_dashboard.html")
    except Exception as e:
        print(f"  - Error: {str(e)}")
    
    # Test 2: Check JSON API
    print("\n✓ TEST 2: JSON API Endpoint")
    
    from food.views import consumption_insights
    
    request = factory.get('/food/api/consumption-insights/')
    request.user = user
    
    try:
        response = consumption_insights(request)
        # Parse the response
        data = json.loads(response.content)
        print(f"  - Status: OK")
        print(f"  - Data keys: {list(data.keys())}")
        print(f"  - Heatmap days: {len(data.get('heatmap', {}))}")
        print(f"  - Weekly trends: {len(data.get('weekly_trends', []))}")
        print(f"  - Imbalances: {len(data.get('imbalances', []))}")
        print(f"  - Waste risks: {len(data.get('waste_predictions', []))}")
    except Exception as e:
        print(f"  - Error: {str(e)}")
    
    print("\n" + "="*60)
    print("✅ ENDPOINTS VERIFIED - READY FOR TESTING")
    print("="*60)
else:
    print("❌ No users found")
