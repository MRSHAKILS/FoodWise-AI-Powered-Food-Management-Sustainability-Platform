"""
Quick script to list available Gemini models for your API key
"""
import os
import google.generativeai as genai

# Load API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    print("Available Gemini Models:")
    print("=" * 60)
    
    try:
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"✓ {model.name}")
                print(f"  Display Name: {model.display_name}")
                print(f"  Description: {model.description[:100] if model.description else 'N/A'}...")
                print()
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("GEMINI_API_KEY not found in environment variables")
