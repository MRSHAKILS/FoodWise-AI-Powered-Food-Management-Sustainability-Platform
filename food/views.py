from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
import json
from .models import FoodItem, ConsumptionLog, FoodItemDatabase
from users.forms import FoodItemForm, ConsumptionLogForm
from .utils import calculate_dashboard_summary, generate_recommendations
from .risk_predictor import FoodRiskPredictor
from .waste_estimator import WasteEstimator


# Inventory Views
@login_required
def inventory_list(request):
    """List all inventory items with filters and risk predictions"""
    items = FoodItem.objects.filter(user=request.user)
    
    # Apply filters if provided
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    # Calculate total inventory value
    total_value = items.aggregate(total=Sum('price'))['total'] or 0
    
    # Calculate last week's expense (items purchased in last 7 days)
    last_week = timezone.now() - timedelta(days=7)
    last_week_items = FoodItem.objects.filter(
        user=request.user,
        purchase_date__gte=last_week.date()
    )
    last_week_expense = last_week_items.aggregate(total=Sum('price'))['total'] or 0
    last_week_count = last_week_items.count()
    
    # Get risk predictions for all items
    predictor = FoodRiskPredictor(request.user)
    risk_items = predictor.predict_risks_for_inventory()
    summary_stats = predictor.get_summary_stats(risk_items)
    
    # Get waste estimations
    waste_estimator = WasteEstimator(request.user)
    waste_projections = waste_estimator.predict_waste_projection(risk_items)
    
    # Create a risk data dictionary keyed by item ID for easy template lookup
    risk_data_by_id = {risk_item['item'].id: risk_item for risk_item in risk_items}
    
    context = {
        'items': items,
        'categories': FoodItem.CATEGORY_CHOICES,
        'risk_data_by_id': risk_data_by_id,
        'summary_stats': summary_stats,
        'total_value': total_value,
        'last_week_expense': last_week_expense,
        'last_week_count': last_week_count,
        'waste_projections': waste_projections,
    }
    return render(request, 'food/inventory_list.html', context)


@login_required
def inventory_form(request):
    """Add new inventory item"""
    if request.method == 'POST':
        form = FoodItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'{item.name} added to inventory!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FoodItemForm()
    
    # Get all food database items for quick selection
    food_database_items = FoodItemDatabase.objects.all().order_by('item_name')
    
    return render(request, 'food/inventory_form.html', {
        'form': form,
        'food_database_items': food_database_items
    })


@login_required
def inventory_edit(request, pk):
    """Edit existing inventory item"""
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = FoodItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'{item.name} updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FoodItemForm(instance=item)
    
    return render(request, 'food/inventory_form.html', {'form': form, 'item': item})


@login_required
def inventory_delete(request, pk):
    """Delete inventory item and create consumption log"""
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    
    # Create consumption log before deleting
    ConsumptionLog.objects.create(
        user=request.user,
        item_name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        category=item.category,
        consumption_date=timezone.now().date(),
        notes=f"Consumed from inventory (deleted item)"
    )
    
    item_name = item.name
    quantity = item.quantity
    unit = item.unit
    item.delete()
    
    messages.success(request, f'{item_name} ({quantity} {unit}) removed from inventory and logged as consumed.')
    return redirect('users:profile')


# Consumption Logs Views
@login_required
def consumption_logs_list(request):
    """List all consumption logs with real-time activity tracking"""
    from django.db.models import Count, Sum
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get all logs for the user
    logs = ConsumptionLog.objects.filter(user=request.user).order_by('-consumption_date', '-created_at')
    
    # Calculate stats
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    total_logs = logs.count()
    today_logs = logs.filter(consumption_date=today).count()
    week_logs = logs.filter(consumption_date__gte=week_ago).count()
    
    # Get most consumed category
    category_stats = logs.values('category').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    most_consumed = dict(ConsumptionLog.CATEGORY_CHOICES).get(
        category_stats['category'], 'None'
    ) if category_stats else 'None'
    
    # Get logs grouped by date
    logs_by_date = {}
    for log in logs[:50]:  # Limit to recent 50
        date_key = log.consumption_date.strftime('%Y-%m-%d')
        if date_key not in logs_by_date:
            logs_by_date[date_key] = []
        logs_by_date[date_key].append(log)
    
    # Apply filters if provided
    category = request.GET.get('category')
    if category:
        logs = logs.filter(category=category)
    
    context = {
        'logs': logs[:50],
        'logs_by_date': logs_by_date,
        'categories': ConsumptionLog.CATEGORY_CHOICES,
        'stats': {
            'total': total_logs,
            'today': today_logs,
            'week': week_logs,
            'most_consumed': most_consumed,
        }
    }
    return render(request, 'food/logs_list.html', context)


@login_required
def consumption_log_form(request):
    """Add new consumption log"""
    if request.method == 'POST':
        form = ConsumptionLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            messages.success(request, f'Consumption of {log.item_name} logged!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ConsumptionLogForm()
    
    return render(request, 'food/log_form.html', {'form': form})


@login_required
def consumption_log_delete(request, pk):
    """Delete consumption log"""
    log = get_object_or_404(ConsumptionLog, pk=pk, user=request.user)
    log_name = log.item_name
    log.delete()
    messages.success(request, f'Log for {log_name} deleted.')
    return redirect('food:logs_list')


@login_required
def consumption_history(request):
    """Display historical consumption data with statistics and filtering"""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get consumption logs
    consumption_logs = ConsumptionLog.objects.filter(user=request.user)
    
    # Get inventory items (for "added" history)
    inventory_items = FoodItem.objects.filter(user=request.user)
    
    # Apply filters
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if category:
        consumption_logs = consumption_logs.filter(category=category)
        inventory_items = inventory_items.filter(category=category)
    if start_date:
        consumption_logs = consumption_logs.filter(consumption_date__gte=start_date)
        inventory_items = inventory_items.filter(created_at__date__gte=start_date)
    if end_date:
        consumption_logs = consumption_logs.filter(consumption_date__lte=end_date)
        inventory_items = inventory_items.filter(created_at__date__lte=end_date)
    
    # Combine both into a unified history (limit to recent 50)
    combined_history = []
    
    # Add consumption logs
    for log in consumption_logs[:25]:
        combined_history.append({
            'type': 'consumed',
            'date': log.consumption_date,
            'item_name': log.item_name,
            'category': log.get_category_display(),
            'quantity': f"{log.quantity} {log.unit}",
            'notes': log.notes,
            'id': log.id,
            'created_at': log.created_at,
        })
    
    # Add inventory additions (recent items)
    for item in inventory_items[:25]:
        combined_history.append({
            'type': 'added',
            'date': item.created_at.date(),
            'item_name': item.name,
            'category': item.get_category_display(),
            'quantity': f"{item.quantity} {item.unit}",
            'notes': f"Added to inventory - Expires: {item.expiration_date}" if item.expiration_date else "Added to inventory",
            'id': item.id,
            'created_at': item.created_at,
        })
    
    # Sort by date (most recent first)
    combined_history.sort(key=lambda x: x['created_at'], reverse=True)
    combined_history = combined_history[:50]  # Limit to 50 items
    
    # Calculate statistics
    total_logs = consumption_logs.count()
    total_added = inventory_items.count()
    
    # This week logs
    week_ago = timezone.now().date() - timedelta(days=7)
    week_logs = consumption_logs.filter(consumption_date__gte=week_ago).count()
    week_added = inventory_items.filter(created_at__date__gte=week_ago).count()
    
    # This month logs
    month_ago = timezone.now().date() - timedelta(days=30)
    month_logs = consumption_logs.filter(consumption_date__gte=month_ago).count()
    month_added = inventory_items.filter(created_at__date__gte=month_ago).count()
    
    # Category breakdown (consumption only)
    category_stats = consumption_logs.values('category').annotate(count=Count('id')).order_by('-count')
    category_breakdown = []
    
    if total_logs > 0:
        for stat in category_stats:
            cat_display = dict(ConsumptionLog.CATEGORY_CHOICES).get(stat['category'], stat['category'])
            percentage = (stat['count'] / total_logs) * 100
            category_breakdown.append({
                'category__display': cat_display,
                'count': stat['count'],
                'percentage': percentage
            })
    
    # Top category
    top_category = category_breakdown[0]['category__display'] if category_breakdown else None
    
    context = {
        'logs': combined_history,
        'categories': ConsumptionLog.CATEGORY_CHOICES,
        'total_logs': total_logs + total_added,
        'week_logs': week_logs + week_added,
        'month_logs': month_logs + month_added,
        'top_category': top_category,
        'category_breakdown': category_breakdown,
        'total_consumed': total_logs,
        'total_added': total_added,
    }
    return render(request, 'food/history.html', context)


# Food Items Database Views (PART 4)
def food_items_list(request):
    """Browse common food items database with filters and search"""
    # Get all food items from database
    items = FoodItemDatabase.objects.all()
    
    # Apply category filter if provided
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    # Apply search filter if provided
    search = request.GET.get('search')
    if search:
        items = items.filter(item_name__icontains=search)
    
    # Order by item name (alphabetically)
    items = items.order_by('item_name')
    
    # Get list of unique categories for filter dropdown
    categories = FoodItemDatabase.CATEGORY_CHOICES
    
    context = {
        'items': items,
        'categories': categories,
        'selected_category': category,
        'search_query': search,
    }
    return render(request, 'food/food_items_list.html', context)


def food_item_detail(request, id):
    """Display detailed information about a single food item from database"""
    # Get single food item or return 404 if not found
    item = get_object_or_404(FoodItemDatabase, pk=id)
    
    context = {
        'item': item,
    }
    return render(request, 'food/food_item_detail.html', context)


# Food Database Views (PART 4 - Enhanced)
def food_database_list(request):
    """Browse food database with advanced filtering"""
    items = FoodItemDatabase.objects.all()
    
    # Category filter
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    # Unit filter
    unit = request.GET.get('unit')
    if unit:
        items = items.filter(unit=unit)
    
    # Search filter
    search = request.GET.get('search')
    if search:
        items = items.filter(
            Q(item_name__icontains=search) | 
            Q(storage_instructions__icontains=search)
        )
    
    # Sort option
    sort_by = request.GET.get('sort', 'item_name')
    if sort_by == 'expiration':
        items = items.order_by('typical_expiration_days')
    elif sort_by == 'price':
        items = items.order_by('sample_cost_per_unit')
    else:
        items = items.order_by('item_name')
    
    context = {
        'items': items,
        'categories': FoodItemDatabase.CATEGORY_CHOICES,
        'units': FoodItemDatabase.UNIT_CHOICES,
        'selected_category': category,
        'selected_unit': unit,
        'search_query': search,
        'sort_by': sort_by,
    }
    return render(request, 'food/food_database_list.html', context)


def food_database_detail(request, pk):
    """Show detailed view of a single food database item"""
    item = get_object_or_404(FoodItemDatabase, pk=pk)
    
    # Get related inventory items (items user added based on this database item)
    if request.user.is_authenticated:
        related_inventory = FoodItem.objects.filter(
            user=request.user,
            name__icontains=item.item_name
        )[:5]
    else:
        related_inventory = None
    
    context = {
        'item': item,
        'related_inventory': related_inventory,
    }
    return render(request, 'food/food_database_detail.html', context)


def food_database_search(request):
    """Advanced search interface for food database"""
    results = None
    total_items = FoodItemDatabase.objects.count()
    
    # Check if any search parameter is provided
    if any(request.GET.get(param) for param in ['q', 'category', 'max_price', 'min_shelf_life', 'unit', 'sort']):
        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        max_price = request.GET.get('max_price', '')
        min_shelf_life = request.GET.get('min_shelf_life', '')
        unit = request.GET.get('unit', '')
        sort_by = request.GET.get('sort', 'item_name')
        
        results = FoodItemDatabase.objects.all()
        
        # Text search
        if query:
            results = results.filter(
                Q(item_name__icontains=query) |
                Q(storage_instructions__icontains=query)
            )
        
        # Category filter
        if category:
            results = results.filter(category=category)
        
        # Price filter
        if max_price:
            try:
                results = results.filter(sample_cost_per_unit__lte=float(max_price))
            except ValueError:
                pass
        
        # Shelf life filter
        if min_shelf_life:
            try:
                results = results.filter(typical_expiration_days__gte=int(min_shelf_life))
            except ValueError:
                pass
        
        # Unit filter
        if unit:
            results = results.filter(unit=unit)
        
        # Sort results
        if sort_by in ['item_name', '-item_name', 'sample_cost_per_unit', '-sample_cost_per_unit', 
                       'typical_expiration_days', '-typical_expiration_days']:
            results = results.order_by(sort_by)
        else:
            results = results.order_by('item_name')
    
    context = {
        'results': results,
        'total_items': total_items,
        'query': request.GET.get('q', ''),
        'category': request.GET.get('category', ''),
        'max_price': request.GET.get('max_price', ''),
        'min_shelf_life': request.GET.get('min_shelf_life', ''),
        'unit': request.GET.get('unit', ''),
        'sort_by': request.GET.get('sort', 'item_name'),
    }
    return render(request, 'food/food_database_search.html', context)


# Dashboard and Recommendations API (PART 6)
@login_required
def dashboard_summary_api(request):
    """
    API endpoint for dashboard summary statistics.
    Returns JSON with inventory metrics, expiring items, and consumption stats.
    
    GET /api/dashboard/summary
    """
    summary = calculate_dashboard_summary(request.user)
    
    # Convert expiring_items to JSON-serializable format
    expiring_items_data = []
    for item_data in summary['expiring_items']:
        expiring_items_data.append({
            'id': item_data['item'].id,
            'name': item_data['item'].name,
            'quantity': float(item_data['item'].quantity),
            'unit': item_data['item'].unit,
            'category': item_data['item'].category,
            'expiration_date': item_data['item'].expiration_date.isoformat(),
            'days_left': item_data['days_left'],
            'urgency': item_data['urgency'],
        })
    
    response_data = {
        'total_inventory_items': summary['total_inventory_items'],
        'total_inventory_value': summary['total_inventory_value'],
        'recent_logs_count': summary['recent_logs_count'],
        'items_expiring_soon': summary['items_expiring_soon'],
        'expiring_items': expiring_items_data,
        'most_logged_category': summary['most_logged_category'],
        'category_breakdown': summary['category_breakdown'],
    }
    
    return JsonResponse(response_data, safe=False)


@login_required
def recommendations_api(request):
    """
    API endpoint for personalized resource recommendations.
    Returns JSON array of recommended resources with reasons and relevance scores.
    
    GET /api/recommendations
    """
    recommendations = generate_recommendations(request.user)
    
    # Convert recommendations to JSON-serializable format
    recommendations_data = []
    for rec in recommendations:
        recommendations_data.append({
            'resource': {
                'id': rec['resource'].id,
                'title': rec['resource'].title,
                'description': rec['resource'].description,
                'category': rec['resource'].category,
                'category_display': rec['resource'].get_category_display(),
                'type': rec['resource'].type,
                'type_display': rec['resource'].get_type_display(),
                'url': rec['resource'].url,
                'tags': rec['resource'].tags,
                'read_time': rec['resource'].read_time,
            },
            'reason': rec['reason'],
            'relevance_score': rec['relevance_score'],
            'matched_rule': rec['matched_rule'],
        })
    
    return JsonResponse(recommendations_data, safe=False)


@login_required
def enhanced_dashboard(request):
    """
    Enhanced dashboard view showing summary statistics and recommendations.
    Uses the PART_6 tracking logic functions.
    """
    # Get dashboard summary
    summary = calculate_dashboard_summary(request.user)
    
    # Get recommendations
    recommendations = generate_recommendations(request.user)
    
    context = {
        'summary': summary,
        'recommendations': recommendations,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def waste_analytics(request):
    """
    Comprehensive waste analytics dashboard
    Shows actual waste, projections, and community comparison
    """
    # Get risk predictions
    predictor = FoodRiskPredictor(request.user)
    risk_items = predictor.predict_risks_for_inventory()
    
    # Get waste estimations
    waste_estimator = WasteEstimator(request.user)
    waste_report = waste_estimator.generate_waste_report(risk_items)
    
    context = {
        'waste_report': waste_report,
        'page_title': 'Waste Analytics',
    }
    
    return render(request, 'food/waste_analytics.html', context)


@login_required
def priority_consumption(request):
    """
    AI Priority Consumption Guide
    Combines FIFO + AI risk scoring to prioritize what to eat first
    """
    # Get risk predictions
    predictor = FoodRiskPredictor(request.user)
    risk_items = predictor.predict_risks_for_inventory()
    
    # Calculate priority scores (FIFO + AI Risk + Expiry urgency)
    priority_items = []
    
    for risk_item in risk_items:
        item = risk_item['item']
        risk_score = risk_item['risk_score']
        days_until_expiry = risk_item.get('days_until_expiry')
        
        # Calculate FIFO score (older items = higher priority)
        days_since_purchase = (timezone.now().date() - item.purchase_date).days if item.purchase_date else 0
        fifo_score = min(days_since_purchase * 2, 40)  # Max 40 points
        
        # Calculate urgency multiplier based on expiry
        if days_until_expiry is not None:
            if days_until_expiry <= 0:
                urgency_multiplier = 1.5
            elif days_until_expiry <= 1:
                urgency_multiplier = 1.4
            elif days_until_expiry <= 2:
                urgency_multiplier = 1.3
            elif days_until_expiry <= 3:
                urgency_multiplier = 1.2
            elif days_until_expiry <= 7:
                urgency_multiplier = 1.1
            else:
                urgency_multiplier = 1.0
        else:
            urgency_multiplier = 1.0
        
        # Combined priority score: (FIFO + AI Risk) * Urgency
        priority_score = (fifo_score + risk_score) * urgency_multiplier
        priority_score = min(priority_score, 100)  # Cap at 100
        
        # Determine priority level
        if priority_score >= 80 or (days_until_expiry is not None and days_until_expiry <= 1):
            priority_level = 'critical'
        elif priority_score >= 60 or (days_until_expiry is not None and days_until_expiry <= 3):
            priority_level = 'high'
        elif priority_score >= 40 or (days_until_expiry is not None and days_until_expiry <= 7):
            priority_level = 'medium'
        else:
            priority_level = 'low'
        
        priority_items.append({
            'item': item,
            'risk_data': risk_item,
            'priority_score': priority_score,
            'priority_level': priority_level,
            'fifo_score': fifo_score,
            'urgency_multiplier': urgency_multiplier,
        })
    
    # Sort by priority score (highest first)
    priority_items.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Calculate statistics
    priority_stats = {
        'eat_today': len([x for x in priority_items if x['priority_level'] == 'critical']),
        'this_week': len([x for x in priority_items if x['priority_level'] == 'high']),
        'soon': len([x for x in priority_items if x['priority_level'] == 'medium']),
        'good': len([x for x in priority_items if x['priority_level'] == 'low']),
    }
    
    context = {
        'priority_items': priority_items,
        'priority_stats': priority_stats,
    }
    
    return render(request, 'food/priority_consumption.html', context)


@login_required
def mark_consumed(request, pk):
    """Quick mark item as consumed and delete from inventory"""
    if request.method == 'POST':
        item = get_object_or_404(FoodItem, pk=pk, user=request.user)
        
        # Create consumption log
        ConsumptionLog.objects.create(
            user=request.user,
            item_name=item.name,
            quantity=item.quantity,
            unit=item.unit,
            category=item.category,
            consumption_date=timezone.now().date(),
            notes=f"Consumed via priority guide"
        )
        
        item_name = item.name
        item.delete()
        
        messages.success(request, f'✅ {item_name} marked as consumed!')
        return redirect('food:priority_consumption')
    
    return redirect('food:priority_consumption')



@login_required
def export_waste_analytics(request, format='json'):
    """
    Export waste analytics data for RAG chatbot or external use
    Supports JSON and text formats
    """
    from django.http import HttpResponse
    import json
    from datetime import datetime
    
    # Get risk predictions
    predictor = FoodRiskPredictor(request.user)
    risk_items = predictor.predict_risks_for_inventory()
    
    # Get waste estimations
    waste_estimator = WasteEstimator(request.user)
    waste_report = waste_estimator.generate_waste_report(risk_items)
    
    # Prepare detailed inventory data
    inventory_details = []
    for risk_item in risk_items:
        item = risk_item['item']
        inventory_details.append({
            'name': item.name,
            'category': item.get_category_display(),
            'quantity': float(item.quantity),
            'unit': item.unit,
            'price': float(item.price) if item.price else 0,
            'purchase_date': item.purchase_date.isoformat() if item.purchase_date else None,
            'expiration_date': item.expiration_date.isoformat() if item.expiration_date else None,
            'days_until_expiry': risk_item.get('days_until_expiry'),
            'risk_score': risk_item['risk_score'],
            'risk_level': risk_item['risk_level'],
            'recommendation': risk_item['recommendation'],
        })
    
    # Prepare export data
    export_data = {
        'user': {
            'username': request.user.username,
            'export_date': datetime.now().isoformat(),
        },
        'summary': {
            'total_inventory_items': len(risk_items),
            'critical_risk_items': len([x for x in risk_items if x['risk_level'] == 'critical']),
            'high_risk_items': len([x for x in risk_items if x['risk_level'] == 'high']),
            'medium_risk_items': len([x for x in risk_items if x['risk_level'] == 'medium']),
            'low_risk_items': len([x for x in risk_items if x['risk_level'] == 'low']),
        },
        'actual_waste': {
            'last_7_days': {
                'total_grams': waste_report['actual_waste']['last_7_days']['total_grams'],
                'total_money': waste_report['actual_waste']['last_7_days']['total_money'],
                'by_category': waste_report['actual_waste']['last_7_days']['by_category'],
            },
            'last_30_days': {
                'total_grams': waste_report['actual_waste']['last_30_days']['total_grams'],
                'total_money': waste_report['actual_waste']['last_30_days']['total_money'],
                'by_category': waste_report['actual_waste']['last_30_days']['by_category'],
            }
        },
        'projections': {
            'weekly': {
                'grams': waste_report['projections']['weekly']['grams'],
                'money': waste_report['projections']['weekly']['money'],
                'by_category': waste_report['projections']['weekly']['by_category'],
            },
            'monthly': {
                'grams': waste_report['projections']['monthly']['grams'],
                'money': waste_report['projections']['monthly']['money'],
                'by_category': waste_report['projections']['monthly']['by_category'],
            }
        },
        'community_comparison': {
            'performance': waste_report['community_comparison']['performance'],
            'message': waste_report['community_comparison']['message'],
            'weekly': waste_report['community_comparison']['weekly'],
            'monthly': waste_report['community_comparison']['monthly'],
            'savings_potential': waste_report['community_comparison']['savings_potential'],
        },
        'insights': {
            'total_at_risk_items': waste_report['insights']['total_at_risk_items'],
            'potential_monthly_savings': waste_report['insights']['potential_monthly_savings'],
            'waste_trend': waste_report['insights']['waste_trend'],
        },
        'recommendations': waste_report['recommendations'],
        'inventory_details': inventory_details,
    }
    
    if format == 'json':
        response = HttpResponse(
            json.dumps(export_data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="waste_analytics_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response
    
    elif format == 'txt':
        # Create human-readable text format for RAG chatbot
        text_content = f"""
FOOD WASTE ANALYTICS REPORT
User: {request.user.username}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

========================================
SUMMARY STATISTICS
========================================
Total Inventory Items: {export_data['summary']['total_inventory_items']}
Critical Risk Items: {export_data['summary']['critical_risk_items']}
High Risk Items: {export_data['summary']['high_risk_items']}
Medium Risk Items: {export_data['summary']['medium_risk_items']}
Low Risk Items: {export_data['summary']['low_risk_items']}

========================================
ACTUAL WASTE (LAST 7 DAYS)
========================================
Total Money Lost: ${export_data['actual_waste']['last_7_days']['total_money']:.2f}
Total Grams Wasted: {export_data['actual_waste']['last_7_days']['total_grams']:.0f}g

========================================
ACTUAL WASTE (LAST 30 DAYS)
========================================
Total Money Lost: ${export_data['actual_waste']['last_30_days']['total_money']:.2f}
Total Grams Wasted: {export_data['actual_waste']['last_30_days']['total_grams']:.0f}g

========================================
WASTE PROJECTIONS - NEXT 7 DAYS
========================================
Projected Money Loss: ${export_data['projections']['weekly']['money']:.2f}
Projected Grams Waste: {export_data['projections']['weekly']['grams']:.0f}g

========================================
WASTE PROJECTIONS - NEXT 30 DAYS
========================================
Projected Money Loss: ${export_data['projections']['monthly']['money']:.2f}
Projected Grams Waste: {export_data['projections']['monthly']['grams']:.0f}g

========================================
COMMUNITY COMPARISON
========================================
Performance Level: {export_data['community_comparison']['performance'].upper()}
Status: {export_data['community_comparison']['message']}

Weekly:
  Your Projection: ${export_data['community_comparison']['weekly']['user']:.2f}
  Community Average: ${export_data['community_comparison']['weekly']['community']:.2f}
  Difference: {export_data['community_comparison']['weekly']['difference_percent']:.1f}%

Monthly:
  Your Projection: ${export_data['community_comparison']['monthly']['user']:.2f}
  Community Average: ${export_data['community_comparison']['monthly']['community']:.2f}
  Difference: {export_data['community_comparison']['monthly']['difference_percent']:.1f}%

Annual Savings Potential: ${export_data['community_comparison']['savings_potential']:.2f}

========================================
INSIGHTS
========================================
Items at Risk (High/Critical): {export_data['insights']['total_at_risk_items']}
Potential Monthly Savings: ${export_data['insights']['potential_monthly_savings']:.2f}
Waste Trend: {export_data['insights']['waste_trend'].upper()}

========================================
AI RECOMMENDATIONS
========================================
"""
        for i, rec in enumerate(export_data['recommendations'], 1):
            text_content += f"{i}. [{rec['priority'].upper()}] {rec['action']}\n"
            text_content += f"   Impact: {rec['impact']}\n\n"
        
        text_content += """
========================================
DETAILED INVENTORY ANALYSIS
========================================
"""
        for item in export_data['inventory_details']:
            text_content += f"\nItem: {item['name']}\n"
            text_content += f"  Category: {item['category']}\n"
            text_content += f"  Quantity: {item['quantity']} {item['unit']}\n"
            text_content += f"  Price: ${item['price']:.2f}\n"
            if item['expiration_date']:
                text_content += f"  Expiration: {item['expiration_date']}\n"
                text_content += f"  Days Until Expiry: {item['days_until_expiry']}\n"
            text_content += f"  Risk Score: {item['risk_score']:.1f}%\n"
            text_content += f"  Risk Level: {item['risk_level'].upper()}\n"
            text_content += f"  Recommendation: {item['recommendation']}\n"
        
        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="waste_analytics_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt"'
        return response
    
    else:
        return JsonResponse({'error': 'Invalid format. Use json or txt'}, status=400)


@login_required
def priority_alerts_api(request):
    """API endpoint to fetch high-priority items for navbar notifications"""
    items = FoodItem.objects.filter(user=request.user)
    
    if not items:
        return JsonResponse({'alerts': []})
    
    # Initialize predictor
    predictor = FoodRiskPredictor()
    
    # Calculate priority scores for all items
    alerts = []
    for item in items:
        today = timezone.now().date()
        
        # Calculate FIFO score (days since purchase)
        days_since_purchase = (today - item.purchase_date).days
        fifo_score = min(days_since_purchase * 2, 40)  # Cap at 40
        
        # Get AI risk score
        ai_risk = predictor.predict_risk(item)
        
        # Calculate urgency multiplier
        if item.expiration_date:
            days_until_expiry = (item.expiration_date - today).days
            if days_until_expiry <= 1:
                urgency_multiplier = 1.5
            elif days_until_expiry <= 3:
                urgency_multiplier = 1.3
            elif days_until_expiry <= 7:
                urgency_multiplier = 1.1
            else:
                urgency_multiplier = 1.0
        else:
            days_until_expiry = 999
            urgency_multiplier = 1.0
        
        # Calculate final priority score
        priority_score = (fifo_score + ai_risk) * urgency_multiplier
        priority_score = min(priority_score, 100)  # Cap at 100
        
        # Determine priority level
        if priority_score >= 80:
            priority_level = 'critical'
        elif priority_score >= 60:
            priority_level = 'high'
        elif priority_score >= 40:
            priority_level = 'medium'
        else:
            priority_level = 'low'
        
        # Only include critical and high priority items in alerts
        if priority_level in ['critical', 'high']:
            message = f"Expires in {days_until_expiry} day{'s' if days_until_expiry != 1 else ''}. "
            if priority_level == 'critical':
                message += "⚠️ Consume immediately!"
            else:
                message += "Consume soon to avoid waste."
            
            alerts.append({
                'id': item.id,
                'name': item.name,
                'priority_score': priority_score,
                'priority_level': priority_level,
                'days_until_expiry': days_until_expiry,
                'message': message,
                'category': item.category,
                'quantity': f"{item.quantity} {item.unit}"
            })
    
    # Sort by priority score (highest first)
    alerts = sorted(alerts, key=lambda x: x['priority_score'], reverse=True)
    
    # Limit to top 10 alerts
    alerts = alerts[:10]
    
    return JsonResponse({
        'alerts': alerts,
        'count': len(alerts)
    })


# =====================================================
# MEAL PLANNING VIEWS (AI Meal Optimization Engine)
# =====================================================

@login_required
def meal_plan_create(request):
    """
    Create a new AI-optimized meal plan
    GET: Show form to input budget and preferences
    POST: Generate optimized meal plan
    """
    from .meal_optimizer import MealOptimizer
    from .models import MealPlan, Recipe
    from datetime import datetime
    
    if request.method == 'POST':
        # Get form data
        budget = float(request.POST.get('budget', 5000))
        week_start_str = request.POST.get('week_start', '')
        notes = request.POST.get('notes', '')
        
        # Parse week start date
        if week_start_str:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        else:
            week_start = None
        
        # Create optimizer and generate plan
        optimizer = MealOptimizer(request.user, budget, week_start)
        result = optimizer.generate_meal_plan()
        
        # Save meal plan to database
        meal_plan = MealPlan.objects.create(
            user=request.user,
            week_start=result['week_start'],
            week_end=result['week_end'],
            budget_limit=result['budget_limit'],
            actual_cost=result['total_cost'],
            meals=result['meal_plan'],
            shopping_list=result['shopping_list'],
            nutrition_summary=result['nutrition_summary'],
            inventory_used=result['inventory_used'],
            notes=notes
        )
        
        messages.success(
            request, 
            f'✅ Meal plan created! {len(result["shopping_list"])} items to shop. Cost: ৳{result["total_cost"]:.2f}'
        )
        
        return redirect('food:meal_plan_detail', pk=meal_plan.pk)
    
    # GET request - show form
    budget_limit = request.user.budget_limit if request.user.budget_limit else 5000
    context = {
        'user_budget': f'{budget_limit:.0f}',
        'household_size': request.user.household_size,
        'dietary_preference': request.user.dietary_preferences if request.user.dietary_preferences else 'any',
    }
    
    return render(request, 'food/meal_plan_create.html', context)


@login_required
def meal_plan_list(request):
    """List all meal plans for the user"""
    from .models import MealPlan
    
    meal_plans = MealPlan.objects.filter(user=request.user)
    
    context = {
        'meal_plans': meal_plans,
    }
    
    return render(request, 'food/meal_plan_list.html', context)


@login_required
def meal_plan_detail(request, pk):
    """View detailed meal plan with weekly calendar and shopping list"""
    from .models import MealPlan, Recipe
    
    meal_plan = get_object_or_404(MealPlan, pk=pk, user=request.user)
    
    # Get recipe details for each meal
    weekly_meals = {}
    for day, meals_data in meal_plan.meals.items():
        weekly_meals[day] = {
            'date': meals_data.get('date'),
            'breakfast': None,
            'lunch': None,
            'dinner': None
        }
        
        for meal_type in ['breakfast', 'lunch', 'dinner']:
            recipe_id = meals_data.get(meal_type)
            if recipe_id:
                try:
                    recipe = Recipe.objects.get(id=recipe_id)
                    weekly_meals[day][meal_type] = {
                        'id': recipe.id,
                        'name': recipe.name,
                        'cost': recipe.estimated_cost,
                        'nutrition': recipe.nutrition,
                        'prep_time': recipe.prep_time,
                        'tags': recipe.tags
                    }
                except Recipe.DoesNotExist:
                    pass
    
    # Group shopping list by category
    shopping_by_category = {}
    for item in meal_plan.shopping_list:
        category = item.get('category', 'other')
        if category not in shopping_by_category:
            shopping_by_category[category] = []
        shopping_by_category[category].append(item)
    
    context = {
        'meal_plan': meal_plan,
        'weekly_meals': weekly_meals,
        'shopping_by_category': shopping_by_category,
        'days_of_week': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
    }
    
    return render(request, 'food/meal_plan_detail.html', context)


@login_required
def meal_plan_delete(request, pk):
    """Delete a meal plan"""
    from .models import MealPlan
    
    meal_plan = get_object_or_404(MealPlan, pk=pk, user=request.user)
    
    if request.method == 'POST':
        meal_plan.delete()
        messages.success(request, '🗑️ Meal plan deleted successfully')
        return redirect('food:meal_plan_list')
    
    return redirect('food:meal_plan_detail', pk=pk)


@login_required
def recipe_list(request):
    """Browse all available recipes"""
    from .models import Recipe
    
    # Get filter parameters
    meal_type = request.GET.get('meal_type', '')
    max_cost = request.GET.get('max_cost', '')
    max_prep_time = request.GET.get('max_prep_time', '')
    tags = request.GET.get('tags', '')
    search = request.GET.get('search', '')
    
    # Start with all recipes
    recipes = Recipe.objects.all()
    
    # Apply filters
    if meal_type:
        recipes = recipes.filter(meal_type=meal_type)
    
    if max_cost:
        recipes = recipes.filter(estimated_cost__lte=float(max_cost))
    
    if max_prep_time:
        recipes = recipes.filter(prep_time__lte=int(max_prep_time))
    
    if tags:
        recipes = recipes.filter(tags__contains=[tags])
    
    if search:
        recipes = recipes.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Count by meal type for filter display
    meal_type_counts = {
        'breakfast': Recipe.objects.filter(meal_type='breakfast').count(),
        'lunch': Recipe.objects.filter(meal_type='lunch').count(),
        'dinner': Recipe.objects.filter(meal_type='dinner').count(),
        'snack': Recipe.objects.filter(meal_type='snack').count(),
    }
    
    context = {
        'recipes': recipes,
        'meal_type_counts': meal_type_counts,
        'selected_meal_type': meal_type,
        'search_query': search,
    }
    
    return render(request, 'food/recipe_list.html', context)


@login_required
def recipe_detail(request, pk):
    """View detailed recipe information"""
    from .models import Recipe
    
    recipe = get_object_or_404(Recipe, pk=pk)
    
    context = {
        'recipe': recipe,
    }
    
    return render(request, 'food/recipe_detail.html', context)


# SDG Impact Scoring Views
@login_required
def sdg_impact_dashboard(request):
    """Display SDG Impact Score and insights"""
    from .sdg_impact_scoring import SDGImpactScorer
    
    scorer = SDGImpactScorer(request.user)
    
    # Calculate score and get insights
    sdg_score = scorer.calculate_sdg_score()
    insights = scorer.get_weekly_insights()
    recommendations = scorer.generate_ai_recommendations()
    badges = scorer.get_sdg_achievement_badges()
    
    context = {
        'sdg_score': sdg_score,
        'insights': insights,
        'recommendations': recommendations,
        'badges': badges,
        'score_breakdown': insights['breakdown']
    }
    
    return render(request, 'food/sdg_dashboard.html', context)


@login_required
def sdg_score_api(request):
    """API endpoint for SDG score (for AJAX)"""
    from .sdg_impact_scoring import SDGImpactScorer
    from django.http import JsonResponse
    
    scorer = SDGImpactScorer(request.user)
    sdg_score = scorer.calculate_sdg_score()
    insights = scorer.get_weekly_insights()
    
    return JsonResponse({
        'score': sdg_score,
        'breakdown': insights['breakdown'],
        'improvement': insights['improvement'],
        'trend': insights['trend']
    })
