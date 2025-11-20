from django.shortcuts import render, get_object_or_404


def resources_list(request):
    # TODO: Query Resource model with seeded data (15-20 items)
    # Categories: Waste Reduction, Budget Tips, Meal Planning, Storage Tips
    return render(request, 'resources/resources_list.html')


def resources_by_category(request, category):
    # TODO: Filter resources by category
    return render(request, 'resources/resources_by_category.html', {'category': category})


def resource_detail(request, pk):
    # TODO: Show detailed resource view
    # resource = get_object_or_404(Resource, pk=pk)
    return render(request, 'resources/resource_detail.html')


def recommended_resources(request):
    # TODO: Implement Phase 5 rule-based recommendation logic
    # Example: IF user logs 'Milk' (Dairy) THEN suggest 'How to keep milk fresh'
    return render(request, 'resources/recommendations.html')
