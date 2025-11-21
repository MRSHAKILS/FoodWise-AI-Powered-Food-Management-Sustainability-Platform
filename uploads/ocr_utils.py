"""
Utility module for processing food images using Google Gemini AI
Integrates with Django models to automatically extract food items from images
"""
import os
import json
import google.generativeai as genai
from PIL import Image
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def configure_gemini():
    """Configure Gemini API with key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please add it to your .env file. Get your key from: "
            "https://makersuite.google.com/app/apikey"
        )
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash-exp')


def process_food_image(image_path):
    """
    Process a food image and extract structured food item data
    
    Args:
        image_path: Path to the image file (can be Django FileField path)
    
    Returns:
        dict: {
            'success': bool,
            'items': list of food items,
            'error': str (if success is False)
        }
    """
    try:
        # Configure API
        model = configure_gemini()
        
        # Load Image
        img = Image.open(image_path)
        
        # The Prompt
        prompt = """
        You are a food inventory assistant. Analyze the image and identify all food items.
        
        For each distinct item, extract or estimate:
        1. Item Name (Specific, e.g., "Sagor Kola (Banana)" with English in parentheses if Bangla).
        2. Category (Choose from: fruit, vegetable, dairy, meat, grain, beverage, snack, other).
        3. Quantity (Count visible items strictly).
        4. Quantity Unit (e.g., pcs, kg, liter, bundle, packet).
        5. Typical Expiration: Estimate the typical expiration time in DAYS based on visual freshness (e.g., a brown banana has 1-2 days, fresh eggs 15-20 days, etc.). Use integer for single value.
        6. Sample Cost Per Unit: Estimate average market price per unit in Bangladeshi Taka (BDT) as a number.
        7. Unit: Same as quantity_unit (measurement unit).

        Return ONLY a valid JSON array. No markdown formatting, no code blocks, no explanatory text.
        
        Structure:
        [
            {
                "item_name": "string",
                "category": "string (lowercase)",
                "quantity": number,
                "quantity_unit": "string",
                "typical_expiration_days": number,
                "sample_cost_per_unit": number,
                "unit": "string"
            }
        ]
        
        If no food items are visible, return an empty array: []
        """
        
        # Generate Content
        response = model.generate_content([prompt, img])
        
        # Check if response is blocked or empty
        if not response or not response.text:
            return {
                'success': False,
                'items': [],
                'error': 'Gemini API returned no response. Possible reasons: API quota exceeded, content policy violation, or rate limiting. Please check your API key limits at https://makersuite.google.com/'
            }
        
        # Clean and Parse JSON
        raw_text = response.text.strip()
        # Remove markdown code blocks if present
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        items = json.loads(raw_text)
        
        # Validate that we got a list
        if not isinstance(items, list):
            return {
                'success': False,
                'items': [],
                'error': 'AI returned invalid format (expected list)'
            }
        
        return {
            'success': True,
            'items': items,
            'error': None
        }
    
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'items': [],
            'error': f'Failed to parse AI response as JSON: {str(e)}. Raw response may not be in correct format.'
        }
    except Exception as e:
        error_msg = str(e)
        
        # Check for common API errors
        if 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
            error_msg = f"⚠️ API Quota/Limit Exceeded: {error_msg}. Your Gemini API key may have reached its free tier limit. Check usage at https://makersuite.google.com/"
        elif 'api_key' in error_msg.lower() or 'authentication' in error_msg.lower():
            error_msg = f"🔑 Authentication Error: {error_msg}. Please verify your GEMINI_API_KEY is correct."
        elif 'blocked' in error_msg.lower() or 'safety' in error_msg.lower():
            error_msg = f"🛡️ Content Safety: {error_msg}. The image may have been blocked by safety filters."
        else:
            error_msg = f"❌ AI Processing failed: {error_msg}"
        
        return {
            'success': False,
            'items': [],
            'error': error_msg
        }


def create_inventory_items_from_ocr(user, ocr_items, upload_instance=None):
    """
    Create FoodItem instances from OCR-extracted data
    
    Args:
        user: User instance
        ocr_items: List of item dictionaries from OCR
        upload_instance: Optional Upload instance to link items to
    
    Returns:
        dict: {
            'success': bool,
            'created_count': int,
            'items': list of created FoodItem instances,
            'errors': list of error messages
        }
    """
    from food.models import FoodItem
    
    created_items = []
    errors = []
    
    # Category mapping to ensure valid choices
    category_mapping = {
        'fruit': 'fruit',
        'vegetable': 'vegetable',
        'dairy': 'dairy',
        'dairy/poultry': 'dairy',
        'meat': 'meat',
        'fish/meat': 'meat',
        'grain': 'grain',
        'grain/snack': 'grain',
        'beverage': 'beverage',
        'snack': 'snack',
        'spice': 'other',
        'oil/fat': 'other',
        'dry good': 'other',
        'other': 'other',
    }
    
    for item_data in ocr_items:
        try:
            # Extract and validate data
            item_name = item_data.get('item_name', 'Unknown Item')
            quantity = item_data.get('quantity', 1)
            unit = item_data.get('unit') or item_data.get('quantity_unit', 'pcs')
            category = item_data.get('category', 'other').lower()
            typical_expiration_days = item_data.get('typical_expiration_days', 7)
            cost = item_data.get('sample_cost_per_unit', 0)
            
            # Map category
            mapped_category = category_mapping.get(category, 'other')
            
            # Calculate expiration date
            today = timezone.now().date()
            expiration_date = today + timedelta(days=int(typical_expiration_days))
            
            # Create FoodItem
            food_item = FoodItem.objects.create(
                user=user,
                name=item_name,
                quantity=quantity,
                unit=unit,
                category=mapped_category,
                purchase_date=today,
                expiration_date=expiration_date,
                price=cost,
                notes=f'Auto-added via AI image recognition'
            )
            
            created_items.append(food_item)
            
        except Exception as e:
            errors.append(f"Failed to create item '{item_data.get('item_name', 'unknown')}': {str(e)}")
    
    return {
        'success': len(created_items) > 0,
        'created_count': len(created_items),
        'items': created_items,
        'errors': errors
    }


def process_upload_with_ocr(upload_instance):
    """
    Process an Upload instance with OCR and create inventory items
    
    Args:
        upload_instance: Upload model instance
    
    Returns:
        dict: {
            'success': bool,
            'created_count': int,
            'message': str,
            'items': list of created items (optional),
            'errors': list of errors (optional)
        }
    """
    # Check if already processed
    if upload_instance.processed:
        return {
            'success': False,
            'created_count': 0,
            'message': 'This image has already been processed',
            'errors': []
        }
    
    # Get the file path
    image_path = upload_instance.file.path
    
    # Process with OCR
    ocr_result = process_food_image(image_path)
    
    if not ocr_result['success']:
        return {
            'success': False,
            'created_count': 0,
            'message': ocr_result['error'],
            'errors': [ocr_result['error']]
        }
    
    # No items found
    if not ocr_result['items']:
        upload_instance.processed = True
        upload_instance.notes += '\n[AI Processing: No food items detected in image]'
        upload_instance.save()
        
        return {
            'success': False,
            'created_count': 0,
            'message': 'No food items detected in the image',
            'errors': []
        }
    
    # Create inventory items
    creation_result = create_inventory_items_from_ocr(
        user=upload_instance.user,
        ocr_items=ocr_result['items'],
        upload_instance=upload_instance
    )
    
    # Mark as processed
    upload_instance.processed = True
    upload_instance.notes += f'\n[AI Processing: {creation_result["created_count"]} items detected and added to inventory]'
    upload_instance.save()
    
    # Link first item to upload if any were created
    if creation_result['items']:
        first_item = creation_result['items'][0]
        upload_instance.associated_inventory = first_item
        upload_instance.save()
    
    return {
        'success': creation_result['success'],
        'created_count': creation_result['created_count'],
        'message': f"Successfully detected and added {creation_result['created_count']} food items to inventory",
        'items': creation_result['items'],
        'errors': creation_result['errors']
    }
