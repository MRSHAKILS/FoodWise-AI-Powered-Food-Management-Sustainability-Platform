import datetime
import json
import logging
from collections import defaultdict, Counter
from django.db.models import Sum
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
    Service layer that aggregates user data and interfaces with a REAL LLM
    (Google Gemini) to generate consumption insights.
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