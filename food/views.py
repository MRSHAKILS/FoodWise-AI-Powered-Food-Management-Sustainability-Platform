from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


# Inventory Views
def inventory_list(request):
    # TODO: Query FoodItem model with filters (category, expiration)
    return render(request, 'food/inventory_list.html')


def inventory_form(request):
    # TODO: Implement add inventory form with validation
    return render(request, 'food/inventory_form.html')


def inventory_edit(request, pk):
    # TODO: Implement edit functionality with form
    # item = get_object_or_404(FoodItem, pk=pk)
    return render(request, 'food/inventory_edit.html')


def inventory_delete(request, pk):
    # TODO: Implement delete confirmation and logic
    # item = get_object_or_404(FoodItem, pk=pk)
    # item.delete()
    return redirect('food:inventory_list')


# Consumption Logs Views
def consumption_logs_list(request):
    # TODO: Query ConsumptionLog model
    return render(request, 'food/logs_list.html')


def consumption_log_form(request):
    # TODO: Implement consumption logging form (Item Name, Quantity, Category)
    return render(request, 'food/log_form.html')


def consumption_log_delete(request, pk):
    # TODO: Implement log deletion
    # log = get_object_or_404(ConsumptionLog, pk=pk)
    # log.delete()
    return redirect('food:logs_list')


def consumption_history(request):
    # TODO: Display historical consumption data with charts/graphs
    return render(request, 'food/history.html')

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
import json

# Import your service and models
from .services import ConsumptionAnalyzer
from .models import ConsumptionLog, PantryItem, FoodCategory

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Initialize the Service Layer
        analyzer = ConsumptionAnalyzer(self.request.user)

        # 1. Get Waste Predictions
        context['waste_predictions'] = analyzer.predict_waste()

        # 2. Get Insights/Imbalances
        context['insights'] = analyzer.detect_imbalances()

        # 3. Get Heatmap Data
        # We dump this to JSON string so JavaScript in the template can parse it easily
        raw_heatmap = analyzer.get_weekly_heatmap_data()
        context['heatmap_json'] = mark_safe(json.dumps(raw_heatmap))
        
        # Pass categories for the legend/filtering
        context['categories'] = [c[0] for c in FoodCategory.choices]

        return context