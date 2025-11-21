from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FoodItem, ConsumptionLog, FoodItemDatabase
from users.forms import FoodItemForm, ConsumptionLogForm


# Inventory Views
@login_required
def inventory_list(request):
    """List all inventory items with filters"""
    items = FoodItem.objects.filter(user=request.user)
    
    # Apply filters if provided
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    context = {
        'items': items,
        'categories': FoodItem.CATEGORY_CHOICES,
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
    
    return render(request, 'food/inventory_form.html', {'form': form})


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
    """Delete inventory item"""
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    item_name = item.name
    item.delete()
    messages.success(request, f'{item_name} removed from inventory.')
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
    
    # Get base queryset
    logs = ConsumptionLog.objects.filter(user=request.user)
    
    # Apply filters
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if category:
        logs = logs.filter(category=category)
    if start_date:
        logs = logs.filter(consumption_date__gte=start_date)
    if end_date:
        logs = logs.filter(consumption_date__lte=end_date)
    
    # Calculate statistics
    total_logs = logs.count()
    
    # This week logs
    week_ago = timezone.now().date() - timedelta(days=7)
    week_logs = logs.filter(consumption_date__gte=week_ago).count()
    
    # This month logs
    month_ago = timezone.now().date() - timedelta(days=30)
    month_logs = logs.filter(consumption_date__gte=month_ago).count()
    
    # Category breakdown
    category_stats = logs.values('category').annotate(count=Count('id')).order_by('-count')
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
        'logs': logs.order_by('-consumption_date', '-created_at'),
        'categories': ConsumptionLog.CATEGORY_CHOICES,
        'total_logs': total_logs,
        'week_logs': week_logs,
        'month_logs': month_logs,
        'top_category': top_category,
        'category_breakdown': category_breakdown,
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
