import datetime
import json
import logging
from collections import defaultdict, Counter
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.conf import settings
from .models import ConsumptionLog, FoodItem

# Try importing the generative AI library
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

logger = logging.getLogger(__name__)

class ConsumptionAnalyzer:
    """
    AI Consumption Pattern Analyzer (Advanced)
    
    Features:
    - Weekly trend detection from user data
    - Over/under-consumption detection by category
    - Waste prediction for 3-7 day window
    - Imbalanced pattern flagging
    - Heatmap-style data insights (JSON output)
    """

    def __init__(self, user):
        self.user = user
        self.today = timezone.now().date()
        self.analysis_window_start = self.today - datetime.timedelta(days=30)
        
        # Configure the API Key from Django Settings
        if HAS_GENAI:
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if api_key:
                genai.configure(api_key=api_key)
            else:
                logger.warning("GEMINI_API_KEY not found in settings.")

    def get_data_context(self):
        """
        Aggregates raw data to be sent to the LLM.
        """
        return {
            "weekly_heatmap": self._get_weekly_heatmap_data(),
            "burn_rates": self._calculate_burn_rate(),
            "inventory_summary": self._get_inventory_summary(),
            "recent_logs": self._get_category_percentages()
        }

    def get_ai_insights(self):
        """
        Orchestrates the LLM call.
        Returns a dictionary with parsed JSON insights from the LLM.
        """
        context_data = self.get_data_context()
        
        # 1. Prepare the Prompt (Improved Version)
        prompt = f"""
        ### ROLE
        You are "FoodWise," an expert Eco-Nutritionist and Data Analyst. Your goal is to help users reduce food waste and improve dietary balance.

        ### INPUT DATA
        {json.dumps(context_data, indent=2)}

        ### INSTRUCTIONS
        1. **Analyze Trends:** Look at 'weekly_heatmap'. Identify spikes or patterns (e.g., "You eat 80% of your fruit on weekends" or "No significant patterns detected").
        2. **Detect Imbalances:** Look at 'recent_logs'. Compare against a standard balanced diet (approx. 50% Fruits/Veg, 25% Protein, 25% Grains). Flag significant shortages (e.g., "Vegetable intake is low at 12%").
        3. **Predict Waste (CRITICAL):** - Iterate through 'inventory_summary'.
           - For each item, compare 'qty' against ('burn_rates' for that category * 'days_left').
           - IF (Quantity > Predicted Usage), flag it as a WASTE RISK.
           - IF burn rate is missing, assume a default of 0.2 units/day.

        ### OUTPUT CONSTRAINTS
        - **Format:** Return ONLY raw JSON. Do NOT use Markdown code blocks (no ```json).
        - **Tone:** Helpful, concise, and non-judgmental. 
        - **Safety:** Do not provide medical advice.

        ### REQUIRED JSON SCHEMA
        {{
            "trends": [
                "Short string describing a trend",
                "Short string describing another trend"
            ],
            "imbalances": [
                "Short string warning about a dietary gap"
            ],
            "waste_predictions": [
                {{
                    "item": "Name of item",
                    "reason": "Specific math-based reason (e.g., 'You have 3L Milk expiring in 2 days, but only drink 0.2L/day.')"
                }}
            ]
        }}
        """

        # 2. Call the Real API
        return self._call_llm_api(prompt)

    def _call_llm_api(self, prompt):
        """
        Calls the Google Gemini API (or your preferred provider).
        """
        if not HAS_GENAI:
            return self._error_response("Google Generative AI SDK not installed. Run `pip install google-generativeai`.")

        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            return self._error_response("API Key missing. Please add GEMINI_API_KEY to settings.py.")

        try:
            # Initialize Model (Gemini Pro is good for text)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Clean the response text (remove potential markdown code blocks)
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            # Parse JSON
            return json.loads(response_text)

        except Exception as e:
            logger.error(f"LLM API Error: {e}")
            return self._error_response(f"Error generating insights: {str(e)}")

    def _error_response(self, message):
        """Returns a safe empty structure with an error message in trends."""
        return {
            "trends": [message],
            "imbalances": [],
            "waste_predictions": [],
            "raw_heatmap": self._get_weekly_heatmap_data() # Still return data for charts
        }

    def _get_weekly_heatmap_data(self):
        """Generates Day of Week vs Category counts."""
        logs = ConsumptionLog.objects.filter(
            user=self.user, 
            consumption_date__gte=self.analysis_window_start
        )
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap = {day: defaultdict(float) for day in days}

        for log in logs:
            day_name = log.consumption_date.strftime('%A')
            cat = log.category.lower()
            heatmap[day_name][cat] += float(log.quantity)
        
        return heatmap

    def _calculate_burn_rate(self):
        """Avg daily consumption per category."""
        logs = ConsumptionLog.objects.filter(
            user=self.user, 
            consumption_date__gte=self.analysis_window_start
        ).values('category').annotate(total=Sum('quantity'))
        
        rates = {}
        for l in logs:
            rates[l['category']] = round(float(l['total']) / 30, 2)
        return rates

    def _get_inventory_summary(self):
        """Summarize expiring inventory."""
        next_week = self.today + datetime.timedelta(days=7)
        items = FoodItem.objects.filter(
            user=self.user,
            expiration_date__range=[self.today, next_week]
        )
        return [
            {
                "name": i.name, 
                "qty": float(i.quantity), 
                "category": i.category,
                "days_left": (i.expiration_date - self.today).days
            } 
            for i in items
        ]

    def _get_category_percentages(self):
        """Get dietary balance percentages."""
        logs = ConsumptionLog.objects.filter(user=self.user, consumption_date__gte=self.analysis_window_start)
        total = logs.count()
        if total == 0: return {}
        
        counts = Counter(logs.values_list('category', flat=True))
        return {k: round((v/total)*100, 1) for k,v in counts.items()}

    def detect_weekly_trends(self):
        """
        Identifies weekly trends in consumption (e.g., high fruit intake on weekends).
        Returns list of trend insights.
        """
        heatmap = self._get_weekly_heatmap_data()
        trends = []

        # Weekend vs Weekday analysis
        weekend_days = ['Saturday', 'Sunday']
        weekday_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        weekend_total = sum(sum(heatmap[day].values()) for day in weekend_days)
        weekday_total = sum(sum(heatmap[day].values()) for day in weekday_days)

        if weekday_total > 0:
            ratio = weekend_total / weekday_total if weekday_total > 0 else 0
            if ratio > 1.3:
                trends.append({
                    'type': 'info',
                    'pattern': 'weekend_spike',
                    'message': f'Higher consumption on weekends ({ratio:.1f}x weekday average)',
                    'severity': 'low'
                })
            elif ratio < 0.7 and weekend_total > 0:
                trends.append({
                    'type': 'info',
                    'pattern': 'weekday_focus',
                    'message': 'More consistent weekday consumption than weekends',
                    'severity': 'low'
                })

        # Category-specific weekly patterns
        category_by_day = defaultdict(lambda: defaultdict(list))
        for day, categories in heatmap.items():
            for cat, val in categories.items():
                category_by_day[cat][day].append(val)

        # Identify peak days per category
        for category, days_data in category_by_day.items():
            if days_data:
                peak_day = max(days_data, key=lambda d: sum(days_data[d]))
                peak_value = sum(days_data[peak_day])
                avg_value = sum(sum(vals) for vals in days_data.values()) / len(days_data) if days_data else 1
                
                if peak_value > avg_value * 1.5:
                    trends.append({
                        'type': 'info',
                        'pattern': f'{category}_peak_day',
                        'message': f'High {category} intake on {peak_day} ({peak_value:.0f} units)',
                        'severity': 'low'
                    })

        return trends

    def detect_imbalances(self):
        """
        Detects over/under-consumption by category based on dietary heuristics.
        Returns list of imbalance flags.
        """
        last_7_days = self.today - datetime.timedelta(days=7)
        logs = ConsumptionLog.objects.filter(
            user=self.user,
            consumption_date__gte=last_7_days
        )

        total_items = logs.count()
        if total_items == 0:
            return []

        category_counts = Counter(log.category or 'other' for log in logs)
        imbalances = []

        total_qty = sum(category_counts.values()) or 1

        # 1. Vegetable Check (Goal: ~30% of intake)
        veg_ratio = (category_counts.get('vegetable', 0) / total_qty) if total_qty > 0 else 0
        if veg_ratio < 0.15:
            imbalances.append({
                'type': 'warning',
                'category': 'vegetable',
                'issue': 'under_consumption',
                'message': 'Low Vegetable Intake detected. Aim for 25-30% of daily intake.',
                'current_ratio': f'{veg_ratio*100:.1f}%',
                'target_ratio': '25-30%'
            })
        elif veg_ratio > 0.40:
            imbalances.append({
                'type': 'success',
                'category': 'vegetable',
                'issue': 'healthy_consumption',
                'message': f'Excellent vegetable intake ({veg_ratio*100:.1f}%)!',
                'current_ratio': f'{veg_ratio*100:.1f}%'
            })

        # 2. Fruit Check (Goal: ~15-20%)
        fruit_ratio = (category_counts.get('fruit', 0) / total_qty) if total_qty > 0 else 0
        if fruit_ratio < 0.10:
            imbalances.append({
                'type': 'warning',
                'category': 'fruit',
                'issue': 'under_consumption',
                'message': 'Low Fruit Intake. Aim for 15-20% of daily intake.',
                'current_ratio': f'{fruit_ratio*100:.1f}%',
                'target_ratio': '15-20%'
            })

        # 3. Snack/Processed Check (Goal: < 15%)
        snack_ratio = ((category_counts.get('snack', 0) + category_counts.get('snacks', 0)) / total_qty) if total_qty > 0 else 0
        if snack_ratio > 0.20:
            imbalances.append({
                'type': 'critical',
                'category': 'snack',
                'issue': 'over_consumption',
                'message': f'High Snack consumption ({snack_ratio*100:.1f}%). Try replacing with fruits or nuts.',
                'current_ratio': f'{snack_ratio*100:.1f}%',
                'target_ratio': '<15%'
            })

        # 4. Protein Check (Goal: ~20-25%)
        protein_ratio = ((category_counts.get('meat', 0) + category_counts.get('dairy', 0) + category_counts.get('grain', 0)) / total_qty) if total_qty > 0 else 0
        if protein_ratio < 0.15:
            imbalances.append({
                'type': 'warning',
                'category': 'protein',
                'issue': 'under_consumption',
                'message': 'Low Protein intake. Aim for 20-25% of daily intake.',
                'current_ratio': f'{protein_ratio*100:.1f}%',
                'target_ratio': '20-25%'
            })

        return imbalances

    def predict_waste(self):
        """
        Predicts items likely to spoil in 3-7 days using consumption patterns.
        Uses simple formula: risk = (expiry_days * avg_weekly_consumption_rate)
        """
        items = FoodItem.objects.filter(user=self.user)
        at_risk_items = []

        # Get average consumption per category per week
        week_ago = self.today - datetime.timedelta(days=7)
        weekly_logs = ConsumptionLog.objects.filter(
            user=self.user,
            consumption_date__gte=week_ago
        )
        
        category_avg_consumption = defaultdict(float)
        for log in weekly_logs:
            cat = log.category or 'other'
            try:
                category_avg_consumption[cat] += float(log.quantity)
            except (ValueError, TypeError):
                category_avg_consumption[cat] += 1

        for item in items:
            if not item.expiration_date:
                continue

            days_until_expiry = (item.expiration_date - self.today).days
            item_name = item.name
            category = item.category or 'other'

            # Simple risk score: days_left * consumption_likelihood
            consumption_rate = category_avg_consumption.get(category, 0)
            waste_risk_score = days_until_expiry * max(0.5, 1 - (consumption_rate / 100))

            if 3 <= days_until_expiry <= 7:
                at_risk_items.append({
                    'name': item_name,
                    'days_left': days_until_expiry,
                    'quantity': float(item.quantity),
                    'unit': item.unit,
                    'category': category,
                    'expiration_date': item.expiration_date.isoformat(),
                    'risk_score': waste_risk_score,
                    'urgency': 'high' if days_until_expiry <= 4 else 'medium',
                    'suggestion': f'Plan a meal with {item_name} before {item.expiration_date.strftime("%A, %B %d")}.',
                })
            elif days_until_expiry < 0:
                at_risk_items.append({
                    'name': item_name,
                    'days_left': days_until_expiry,
                    'quantity': float(item.quantity),
                    'unit': item.unit,
                    'category': category,
                    'expiration_date': item.expiration_date.isoformat(),
                    'risk_score': 100,  # Maximum risk
                    'urgency': 'critical',
                    'suggestion': 'Item likely expired. Please check and discard.',
                })

        # Sort by urgency and days left
        at_risk_items.sort(key=lambda x: (x['urgency'] != 'critical', x['days_left']))
        return at_risk_items

    def flag_imbalanced_patterns(self):
        """
        Flags imbalanced consumption patterns (e.g., low veggies, high snacks).
        Returns categorized flags.
        """
        imbalances = self.detect_imbalances()
        trends = self.detect_weekly_trends()
        
        flags = {
            'warnings': [i for i in imbalances if i.get('type') == 'warning'],
            'critical': [i for i in imbalances if i.get('type') == 'critical'],
            'successes': [i for i in imbalances if i.get('type') == 'success'],
            'trends': trends,
        }
        
        return flags

    def generate_heatmap_data(self):
        """
        Generates heatmap JSON for visualization (UI optional).
        Format: {'Monday': {'fruit': 5, 'vegetable': 3}, ...}
        """
        heatmap = self._get_weekly_heatmap_data()
        # Convert defaultdicts to regular dicts for JSON serialization
        return {day: dict(values) for day, values in heatmap.items()}

    def generate_report(self):
        """
        Aggregate all insights into a comprehensive JSON-serializable report.
        Perfect for API response and frontend visualization.
        """
        report = {
            'analysis_date': self.today.isoformat(),
            'user_id': self.user.id,
            'heatmap': self.generate_heatmap_data(),
            'weekly_trends': self.detect_weekly_trends(),
            'imbalances': self.detect_imbalances(),
            'waste_predictions': self.predict_waste(),
            'flags': self.flag_imbalanced_patterns(),
            'summary': {
                'total_logs_7d': ConsumptionLog.objects.filter(
                    user=self.user,
                    consumption_date__gte=self.today - datetime.timedelta(days=7)
                ).count(),
                'total_logs_30d': ConsumptionLog.objects.filter(
                    user=self.user,
                    consumption_date__gte=self.today - datetime.timedelta(days=30)
                ).count(),
                'inventory_items_count': FoodItem.objects.filter(user=self.user).count(),
                'expiring_soon_count': FoodItem.objects.filter(
                    user=self.user,
                    expiration_date__lte=self.today + datetime.timedelta(days=7),
                    expiration_date__gte=self.today
                ).count(),
            }
        }
        return report

    def get_llm_prompt_context(self):
        """
        Serialize analysis data for LLM (OpenAI/Gemini) for human-like advice.
        """
        report = self.generate_report()
        waste = report['waste_predictions']
        imbalances = report['imbalances']
        
        prompt = f"""
Based on the user's food consumption and inventory data:

Waste Risks (Next 7 days):
{json.dumps(waste, indent=2)[:500]}...

Imbalances Detected:
{json.dumps(imbalances, indent=2)[:500]}...

Please suggest:
1. Top 3 recipes using at-risk items
2. Dietary adjustments for imbalances
3. Shopping recommendations
"""
        return prompt