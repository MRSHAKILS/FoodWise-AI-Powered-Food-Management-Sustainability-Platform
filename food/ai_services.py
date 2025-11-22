"""
AI Service Utilities for Gemini API Integration
Provides reusable functions for all AI features with error handling,
rate limiting, and fallback logic.
"""

import os
import json
import time
import logging
from functools import wraps
from typing import Dict, List, Any, Optional
from django.core.cache import cache
from django.conf import settings
import google.generativeai as genai

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")


class GeminiService:
    """Main service class for Gemini API interactions"""
    
    # Rate limiting configuration (Free tier: 15 RPM, 1M TPM)
    RATE_LIMIT_WINDOW = 60  # seconds
    MAX_REQUESTS_PER_WINDOW = 15
    CACHE_PREFIX = 'gemini_rate_limit'
    
    def __init__(self, model_name='gemini-2.0-flash-lite'):
        """
        Initialize Gemini service
        Args:
            model_name: Model to use (gemini-2.0-flash-lite - lightweight flash model with better quota)
        """
        self.model_name = model_name
        self.model = None
        
        if GEMINI_API_KEY:
            try:
                self.model = genai.GenerativeModel(model_name)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        cache_key = f"{self.CACHE_PREFIX}:requests"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.MAX_REQUESTS_PER_WINDOW:
            logger.warning("Rate limit exceeded for Gemini API")
            return False
        
        # Increment counter
        cache.set(cache_key, current_count + 1, self.RATE_LIMIT_WINDOW)
        return True
    
    def _parse_json_response(self, text: str) -> Any:
        """
        Parse JSON from Gemini response, handling markdown code blocks
        """
        try:
            # Remove markdown code blocks if present
            clean_text = text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            if clean_text.startswith('```'):
                clean_text = clean_text[3:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            
            return json.loads(clean_text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}\nText: {text[:200]}")
            raise
    
    def generate_content(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        expect_json: bool = False,
        cache_key: Optional[str] = None,
        cache_timeout: int = 3600,
        retry_count: int = 3
    ) -> Optional[Any]:
        """
        Generate content using Gemini API with error handling and caching
        
        Args:
            prompt: The prompt to send to Gemini
            temperature: Creativity level (0.0-1.0)
            expect_json: If True, parse response as JSON
            cache_key: Optional cache key for result caching
            cache_timeout: Cache timeout in seconds
            retry_count: Number of retry attempts
            
        Returns:
            Generated content (str or dict/list if expect_json=True)
        """
        # Check cache first
        if cache_key:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_result
        
        # Check if model is initialized
        if not self.model:
            logger.error("Gemini model not initialized")
            return None
        
        # Retry loop
        for attempt in range(retry_count):
            try:
                # Check rate limit
                if not self._check_rate_limit():
                    if attempt < retry_count - 1:
                        wait_time = 5 * (attempt + 1)
                        logger.info(f"Rate limited, waiting {wait_time}s before retry")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception("Rate limit exceeded, max retries reached")
                
                # Generate content
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                    )
                )
                
                # Extract text
                result_text = response.text
                
                # Parse JSON if needed
                result = self._parse_json_response(result_text) if expect_json else result_text
                
                # Cache result
                if cache_key:
                    cache.set(cache_key, result, cache_timeout)
                
                return result
                
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}/{retry_count}): {e}")
                
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                else:
                    logger.error("All retry attempts failed")
                    return None
        
        return None
    
    def generate_with_images(
        self,
        prompt: str,
        images: List[Any],
        temperature: float = 0.7,
        expect_json: bool = False
    ) -> Optional[Any]:
        """
        Generate content with image inputs (for OCR)
        
        Args:
            prompt: Text prompt
            images: List of PIL Image objects
            temperature: Creativity level
            expect_json: Parse as JSON
            
        Returns:
            Generated content
        """
        if not self.model:
            logger.error("Gemini model not initialized")
            return None
        
        try:
            # Check rate limit
            if not self._check_rate_limit():
                raise Exception("Rate limit exceeded")
            
            # Generate content with images
            response = self.model.generate_content(
                [prompt] + images,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                )
            )
            
            result_text = response.text
            return self._parse_json_response(result_text) if expect_json else result_text
            
        except Exception as e:
            logger.error(f"Gemini Vision API error: {e}")
            return None


# Convenience functions for common operations

def analyze_consumption_patterns(consumption_data: List[Dict]) -> Optional[Dict]:
    """
    Analyze user consumption patterns using Gemini
    
    Args:
        consumption_data: List of consumption log dictionaries
        
    Returns:
        Analysis results with trends, flags, and waste predictions
    """
    service = GeminiService()
    
    prompt = f"""Analyze this 30-day food consumption data: {json.dumps(consumption_data)}

Identify:
1. Weekly consumption trends by category
2. Over/under-consumption patterns
3. Items likely to waste in next 7 days
4. Nutritional imbalances

Return response as JSON with structure:
{{
  "trends": [{{"category": string, "avgConsumption": number, "trend": "increasing|decreasing|stable"}}],
  "flags": [{{"type": string, "category": string, "severity": "high|medium|low", "message": string}}],
  "wasteRisk": [{{"itemId": string, "itemName": string, "riskScore": number, "daysUntilWaste": number}}],
  "insights": string
}}"""
    
    cache_key = f"consumption_analysis:{hash(json.dumps(consumption_data))}"
    
    return service.generate_content(
        prompt=prompt,
        temperature=0.5,
        expect_json=True,
        cache_key=cache_key,
        cache_timeout=1800  # 30 minutes
    )


def generate_meal_plan(
    budget: float,
    inventory: List[Dict],
    dietary_needs: Dict,
    days: int = 7
) -> Optional[Dict]:
    """
    Generate optimized meal plan using Gemini
    
    Args:
        budget: Budget limit
        inventory: Current inventory items
        dietary_needs: Dietary requirements and preferences
        days: Number of days to plan
        
    Returns:
        Meal plan with schedule, shopping list, and costs
    """
    service = GeminiService()
    
    prompt = f"""Create a {days}-day meal plan:
Budget: ${budget}
Current Inventory: {json.dumps(inventory)}
Dietary Requirements: {json.dumps(dietary_needs)}

Rules:
- Prioritize items expiring within 5 days
- Ensure minimum: 50g protein/day, 5 veggie servings/day
- Stay within budget
- Minimize waste

Return JSON:
{{
  "mealPlan": [{{"day": string, "meals": [{{"name": string, "ingredients": [string], "cost": number, "nutrients": {{}}}}]}}],
  "shoppingList": [{{"item": string, "quantity": string, "estimatedCost": number}}],
  "totalCost": number,
  "wasteReduction": string,
  "nutritionScore": number
}}"""
    
    return service.generate_content(
        prompt=prompt,
        temperature=0.7,
        expect_json=True
    )


def chat_with_nourish_bot(
    user_message: str,
    user_context: Dict,
    chat_history: Optional[List[Dict]] = None
) -> Optional[str]:
    """
    Chat with NourishBot for food sustainability guidance
    
    Args:
        user_message: User's message
        user_context: User's inventory and consumption data
        chat_history: Previous conversation history
        
    Returns:
        Bot response
    """
    service = GeminiService(model_name='gemini-2.0-flash-lite')
    
    # Build detailed context with actual user data
    inventory_items = user_context.get('inventory', [])
    consumption_items = user_context.get('recent_consumption', [])
    budget = user_context.get('budget', 'Not set')
    
    # Format inventory details
    inventory_str = "\n".join([
        f"  - {item['name']}: {item['quantity']} units (expires in {item['expiring_days']} days)" 
        if item['expiring_days'] is not None 
        else f"  - {item['name']}: {item['quantity']} units"
        for item in inventory_items[:10]
    ]) if inventory_items else "  No items in inventory"
    
    # Format consumption details
    consumption_str = "\n".join([
        f"  - {item['name']}: {item['quantity']} units on {item['date']}"
        for item in consumption_items[:10]
    ]) if consumption_items else "  No recent consumption logged"
    
    # Build context-aware prompt
    context_str = f"""
User's Current Situation:
- Budget: ${budget}
- Total Inventory Items: {len(inventory_items)}

Current Inventory:
{inventory_str}

Recent Consumption (Last 10 items):
{consumption_str}
"""
    
    system_instruction = """You are NourishBot, an AI assistant helping users reduce food waste, 
improve nutrition, and make sustainable food choices aligned with UN SDG 2 (Zero Hunger) and 
SDG 12 (Responsible Consumption). 

Your role:
1. Analyze the user's inventory and consumption patterns
2. Suggest recipes using items that are expiring soon
3. Provide nutrition tips based on their eating habits
4. Recommend storage tips to extend food life
5. Offer sustainable food choices and waste reduction strategies

Be practical, friendly, and actionable. Always reference their actual inventory items when giving advice."""
    
    # Add chat history if available
    history_str = ""
    if chat_history:
        history_str = "\n\nPrevious Conversation:\n"
        for msg in chat_history[-5:]:  # Last 5 messages
            role = "User" if msg.get('role') == 'user' else "NourishBot"
            history_str += f"{role}: {msg.get('content')}\n"
    
    full_prompt = f"{system_instruction}\n\n{context_str}{history_str}\n\nUser: {user_message}\n\nNourishBot:"
    
    response = service.generate_content(
        prompt=full_prompt,
        temperature=0.7,
        cache_timeout=0  # Don't cache chat responses
    )
    
    # Use intelligent fallback if AI response fails
    if not response:
        return nourish_bot_fallback(user_message, user_context)
    
    return response


def calculate_sdg_score(
    waste_data: Dict,
    nutrition_data: Dict,
    budget_data: Dict
) -> Optional[Dict]:
    """
    Calculate SDG impact score with AI insights
    
    Args:
        waste_data: Waste reduction metrics
        nutrition_data: Nutrition balance metrics
        budget_data: Budget efficiency metrics
        
    Returns:
        SDG score breakdown and insights
    """
    service = GeminiService()
    
    prompt = f"""Calculate SDG impact score based on:

Waste Reduction: {json.dumps(waste_data)}
Nutrition Balance: {json.dumps(nutrition_data)}
Budget Efficiency: {json.dumps(budget_data)}

Calculate score (0-100) with weights:
- Waste Reduction: 40%
- Nutrition Balance: 30%
- Budget Efficiency: 20%
- Community Engagement: 10%

Return JSON:
{{
  "totalScore": number,
  "breakdown": {{
    "wasteReduction": number,
    "nutritionBalance": number,
    "budgetEfficiency": number,
    "communityEngagement": number
  }},
  "weeklyChange": number,
  "insights": string,
  "recommendations": [string]
}}"""
    
    return service.generate_content(
        prompt=prompt,
        temperature=0.6,
        expect_json=True
    )


def extract_food_from_image(image_path: str) -> Optional[List[Dict]]:
    """
    Extract food items from image using Gemini Vision
    
    Args:
        image_path: Path to image file
        
    Returns:
        List of extracted food items
    """
    from PIL import Image
    
    service = GeminiService(model_name='gemini-2.0-flash-lite')
    
    try:
        image = Image.open(image_path)
    except Exception as e:
        logger.error(f"Failed to open image: {e}")
        return None
    
    prompt = """Analyze this image of food items, grocery receipt, or product label. 
Extract and return ONLY a JSON array with this structure: 
[{
  "itemName": "string", 
  "quantity": "string with unit", 
  "expiryDate": "YYYY-MM-DD or null",
  "category": "fruit|vegetable|dairy|meat|grain|snack|other"
}]

If expiration date is not visible, set to null. Be precise with item names."""
    
    return service.generate_with_images(
        prompt=prompt,
        images=[image],
        temperature=0.3,
        expect_json=True
    )


# Fallback functions for when AI is unavailable

def nourish_bot_fallback(user_message: str, user_context: Dict) -> str:
    """
    Rule-based fallback responses for NourishBot when AI is unavailable
    Provides helpful, context-aware responses based on user data
    """
    message_lower = user_message.lower()
    inventory = user_context.get('inventory', [])
    consumption = user_context.get('recent_consumption', [])
    budget = user_context.get('budget', 'Not set')
    
    # Find items expiring soon (within 3 days)
    expiring_soon = [item for item in inventory if item.get('expiring_days') is not None and item['expiring_days'] <= 3]
    
    # Recipe/meal suggestions
    if any(word in message_lower for word in ['recipe', 'cook', 'make', 'meal', 'dish', 'prepare']):
        if expiring_soon:
            items_list = ', '.join([item['name'] for item in expiring_soon[:3]])
            return f"""Based on your inventory, I recommend using these items expiring soon: {items_list}.

Quick recipe ideas:
• If you have {expiring_soon[0]['name']}, try making a stir-fry or soup
• Combine multiple items for a mixed dish to reduce waste
• Check online for specific recipes using these ingredients

Tip: Use items expiring in the next 1-3 days first to minimize waste! 🌱"""
        elif inventory:
            items_list = ', '.join([item['name'] for item in inventory[:3]])
            return f"""You have {len(inventory)} items in your inventory including: {items_list}.

General recipe suggestions:
• Look for recipes that use multiple ingredients from your inventory
• Consider batch cooking to save time
• Freeze portions for later to extend shelf life

Would you like specific tips for any particular ingredient?"""
        else:
            return "You don't have any items in your inventory yet. Add some items to get personalized recipe suggestions!"
    
    # Waste reduction
    elif any(word in message_lower for word in ['waste', 'reduce', 'save', 'prevent']):
        response = f"""Here are ways to reduce food waste:

📦 Storage Tips:
• Store fruits and vegetables separately
• Keep herbs in water like flowers
• Use airtight containers for leftovers

⏰ Timing:
• First In, First Out (FIFO) - use older items first
• Check expiration dates weekly"""
        if expiring_soon:
            response += f"\n\n⚠️ Priority Action: You have {len(expiring_soon)} items expiring within 3 days:\n"
            for item in expiring_soon[:3]:
                response += f"  • {item['name']} - {item['expiring_days']} days left\n"
        return response
    
    # Storage/preservation
    elif any(word in message_lower for word in ['storage', 'store', 'keep', 'preserve', 'freeze']):
        return """Food Storage Best Practices:

❄️ Freezer:
• Bread, meat, cooked meals can be frozen
• Label with dates
• Use freezer bags to prevent freezer burn

🧊 Refrigerator:
• Keep temperature at 37-40°F (3-4°C)
• Store meat on bottom shelf
• Keep dairy products in main compartment, not door

🏠 Pantry:
• Cool, dry, dark place
• Use airtight containers
• Check for pests regularly

Tip: Blanch vegetables before freezing to preserve color and nutrients!"""
    
    # Nutrition
    elif any(word in message_lower for word in ['nutrition', 'healthy', 'vitamin', 'protein', 'balanced']):
        categories = {}
        for item in inventory:
            cat = item.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        response = "Balanced Nutrition Tips:\n\n"
        response += "🥗 Daily Goals:\n"
        response += "• 5+ servings fruits & vegetables\n"
        response += "• 50-60g protein\n"
        response += "• Whole grains at each meal\n"
        response += "• Healthy fats (nuts, olive oil)\n\n"
        
        if categories:
            response += f"📊 Your Inventory Balance:\n"
            for cat, count in categories.items():
                response += f"  • {cat.title()}: {count} items\n"
        
        return response
    
    # Budget
    elif any(word in message_lower for word in ['budget', 'money', 'save', 'cheap', 'affordable']):
        return f"""Budget-Friendly Food Tips:

💰 Your Budget: ${budget if budget != 'Not set' else '100 (recommended)'}

Smart Shopping:
• Buy seasonal produce (cheaper & fresher)
• Compare unit prices, not package prices
• Use store brands for staples
• Buy in bulk for non-perishables

Meal Planning:
• Plan weekly meals before shopping
• Cook in batches and freeze portions
• Use all parts (broth from bones, etc.)
• Stretch meals with grains and beans

Waste = Wasted Money! Every item thrown away costs you twice - purchase price + disposal."""
    
    # Inventory check
    elif any(word in message_lower for word in ['inventory', 'have', 'stock', 'items']):
        if inventory:
            response = f"📦 Your Current Inventory ({len(inventory)} items):\n\n"
            for item in inventory[:10]:
                exp_info = f" - expires in {item['expiring_days']} days" if item.get('expiring_days') is not None else ""
                response += f"• {item['name']}: {item['quantity']} units{exp_info}\n"
            if len(inventory) > 10:
                response += f"\n... and {len(inventory) - 10} more items"
            return response
        else:
            return "Your inventory is empty. Start adding items to track your food and get personalized recommendations!"
    
    # Default helpful response
    else:
        tips = []
        if expiring_soon:
            tips.append(f"⚠️ You have {len(expiring_soon)} items expiring soon - use them first!")
        if inventory:
            tips.append(f"📦 You have {len(inventory)} items in inventory")
        if consumption:
            tips.append(f"📊 {len(consumption)} items consumed recently")
        
        response = "I'm NourishBot, your food sustainability assistant! 🌱\n\n"
        if tips:
            response += "\n".join(tips) + "\n\n"
        
        response += """I can help you with:
• Recipe suggestions using your inventory
• Food storage and preservation tips
• Waste reduction strategies
• Nutrition advice
• Budget-friendly meal planning

What would you like to know?"""
        return response

def rule_based_consumption_analysis(consumption_data: List[Dict]) -> Dict:
    """Simple rule-based fallback for consumption analysis"""
    from collections import defaultdict
    
    category_counts = defaultdict(int)
    for log in consumption_data:
        category_counts[log.get('category', 'other')] += 1
    
    total = len(consumption_data)
    trends = []
    
    for category, count in category_counts.items():
        avg = count / 30  # Assume 30 days
        trends.append({
            "category": category,
            "avgConsumption": avg,
            "trend": "stable"
        })
    
    return {
        "trends": trends,
        "flags": [],
        "wasteRisk": [],
        "insights": "Using fallback analysis. Enable Gemini API for AI-powered insights."
    }
