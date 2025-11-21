from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import FoodItem, ConsumptionLog, FoodItemDatabase
from users.forms import FoodItemForm, ConsumptionLogForm
from .utils import calculate_dashboard_summary, generate_recommendations
from .risk_predictor import FoodRiskPredictor


# Inventory Views
@login_required
def inventory_list(request):
    """List all inventory items with filters and risk predictions"""
    items = FoodItem.objects.filter(user=request.user)
    
    # Apply filters if provided
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    # Get risk predictions for all items
    predictor = FoodRiskPredictor(request.user)
    risk_items = predictor.predict_risks_for_inventory()
    summary_stats = predictor.get_summary_stats(risk_items)
    
    # Create a risk data dictionary keyed by item ID for easy template lookup
    risk_data_by_id = {risk_item['item'].id: risk_item for risk_item in risk_items}
    
    context = {
        'items': items,
        'categories': FoodItem.CATEGORY_CHOICES,
        'risk_data_by_id': risk_data_by_id,
        'summary_stats': summary_stats,
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
    """List all consumption logs"""
    logs = ConsumptionLog.objects.filter(user=request.user)
    
    # Apply filters if provided
    category = request.GET.get('category')
    if category:
        logs = logs.filter(category=category)
    
    context = {
        'logs': logs,
        'categories': ConsumptionLog.CATEGORY_CHOICES,
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
    return redirect('users:profile')


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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .services import ConsumptionAnalyzer

# ... existing imports ...

@login_required
def consumption_analysis_dashboard(request):
    """
    MVT View for the AI Analysis Dashboard.
    """
    analyzer = ConsumptionAnalyzer(request.user)
    
    # Call the REAL AI Service
    # NOTE: This might take 1-3 seconds. In production, use Celery/background tasks.
    ai_results = analyzer.get_ai_insights()
    
    # Fallback: If API failed, ensure we still have heatmap data to show the chart
    if 'raw_heatmap' not in ai_results:
        ai_results['raw_heatmap'] = analyzer._get_weekly_heatmap_data()

    context = {
        'trends': ai_results.get('trends', []),
        'imbalances': ai_results.get('imbalances', []),
        'waste_predictions': ai_results.get('waste_predictions', []),
        'heatmap_data': ai_results.get('raw_heatmap', {}),
        'has_api_key': hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY
    }
    
    return render(request, 'food/analysis_dashboard.html', context)