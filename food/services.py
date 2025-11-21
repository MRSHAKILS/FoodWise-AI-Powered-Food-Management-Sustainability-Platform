import datetime
from collections import defaultdict, Counter
from django.db.models import Sum, F
from .models import ConsumptionLog, PantryItem, FoodCategory

class ConsumptionAnalyzer:
    """
    Service layer to handle pattern recognition, waste prediction,
    and trend analysis.
    """

    def __init__(self, user):
        self.user = user
        self.today = datetime.date.today()

    def get_weekly_heatmap_data(self):
        """
        Generates a heatmap structure: Day of Week vs Category Intensity.
        Returns JSON-serializable dict.
        """
        # Get logs for the last 30 days for better trend analysis
        start_date = self.today - datetime.timedelta(days=30)
        logs = ConsumptionLog.objects.filter(
            user=self.user, 
            date_consumed__gte=start_date
        ).select_related('food_item')

        # Structure: {'Monday': {'Fruit': 5, 'Veg': 2}, ...}
        heatmap = {day: defaultdict(int) for day in [
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ]}

        for log in logs:
            day_name = log.date_consumed.strftime('%A')
            category = log.food_item.category
            heatmap[day_name][category] += log.quantity

        return heatmap

    def detect_imbalances(self):
        """
        Identifies over/under consumption based on simple dietary heuristics.
        """
        last_7_days = self.today - datetime.timedelta(days=7)
        logs = ConsumptionLog.objects.filter(
            user=self.user, 
            date_consumed__gte=last_7_days
        ).select_related('food_item')

        total_items = logs.count()
        if total_items == 0:
            return ["No consumption data available for analysis."]

        category_counts = Counter([log.food_item.category for log in logs])
        insights = []

        # 1. Veggie Check (Goal: ~30% of intake)
        veg_count = category_counts.get(FoodCategory.VEGETABLE, 0)
        if (veg_count / total_items) < 0.15:
            insights.append({
                'type': 'warning',
                'message': 'Low Vegetable Intake detected this week. Consider adding leafy greens.'
            })

        # 2. Sugar/Snack Check (Goal: < 10%)
        snack_count = category_counts.get(FoodCategory.SNACK, 0)
        if (snack_count / total_items) > 0.20:
            insights.append({
                'type': 'critical',
                'message': 'High Snack consumption detected. Try replacing processed snacks with fruits.'
            })

        # 3. Weekend Spike Detection (e.g., Alcohol or fast food)
        # This logic would compare weekend averages vs weekday averages
        
        return insights

    def predict_waste(self):
        """
        Predicts items likely to spoil in 3-7 days.
        """
        # Fetch user's pantry items
        items = PantryItem.objects.filter(user=self.user).select_related('food_item')
        at_risk_items = []

        for item in items:
            days_until_expiry = (item.expiry_date - self.today).days

            if 3 <= days_until_expiry <= 7:
                at_risk_items.append({
                    'name': item.food_item.name,
                    'days_left': days_until_expiry,
                    'quantity': item.quantity,
                    'suggestion': f"Plan a meal with {item.food_item.name} by {item.expiry_date.strftime('%A')}."
                })
            elif days_until_expiry < 0:
                 at_risk_items.append({
                    'name': item.food_item.name,
                    'days_left': days_until_expiry,
                    'quantity': item.quantity,
                    'suggestion': "Item likely expired. Please check and discard."
                })

        # Sort by urgency
        at_risk_items.sort(key=lambda x: x['days_left'])
        return at_risk_items

    def get_llm_prompt_context(self):
        """
        Helper to serialize data if you want to send it to OpenAI/Gemini
        for more 'human' advice.
        """
        waste = self.predict_waste()
        heatmap = self.get_weekly_heatmap_data()
        return f"User Waste Risks: {waste}. Consumption Patterns: {heatmap}. Suggest 3 recipes."