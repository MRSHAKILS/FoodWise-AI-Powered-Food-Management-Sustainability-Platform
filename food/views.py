from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
import json

from .models import FoodItem, ConsumptionLog, FoodItemDatabase, MealPlan, SDGScore, WasteLog, ChatSession, FoodSurplus
from users.forms import FoodItemForm, ConsumptionLogForm
from .utils import calculate_dashboard_summary, generate_recommendations
from .risk_predictor import FoodRiskPredictor
from .ai_services import (
    analyze_consumption_patterns,
    generate_meal_plan,
    chat_with_nourish_bot,
    calculate_sdg_score,
    rule_based_consumption_analysis
)


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
    total_value = sum(item.quantity * (item.price or 0) for item in items)
    
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
        'total_value': total_value,
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
            return redirect('food:inventory_list')
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


# ==================== AI-POWERED FEATURES (Part 2) ====================

@login_required
@require_http_methods(["POST"])
def analyze_consumption_api(request):
    """
    API: Analyze consumption patterns using AI
    POST /api/analyze/consumption
    
    Returns trends, flags, waste predictions, and insights
    """
    try:
        # Get last 30 days of consumption data
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        consumption_logs = ConsumptionLog.objects.filter(
            user=request.user,
            consumption_date__gte=thirty_days_ago
        ).values('item_name', 'quantity', 'unit', 'category', 'consumption_date')
        
        consumption_data = list(consumption_logs)
        
        # Convert dates to strings for JSON serialization
        for log in consumption_data:
            log['consumption_date'] = log['consumption_date'].isoformat()
        
        if not consumption_data:
            return JsonResponse({
                'success': False,
                'error': 'No consumption data found for the last 30 days'
            }, status=404)
        
        # Analyze using AI
        analysis_result = analyze_consumption_patterns(consumption_data)
        
        # Fallback to rule-based if AI fails
        if not analysis_result:
            analysis_result = rule_based_consumption_analysis(consumption_data)
        
        return JsonResponse({
            'success': True,
            'data': analysis_result,
            'period': {
                'start': thirty_days_ago.isoformat(),
                'end': timezone.now().date().isoformat(),
                'total_logs': len(consumption_data)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def generate_meal_plan_api(request):
    """
    API: Generate AI-optimized meal plan
    POST /api/optimize/meal-plan
    
    Body: {
        "budget": float,
        "days": int (optional, default 7),
        "dietary_preferences": {}
    }
    """
    try:
        data = json.loads(request.body)
        budget = float(data.get('budget', request.user.budget_limit or 100))
        days = int(data.get('days', 7))
        dietary_needs = data.get('dietary_preferences', {})
        
        # Get current inventory
        inventory = FoodItem.objects.filter(user=request.user).values(
            'id', 'name', 'quantity', 'unit', 'expiration_date', 'category', 'price'
        )
        
        inventory_data = []
        for item in inventory:
            inventory_data.append({
                'id': item['id'],
                'name': item['name'],
                'quantity': float(item['quantity']),
                'unit': item['unit'],
                'expiration_date': item['expiration_date'].isoformat() if item['expiration_date'] else None,
                'category': item['category'],
                'price': float(item['price']) if item['price'] else 0
            })
        
        # Generate meal plan using AI
        meal_plan_result = generate_meal_plan(budget, inventory_data, dietary_needs, days)
        
        if not meal_plan_result:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate meal plan. Please try again.'
            }, status=500)
        
        # Save meal plan to database
        from datetime import date
        meal_plan = MealPlan.objects.create(
            user=request.user,
            week_start_date=date.today(),
            meals_data=meal_plan_result.get('mealPlan', []),
            shopping_list=meal_plan_result.get('shoppingList', []),
            total_cost=meal_plan_result.get('totalCost', 0),
            budget_limit=budget,
            nutrition_score=meal_plan_result.get('nutritionScore', 0),
            waste_reduction_estimate=meal_plan_result.get('wasteReduction', ''),
            generated_by='AI'
        )
        
        return JsonResponse({
            'success': True,
            'data': meal_plan_result,
            'meal_plan_id': meal_plan.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def nourish_bot_chat_api(request):
    """
    API: Chat with NourishBot
    POST /api/chat/nourish-bot
    
    Body: {
        "message": str,
        "session_id": str (optional)
    }
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            }, status=400)
        
        # Get or create chat session
        if session_id:
            chat_session = ChatSession.objects.filter(
                user=request.user,
                session_id=session_id,
                is_active=True
            ).first()
        else:
            # Create new session
            import uuid
            session_id = str(uuid.uuid4())
            chat_session = ChatSession.objects.create(
                user=request.user,
                session_id=session_id
            )
        
        # Prepare user context with detailed data
        inventory = FoodItem.objects.filter(user=request.user).order_by('expiration_date')[:20]
        recent_consumption = ConsumptionLog.objects.filter(user=request.user).order_by('-consumption_date')[:15]
        
        user_context = {
            'inventory': [
                {
                    'name': item.name, 
                    'quantity': float(item.quantity), 
                    'expiring_days': item.days_until_expiration,
                    'category': item.category
                }
                for item in inventory
            ],
            'recent_consumption': [
                {
                    'name': log.item_name, 
                    'quantity': float(log.quantity), 
                    'date': log.consumption_date.isoformat(),
                    'category': log.category
                }
                for log in recent_consumption
            ],
            'budget': float(request.user.budget_limit) if request.user.budget_limit else None
        }
        
        # Get chat history from session
        chat_history = None
        if chat_session and hasattr(chat_session, 'messages'):
            try:
                chat_history = json.loads(chat_session.messages) if chat_session.messages else []
            except:
                chat_history = []
        
        # Get AI response
        bot_response = chat_with_nourish_bot(user_message, user_context, chat_history)
        
        if not bot_response:
            bot_response = "I'm sorry, I'm having trouble connecting right now. Please try again in a moment."
        
        # Save messages to session
        chat_session.add_message('user', user_message)
        chat_session.add_message('assistant', bot_response)
        
        return JsonResponse({
            'success': True,
            'response': bot_response,
            'session_id': session_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def waste_estimation_api(request):
    """
    API: Get waste estimation and projections
    GET /api/estimate/waste
    """
    try:
        # Get waste logs
        waste_logs = WasteLog.objects.filter(user=request.user)
        
        # Current week
        week_start = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
        week_waste = waste_logs.filter(waste_date__gte=week_start)
        
        # Current month
        month_start = timezone.now().date().replace(day=1)
        month_waste = waste_logs.filter(waste_date__gte=month_start)
        
        # Calculate metrics
        week_total_kg = sum(float(log.quantity) for log in week_waste)
        week_total_cost = sum(float(log.estimated_cost or 0) for log in week_waste)
        
        month_total_kg = sum(float(log.quantity) for log in month_waste)
        month_total_cost = sum(float(log.estimated_cost or 0) for log in month_waste)
        
        # Average community baseline (dummy data)
        community_avg_waste_percent = 30
        
        # Calculate user's waste percentage
        total_inventory_value = sum(
            float(item.price or 0) * float(item.quantity)
            for item in FoodItem.objects.filter(user=request.user)
        )
        
        if total_inventory_value > 0:
            user_waste_percent = (month_total_cost / total_inventory_value) * 100
        else:
            user_waste_percent = 0
        
        # Projection (simple linear projection)
        avg_weekly_waste = month_total_kg / 4 if month_total_kg > 0 else 0
        next_month_projection = avg_weekly_waste * 4
        
        return JsonResponse({
            'success': True,
            'data': {
                'currentWeek': {
                    'totalWasteKg': round(week_total_kg, 2),
                    'totalWasteCost': round(week_total_cost, 2),
                    'itemsWasted': week_waste.count()
                },
                'currentMonth': {
                    'totalWasteKg': round(month_total_kg, 2),
                    'totalWasteCost': round(month_total_cost, 2),
                    'itemsWasted': month_waste.count(),
                    'wastePercentage': round(user_waste_percent, 2)
                },
                'projection': {
                    'nextMonthKg': round(next_month_projection, 2),
                    'trend': 'stable'
                },
                'comparison': {
                    'communityAverage': community_avg_waste_percent,
                    'yourPerformance': round(community_avg_waste_percent - user_waste_percent, 2),
                    'message': f"You're wasting {abs(community_avg_waste_percent - user_waste_percent):.1f}% {'less' if user_waste_percent < community_avg_waste_percent else 'more'} than average"
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def sdg_score_api(request):
    """
    API: Get user's SDG impact score
    GET /api/score/sdg
    """
    try:
        # Get or calculate current week's score
        current_date = timezone.now().date()
        week_number = current_date.isocalendar()[1]
        year = current_date.year
        
        # Check if score already calculated this week
        existing_score = SDGScore.objects.filter(
            user=request.user,
            year=year,
            week_number=week_number
        ).first()
        
        if existing_score:
            score_data = {
                'totalScore': existing_score.score,
                'breakdown': {
                    'wasteReduction': float(existing_score.waste_reduction_score),
                    'nutritionBalance': float(existing_score.nutrition_score),
                    'budgetEfficiency': float(existing_score.budget_efficiency_score),
                    'communityEngagement': float(existing_score.community_engagement_score)
                },
                'insights': existing_score.insights,
                'recommendations': existing_score.recommendations
            }
        else:
            # Calculate new score
            # Get waste data
            week_start = current_date - timedelta(days=current_date.weekday())
            waste_logs = WasteLog.objects.filter(
                user=request.user,
                waste_date__gte=week_start
            )
            
            waste_data = {
                'total_waste_kg': sum(float(log.quantity) for log in waste_logs),
                'total_cost': sum(float(log.estimated_cost or 0) for log in waste_logs)
            }
            
            # Get nutrition data (simplified)
            consumption_logs = ConsumptionLog.objects.filter(
                user=request.user,
                consumption_date__gte=week_start
            )
            
            category_counts = {}
            for log in consumption_logs:
                category_counts[log.category] = category_counts.get(log.category, 0) + 1
            
            nutrition_data = {
                'category_diversity': len(category_counts),
                'total_items': consumption_logs.count()
            }
            
            # Get budget data
            budget_data = {
                'budget_limit': float(request.user.budget_limit) if request.user.budget_limit else 100,
                'actual_spend': sum(float(item.price or 0) for item in FoodItem.objects.filter(user=request.user))
            }
            
            # Calculate using AI
            score_result = calculate_sdg_score(waste_data, nutrition_data, budget_data)
            
            if score_result:
                # Save to database
                sdg_score = SDGScore.objects.create(
                    user=request.user,
                    score=score_result['totalScore'],
                    waste_reduction_score=score_result['breakdown']['wasteReduction'],
                    nutrition_score=score_result['breakdown']['nutritionBalance'],
                    budget_efficiency_score=score_result['breakdown']['budgetEfficiency'],
                    community_engagement_score=score_result['breakdown']['communityEngagement'],
                    waste_reduced_kg=waste_data['total_waste_kg'],
                    waste_cost_saved=waste_data['total_cost'],
                    nutrition_balance=nutrition_data,
                    budget_data=budget_data,
                    insights=score_result.get('insights', ''),
                    recommendations=score_result.get('recommendations', []),
                    week_number=week_number,
                    year=year
                )
                
                score_data = score_result
            else:
                # Fallback calculation
                score_data = {
                    'totalScore': 50,
                    'breakdown': {
                        'wasteReduction': 50,
                        'nutritionBalance': 50,
                        'budgetEfficiency': 50,
                        'communityEngagement': 50
                    },
                    'insights': 'Score calculated using basic metrics. Enable AI for detailed insights.',
                    'recommendations': ['Track your food consumption regularly', 'Plan meals to reduce waste']
                }
        
        return JsonResponse({
            'success': True,
            'data': score_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ==================== FRONTEND VIEWS FOR AI FEATURES ====================

@login_required
def consumption_analysis_view(request):
    """Frontend view for consumption pattern analysis"""
    return render(request, 'food/ai/consumption_analysis.html')


@login_required
def meal_planner_view(request):
    """Frontend view for AI meal planner"""
    # Get user's current inventory for display
    inventory = FoodItem.objects.filter(user=request.user)
    context = {
        'inventory': inventory,
        'user_budget': request.user.budget_limit or 100
    }
    return render(request, 'food/ai/meal_planner.html', context)


@login_required
def nourish_bot_view(request):
    """Frontend view for NourishBot chatbot"""
    return render(request, 'food/ai/nourish_bot.html')


@login_required
def sdg_score_view(request):
    """Frontend view for SDG impact score dashboard"""
    # Get historical scores
    scores = SDGScore.objects.filter(user=request.user).order_by('-calculated_date')[:10]
    context = {
        'historical_scores': scores
    }
    return render(request, 'food/ai/sdg_score.html', context)


@login_required
def waste_estimation_view(request):
    """Frontend view for waste estimation and analytics"""
    # Get recent waste logs
    waste_logs = WasteLog.objects.filter(user=request.user).order_by('-waste_date')[:20]
    context = {
        'recent_waste_logs': waste_logs
    }
    return render(request, 'food/ai/waste_estimation.html', context)


@login_required
def expiration_risks_view(request):
    """Frontend view for expiration risk prediction"""
    # Get risk predictions using existing predictor
    predictor = FoodRiskPredictor(request.user)
    risk_items = predictor.predict_risks_for_inventory()
    summary_stats = predictor.get_summary_stats(risk_items)
    
    context = {
        'risk_items': risk_items,
        'summary_stats': summary_stats
    }
    return render(request, 'food/ai/expiration_risks.html', context)


# ==================== WASTE LOG MANAGEMENT ====================

@login_required
def waste_logs_list(request):
    """List all waste logs with filtering"""
    logs = WasteLog.objects.filter(user=request.user)
    
    # Apply filters if provided
    category = request.GET.get('category')
    reason = request.GET.get('reason')
    
    if category:
        logs = logs.filter(category=category)
    if reason:
        logs = logs.filter(reason=reason)
    
    # Calculate summary stats
    total_waste_kg = sum(float(log.quantity) for log in logs)
    total_waste_cost = sum(float(log.estimated_cost or 0) for log in logs)
    
    context = {
        'logs': logs,
        'categories': WasteLog._meta.get_field('category').choices,
        'reasons': WasteLog._meta.get_field('reason').choices,
        'total_waste_kg': total_waste_kg,
        'total_waste_cost': total_waste_cost,
    }
    return render(request, 'food/waste_logs_list.html', context)


@login_required
def waste_log_form(request):
    """Add new waste log"""
    if request.method == 'POST':
        # Create waste log from POST data
        item_name = request.POST.get('item_name')
        quantity = request.POST.get('quantity')
        unit = request.POST.get('unit')
        category = request.POST.get('category')
        estimated_cost = request.POST.get('estimated_cost')
        reason = request.POST.get('reason')
        waste_date = request.POST.get('waste_date')
        notes = request.POST.get('notes', '')
        
        try:
            WasteLog.objects.create(
                user=request.user,
                item_name=item_name,
                quantity=quantity,
                unit=unit,
                category=category,
                estimated_cost=estimated_cost if estimated_cost else None,
                reason=reason,
                waste_date=waste_date if waste_date else timezone.now().date(),
                notes=notes
            )
            messages.success(request, f'Waste log for {item_name} added successfully!')
            return redirect('food:waste_logs_list')
        except Exception as e:
            messages.error(request, f'Error creating waste log: {str(e)}')
    
    context = {
        'categories': WasteLog._meta.get_field('category').choices,
        'reasons': WasteLog._meta.get_field('reason').choices,
        'units': ['kg', 'g', 'liter', 'ml', 'piece', 'pcs'],
    }
    return render(request, 'food/waste_log_form.html', context)


@login_required
def waste_log_delete(request, pk):
    """Delete waste log"""
    log = get_object_or_404(WasteLog, pk=pk, user=request.user)
    log_name = log.item_name
    log.delete()
    messages.success(request, f'Waste log for {log_name} deleted.')
    return redirect('food:waste_logs_list')


# Food Surplus/Sharing Views
@login_required
def surplus_list(request):
    """List all available food surplus"""
    from .models import FoodSurplus
    
    # Get all available surplus items
    surplus_items = FoodSurplus.objects.filter(status='available')
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        surplus_items = surplus_items.filter(category=category)
    
    # Filter by location if provided
    location = request.GET.get('location')
    if location:
        surplus_items = surplus_items.filter(pickup_location__icontains=location)
    
    # Exclude expired items
    surplus_items = surplus_items.filter(available_until__gt=timezone.now())
    
    context = {
        'surplus_items': surplus_items,
        'categories': FoodSurplus.CATEGORY_CHOICES,
        'user_surplus': FoodSurplus.objects.filter(donor=request.user).order_by('-created_at')[:5]
    }
    return render(request, 'food/surplus_list.html', context)


@login_required
def surplus_create(request):
    """Create a new food surplus listing"""
    from .models import FoodSurplus
    
    if request.method == 'POST':
        try:
            # Calculate available_until datetime
            hours = int(request.POST.get('available_hours', 24))
            available_until = timezone.now() + timedelta(hours=hours)
            
            surplus = FoodSurplus.objects.create(
                donor=request.user,
                item_name=request.POST.get('item_name'),
                category=request.POST.get('category'),
                quantity=request.POST.get('quantity'),
                unit=request.POST.get('unit'),
                description=request.POST.get('description', ''),
                available_until=available_until,
                pickup_location=request.POST.get('pickup_location'),
                pickup_instructions=request.POST.get('pickup_instructions', ''),
                status='available'
            )
            
            messages.success(request, f'Surplus "{surplus.item_name}" listed successfully!')
            return redirect('food:surplus_list')
        except Exception as e:
            messages.error(request, f'Error creating surplus: {str(e)}')
    
    context = {
        'categories': FoodSurplus.CATEGORY_CHOICES,
        'units': ['kg', 'g', 'liter', 'ml', 'piece', 'bunch', 'loaf', 'dozen'],
    }
    return render(request, 'food/surplus_form.html', context)


@login_required
def surplus_detail(request, pk):
    """View surplus details and claim it"""
    from .models import FoodSurplus
    
    surplus = get_object_or_404(FoodSurplus, pk=pk)
    
    if request.method == 'POST' and request.POST.get('action') == 'claim':
        if surplus.status == 'available' and surplus.is_available:
            if surplus.donor != request.user:
                surplus.recipient = request.user
                surplus.status = 'reserved'
                surplus.save()
                messages.success(request, f'You have claimed "{surplus.item_name}". Contact donor for pickup.')
            else:
                messages.warning(request, 'You cannot claim your own surplus.')
        else:
            messages.error(request, 'This surplus is no longer available.')
        return redirect('food:surplus_detail', pk=pk)
    
    context = {
        'surplus': surplus,
    }
    return render(request, 'food/surplus_detail.html', context)


@login_required
def surplus_my_listings(request):
    """View user's own surplus listings"""
    from .models import FoodSurplus
    from django.db.models import Sum
    
    # Get filter from query params
    status_filter = request.GET.get('status', 'all')
    
    my_listings = FoodSurplus.objects.filter(donor=request.user).order_by('-created_at')
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        my_listings = my_listings.filter(status=status_filter)
    
    # Calculate stats
    all_listings = FoodSurplus.objects.filter(donor=request.user)
    available_count = all_listings.filter(status='available').count()
    reserved_count = all_listings.filter(status='reserved').count()
    completed_count = all_listings.filter(status='completed').count()
    total_quantity = all_listings.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    context = {
        'listings': my_listings,
        'status_filter': status_filter,
        'available_count': available_count,
        'reserved_count': reserved_count,
        'completed_count': completed_count,
        'total_quantity': total_quantity,
    }
    return render(request, 'food/surplus_my_listings.html', context)


@login_required
def surplus_complete(request, pk):
    """Mark surplus as completed"""
    from .models import FoodSurplus
    
    surplus = get_object_or_404(FoodSurplus, pk=pk, donor=request.user)
    
    if request.method == 'POST':
        surplus.status = 'completed'
        surplus.completed_at = timezone.now()
        surplus.save()
        messages.success(request, f'Surplus "{surplus.item_name}" marked as completed.')
        return redirect('food:surplus_my_listings')
    
    return redirect('food:surplus_detail', pk=pk)
