import argparse
import os
import json
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_image(image_path):
    """
    Sends image to Gemini 1.5 Pro and returns structured JSON data.
    """
    # 1. Configure API
    genai.configure(api_key=API_KEY)
    
    # 2. Load Model (Using gemini-2.0-flash-lite - lightweight flash model)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')

    # 3. Load Image
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(json.dumps({"error": f"Could not open image: {str(e)}"}))
        return

    # 4. The Prompt
    prompt = """
    You are a food inventory assistant. Analyze the image and identify all food items.
    
    For each distinct item, extract or estimate:
    1. Item Name (Specific, e.g., "Sagor Kola (Banana)" with English in parentheses).
    2. Category (Fruit, Vegetable, Dairy, Grain, Fish/Meat, Spice, Snack, Oil/Fat, Dairy/Poultry, Grain/Snack, Dry Good).
    3. Quantity (Count visible items strictly).
    4. Quantity Unit (e.g., pcs, kg, liter, bundle, packet).
    5. Typical Expiration: Estimate the typical expiration time in DAYS based on visual freshness (e.g., a brown banana has 1-2 days, fresh eggs 15-20 days, etc.). Use integer for single value.
    6. Sample Cost Per Unit: Estimate average market price per unit in Bangladeshi Taka (BDT) as a number.
    7. Unit: Same as quantity_unit (measurement unit).

    Return ONLY a JSON list. No markdown formatting, no code blocks, no plain text.
    
    Structure:
    [
        {
            "item_name": "string",
            "category": "string",
            "quantity": integer,
            "quantity_unit": "string",
            "typical_expiration_days": integer,
            "sample_cost_per_unit": number,
            "unit": "string"
        }
    ]
    """

    try:
        # 5. Generate Content
        response = model.generate_content([prompt, img])
        
        # 6. Clean and Parse JSON
        # Sometimes AI adds ```json at the start, we remove it.
        raw_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(raw_text)

        # 7. Output data (already in correct format)
        print(json.dumps(data, indent=4))

    except Exception as e:
        print(json.dumps({"error": f"AI Processing failed: {str(e)}"}))

if __name__ == "__main__":
    # Command line argument setup
    parser = argparse.ArgumentParser(description="Extract food info from image for Django Database")
    parser.add_argument("--image", type=str, required=True, help="Path to the food image file")
    
    args = parser.parse_args()
    
    if os.path.exists(args.image):
        analyze_image(args.image)
    else:
        print(json.dumps({"error": "File not found"}))