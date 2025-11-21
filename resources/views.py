from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Resource


def resources_list(request):
    """Browse educational resources with filters and search"""
    # Get all resources
    resources = Resource.objects.all()
    
    # Apply category filter if provided
    category = request.GET.get('category')
    if category:
        resources = resources.filter(category=category)
    
    # Apply type filter if provided
    resource_type = request.GET.get('type')
    if resource_type:
        resources = resources.filter(type=resource_type)
    
    # Apply search filter if provided (search in title and description)
    search = request.GET.get('search')
    if search:
        resources = resources.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    # Order by title (alphabetically)
    resources = resources.order_by('title')
    
    # Get unique categories and types for filter dropdowns
    categories = Resource.CATEGORY_CHOICES
    types = Resource.TYPE_CHOICES
    
    context = {
        'resources': resources,
        'categories': categories,
        'types': types,
        'selected_category': category,
        'selected_type': resource_type,
        'search_query': search,
    }
    return render(request, 'resources/resources_list.html', context)


def resources_by_category(request, category):
    """Filter resources by category (legacy view)"""
    resources = Resource.objects.filter(category=category).order_by('title')
    categories = Resource.CATEGORY_CHOICES
    
    context = {
        'resources': resources,
        'category': category,
        'categories': categories,
    }
    return render(request, 'resources/resources_by_category.html', context)


def resource_detail(request, id):
    """Display detailed information about a single resource"""
    # Get single resource or return 404 if not found
    resource = get_object_or_404(Resource, pk=id)
    
    context = {
        'resource': resource,
    }
    return render(request, 'resources/resource_detail.html', context)


def recommended_resources(request):
    # TODO: Implement Phase 5 rule-based recommendation logic
    # Example: IF user logs 'Milk' (Dairy) THEN suggest 'How to keep milk fresh'
    return render(request, 'resources/recommendations.html')
