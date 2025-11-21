{
  "instructions": {
    "projectContext": "AI-Powered Food Management & Sustainability Platform for SDG 2 & SDG 12. This is Part 2 of a hackathon project extending an existing food tracking platform with advanced AI features.",
    
    "coreObjectives": [
      "Analyze user consumption patterns and predict waste",
      "Optimize meal plans based on budget and inventory",
      "Provide AI-driven sustainability insights and chatbot assistance",
      "Generate personalized SDG impact analytics"
    ],

    "technicalStack": {
      "suggested": {
        "backend": "django",
        "frontend": "",
        "database": "sdlite",
        "aiServices": [
          "Google Gemini API (gemini-2.5-flash for all AI features)",
          "Gemini Vision for OCR and image analysis",
          "Simple rule-based models for predictions"
        ],
        "utilities": "Pandas for data analysis, Chart.js/Recharts for visualization",
        "geminiSDK": "google-generativeai (Python)"
      }
    },

    "featurePriority": {
      "phase1_critical": [
        "AI Consumption Pattern Analyzer",
        "AI Expiration Risk Prediction",
        "NourishBot Chatbot"
      ],
      "phase2_important": [
        "AI Meal Optimization Engine",
        "OCR Food Input",
        "SDG Impact Scoring"
      ],
      "phase3_bonus": [
        "AI Waste Estimation Model",
        "Local Food Sharing",
        "Nutrient Gap Prediction",
        "Admin Panel"
      ]
    },

    "codingGuidelines": {
      "architecture": [
        "Use modular structure with separate services for AI features",
        "Create reusable API endpoints for each AI capability",
        "Implement proper error handling and fallbacks for AI services",
        "Use environment variables for API keys (.env file)",
        "Include data validation on all inputs"
      ],
      
      "aiIntegration": [
        "For Gemini: Use generateContent API with system instructions for NourishBot",
        "Use gemini-1.5-pro for complex analysis, gemini-1.5-flash for faster responses",
        "Implement rate limiting and caching for API calls (Gemini free tier: 15 RPM, 1M TPM)",
        "Add fallback logic when AI services are unavailable",
        "Use streaming with generateContentStream for chatbot for better UX",
        "Store conversation context using Gemini's chat sessions or in database",
        "Use Gemini Vision API for OCR instead of separate vision service"
      ],

      "dataModels": {
        "userConsumption": {
          "fields": ["userId", "itemId", "quantity", "consumedDate", "category", "nutrients"],
          "indexes": ["userId", "consumedDate", "category"]
        },
        "inventory": {
          "fields": ["userId", "itemName", "quantity", "expirationDate", "addedDate", "category", "estimatedCost"],
          "indexes": ["userId", "expirationDate"]
        },
        "mealPlan": {
          "fields": ["userId", "weekStartDate", "meals", "totalCost", "nutritionScore", "generatedBy"],
          "computed": ["itemsUsed", "wasteReduction", "budgetSavings"]
        },
        "sdgScore": {
          "fields": ["userId", "score", "wasteReduced", "nutritionImproved", "calculatedDate", "insights"],
          "range": "0-100"
        }
      },

      "bestPractices": [
        "Use TypeScript for type safety (optional but recommended)",
        "Write unit tests for core AI logic functions",
        "Add JSDoc comments for complex functions",
        "Use async/await for all AI API calls",
        "Implement proper logging for debugging",
        "Create README with setup instructions and API documentation"
      ]
    },

    "featureImplementationGuides": {
      "1_consumptionPatternAnalyzer": {
        "description": "Analyze user food consumption trends and detect patterns",
        "implementation": [
          "Query last 30 days of user consumption data",
          "Group by category and day of week to find trends",
          "Calculate average consumption rates per category",
          "Detect anomalies (over/under consumption) using standard deviation",
          "Use LLM to generate natural language insights from data",
          "Return JSON with trends, flags, and recommendations"
        ],
        "samplePrompt": "Analyze this weekly consumption data: {data}. Identify: 1) High/low consumption patterns, 2) Days with most variety, 3) Over/under consumed categories, 4) Items likely to waste soon",
        "outputFormat": {
          "trends": "array of {category, avgConsumption, trend}",
          "flags": "array of {type, category, severity, message}",
          "predictions": "array of {itemId, wasteRisk, daysUntilWaste}",
          "heatmapData": "2D array for visualization"
        }
      },

      "2_mealOptimizationEngine": {
        "description": "Generate optimal weekly meal plans based on budget and inventory",
        "implementation": [
          "Fetch user's budget, dietary preferences, and current inventory",
          "Define minimum nutrition requirements (dummy: protein 50g, veggies 5 servings, etc.)",
          "Create meal combinations prioritizing inventory items near expiration",
          "Calculate costs using local price data (dummy dataset acceptable)",
          "Use LLM to suggest creative meal ideas with available items",
          "Generate shopping list for missing ingredients",
          "Optimize for: waste reduction > nutrition > budget"
        ],
        "algorithm": "1. FIFO for expiring items, 2. Rule-based nutrition balancing, 3. LLM for meal creativity, 4. Cost calculation and optimization",
        "outputFormat": {
          "mealPlan": "array of {day, meals: [{name, ingredients, cost, nutrients}]}",
          "shoppingList": "array of {item, quantity, estimatedCost}",
          "totalCost": "number",
          "nutritionSummary": "object with totals",
          "wasteReduction": "percentage or grams saved"
        }
      },

      "3_ocrFoodInput": {
        "description": "Extract food information from uploaded images using Gemini Vision",
        "implementation": [
          "Accept image upload (receipt, label, grocery list)",
          "Use Gemini Vision API (gemini-1.5-pro-vision or gemini-1.5-flash-vision)",
          "Convert image to base64 or pass file directly to Gemini",
          "Create structured prompt: 'Extract food items with quantities and expiration dates from this image. Return as JSON: [{itemName, quantity, expiryDate}]'",
          "Use JSON mode or request structured output in prompt",
          "Parse response and validate data structure",
          "Show confirmation UI for user to verify/edit extracted data"
        ],
        "geminiPrompt": "Analyze this image of food items, grocery receipt, or product label. Extract and return ONLY a JSON array with this structure: [{\"itemName\": \"string\", \"quantity\": \"string with unit\", \"expiryDate\": \"YYYY-MM-DD or null\"}]. If expiration date is not visible, set to null. Be precise with item names.",
        "libraries": ["@google/generative-ai", "multer for uploads", "sharp for image preprocessing"],
        "fallback": "If extraction confidence seems low, prompt user for manual entry"
      },

      "4_expirationRiskPrediction": {
        "description": "Predict which items are at risk of expiring",
        "implementation": [
          "Calculate days until expiration for each inventory item",
          "Analyze consumption frequency: items consumed < once/week = high risk",
          "Apply category rules: fruits/veggies expire faster (1-7 days), canned goods slower (30+ days)",
          "Consider seasonal factors (dummy: warm season = faster spoilage)",
          "Generate risk score: 0-100 based on time + consumption + category",
          "Sort items by risk score (highest first)",
          "Create alerts for items with risk > 70"
        ],
        "formula": "riskScore = (100 - daysUntilExpiry * 10) + (50 if lowConsumption) + (20 if perishableCategory) + (10 if warmSeason)",
        "outputFormat": {
          "highRiskItems": "array of {itemId, name, riskScore, daysLeft, recommendedAction}",
          "alerts": "array of alert messages"
        }
      },

      "5_wasteEstimationModel": {
        "description": "Estimate food waste based on user patterns",
        "implementation": [
          "Track items that expired without full consumption",
          "Calculate waste = quantity * cost for expired items",
          "Aggregate by week and month",
          "Compare to dummy community averages (e.g., avg household wastes 30% of food)",
          "Use simple predictive formula: futureWaste = avgWeeklyWaste * 4",
          "Optionally: use ML model (linear regression) on historical data",
          "Generate insights: 'You wasted 15% less than last month'"
        ],
        "metrics": ["totalWasteGrams", "totalWasteCost", "wastePercentage", "trendVsPreviousPeriod"],
        "outputFormat": {
          "currentWeek": "waste stats",
          "currentMonth": "waste stats",
          "projection": "next month estimate",
          "comparison": "vs community average"
        }
      },

      "6_nourishBotChatbot": {
        "description": "Multi-capability AI chatbot using Gemini for food sustainability guidance",
        "implementation": [
          "Use Gemini's generateContent API with system instructions",
          "Initialize chat session: model.startChat() with history for context",
          "System instruction includes: SDG goals, food waste tips, nutrition guidelines, budget strategies",
          "Implement function calling with Gemini's tool/function declarations",
          "Define tools: getUserInventory(), getConsumptionHistory(), generateMealIdeas()",
          "Maintain conversation context using Gemini's built-in chat history (last 10-20 messages)",
          "Handle queries: 'How can I use leftover chicken?', 'Nutrition tips?', 'Reduce my waste?'",
          "Use generateContentStream for real-time streaming responses"
        ],
        "systemInstruction": "You are NourishBot, an AI assistant helping users reduce food waste, improve nutrition, and make sustainable food choices aligned with UN SDG 2 (Zero Hunger) and SDG 12 (Responsible Consumption). You have access to the user's food inventory, consumption history, and waste data through function calls. Provide practical, friendly, and actionable advice. Always suggest specific recipes when users ask about using ingredients.",
        "tools": [
          {
            "name": "getUserInventory",
            "description": "Get user's current food inventory with expiration dates",
            "parameters": {"type": "object", "properties": {"userId": {"type": "string"}}}
          },
          {
            "name": "getConsumptionHistory",
            "description": "Get user's food consumption history for analysis",
            "parameters": {"type": "object", "properties": {"userId": {"type": "string"}, "days": {"type": "number"}}}
          },
          {
            "name": "generateMealIdeas",
            "description": "Generate meal ideas using specific ingredients",
            "parameters": {"type": "object", "properties": {"ingredients": {"type": "array", "items": {"type": "string"}}}}
          }
        ],
        "outputFormat": "text response with optional structured actions"
      },

      "7_sdgImpactScoring": {
        "description": "Calculate user's SDG impact score and provide insights",
        "implementation": [
          "Define scoring components: wasteReduction (40%), nutritionBalance (30%), budgetEfficiency (20%), communitySharing (10%)",
          "Calculate wasteReduction: compare current vs baseline waste percentage",
          "Calculate nutritionBalance: check if meeting minimum requirements across categories",
          "Calculate budgetEfficiency: actual spend vs recommended spend for nutrition level",
          "Use weighted average for final score (0-100)",
          "Generate weekly progress report with LLM insights",
          "Provide actionable recommendations to improve score"
        ],
        "formula": "score = (wasteReduction * 0.4) + (nutritionScore * 0.3) + (budgetScore * 0.2) + (sharingScore * 0.1)",
        "outputFormat": {
          "totalScore": "number 0-100",
          "breakdown": "scores per category",
          "weeklyChange": "+/-X points",
          "insights": "natural language summary",
          "recommendations": "array of actionable next steps"
        }
      }
    },

    "bonusFeatureGuides": {
      "localFoodSharing": {
        "description": "Connect users to local food surplus opportunities",
        "implementation": [
          "Create listings model: {location, foodItems, quantity, expiryDate, contactInfo}",
          "Implement simple matching: users within X km radius",
          "Add map view using Leaflet or Google Maps",
          "Allow users to post surplus food they can't consume",
          "Show distance and availability status"
        ]
      },
      
      "nutrientGapPrediction": {
        "description": "Predict likely nutrient deficiencies from consumption patterns",
        "implementation": [
          "Define daily nutrient requirements (dummy: Protein 50g, Vitamin C 90mg, Iron 18mg, etc.)",
          "Aggregate user's weekly nutrient intake",
          "Compare to requirements, flag gaps > 20% below target",
          "Use LLM to suggest specific foods to fill gaps",
          "Generate personalized meal suggestions"
        ]
      },

      "adminPanel": {
        "description": "Admin dashboard for data management and analytics",
        "implementation": [
          "Protected routes with admin authentication",
          "CRUD operations for: food items, categories, nutrients",
          "Analytics: active users, most wasted items, nutrition trends",
          "Charts using Chart.js or Recharts",
          "Export data as CSV"
        ]
      },

      "multiLanguageSupport": {
        "description": "Add internationalization (i18n)",
        "implementation": [
          "Use i18next or react-intl library",
          "Create translation files: en.json, es.json, etc.",
          "Translate: UI labels, button text, error messages",
          "Add language selector in settings",
          "Store user preference in database"
        ]
      }
    },

    "examplePrompts": {
      "forConsumptionAnalysis": "Based on this user's food consumption data over the last 30 days: {data}, identify weekly trends, detect over/under-consumption patterns, predict items likely to be wasted in the next week, and flag any nutritional imbalances.",
      
      "forMealOptimization": "Create a weekly meal plan for a user with a $50 budget. Current inventory: {items}. Dietary requirements: {requirements}. Prioritize using items expiring within 5 days. Ensure balanced nutrition and minimize waste. Provide meal names, ingredients, and a shopping list.",
      
      "forNourishBot": "User asks: 'I have leftover rice, chicken, and broccoli. What can I make for dinner that's healthy and won't let these ingredients go to waste?' Provide 2-3 creative meal ideas with brief preparation instructions.",
      
      "forSDGInsights": "Analyze this user's sustainability progress: waste reduced by 25%, nutrition score 78/100, budget efficiency 85%. Generate a motivating weekly insight message highlighting their achievements and provide one actionable tip to improve their score."
    },

    "apiEndpointSuggestions": [
      "POST /api/analyze/consumption - Analyze consumption patterns",
      "POST /api/optimize/meal-plan - Generate optimized meal plan",
      "POST /api/ocr/extract - Extract food data from image",
      "GET /api/predict/expiration-risks - Get high-risk items",
      "GET /api/estimate/waste - Get waste estimation and projections",
      "POST /api/chat/nourish-bot - Chat with NourishBot",
      "GET /api/score/sdg - Get user's SDG impact score",
      "POST /api/share/surplus - Create food sharing listing (bonus)",
      "GET /api/predict/nutrient-gaps - Predict nutrient deficiencies (bonus)"
    ],

    "environmentVariables": {
      "required": [
        "GEMINI_API_KEY",
        "DATABASE_URL",
        "JWT_SECRET"
      ],
      "optional": [
        "MAPS_API_KEY",
        "REDIS_URL (for caching)"
      ]
    },

    "testingStrategy": [
      "Unit tests for utility functions (risk calculation, waste estimation)",
      "Integration tests for API endpoints",
      "Mock AI API responses for consistent testing",
      "Test edge cases: empty inventory, extreme budgets, missing data",
      "Load test chatbot with concurrent requests"
    ],

    "documentationRequirements": [
      "README with: project overview, setup instructions, API documentation",
      "List all external APIs/services used with links",
      "Include .env.example file with required variables",
      "Add inline comments for complex AI logic",
      "Create ARCHITECTURE.md explaining system design"
    ],

    "commonPitfalls": [
      "Don't overuse AI - simple rules work better for some features",
      "Handle API failures gracefully with fallbacks",
      "Don't expose API keys in frontend code",
      "Validate and sanitize all user inputs",
      "Consider rate limits on AI API calls",
      "Test with realistic data, not just perfect scenarios",
      "Don't forget to handle image size limits for OCR"
    ],

    "timeManagement": {
      "hour_0_2": "Set up AI API integrations, test basic calls",
      "hour_2_5": "Implement core features: analyzer, expiration prediction, chatbot",
      "hour_5_7": "Build meal optimization and OCR features",
      "hour_7_9": "Implement SDG scoring and one bonus feature",
      "hour_9_10": "Testing, bug fixes, documentation, polish UI"
    },

    "promptTemplatesForCopilot": {
      "consumptionAnalyzer": "// Create a function that analyzes user consumption data for the last 30 days, identifies weekly trends by category, detects over/under consumption using statistical methods, predicts items at risk of waste, and returns structured JSON with insights",
      
      "mealOptimizer": "// Build a meal optimization engine that takes user budget, inventory, and dietary needs, generates a weekly meal plan prioritizing expiring items, ensures minimum nutrition requirements, calculates total cost, and returns meal schedule with shopping list",
      
      "ocrExtractor": "// Implement OCR functionality to extract food items from uploaded images, parse text for item names, quantities, and expiration dates using regex, structure the data, and return with confidence scores for user verification",
      
      "chatbotHandler": "// Create a Gemini-powered chatbot using startChat() that handles food waste reduction queries, maintains conversation context through chat history, has access to user inventory through function calling, and provides practical sustainability advice aligned with SDG goals. Use generateContentStream for real-time responses.",
      
      "sdgScorer": "// Build an SDG impact scoring system that calculates user scores based on waste reduction (40%), nutrition balance (30%), budget efficiency (20%), and community sharing (10%), generates weekly insights, and provides actionable recommendations"
    },

    "geminiImplementationExamples": {
      "setup": {
        "node": "const { GoogleGenerativeAI } = require('@google/generative-ai');\nconst genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);\nconst model = genAI.getGenerativeModel({ model: 'gemini-1.5-pro' });",
        "python": "import google.generativeai as genai\ngenai.configure(api_key=os.environ['GEMINI_API_KEY'])\nmodel = genai.GenerativeModel('gemini-1.5-pro')"
      },

      "consumptionAnalysis": {
        "node": "async function analyzeConsumption(consumptionData) {\n  const prompt = `Analyze this 30-day food consumption data: ${JSON.stringify(consumptionData)}.\n  \n  Identify:\n  1. Weekly consumption trends by category\n  2. Over/under-consumption patterns\n  3. Items likely to waste in next 7 days\n  4. Nutritional imbalances\n  \n  Return response as JSON with structure:\n  {\n    \"trends\": [{\"category\": string, \"avgConsumption\": number, \"trend\": \"increasing|decreasing|stable\"}],\n    \"flags\": [{\"type\": string, \"category\": string, \"severity\": \"high|medium|low\", \"message\": string}],\n    \"wasteRisk\": [{\"itemId\": string, \"itemName\": string, \"riskScore\": number, \"daysUntilWaste\": number}]\n  }`;\n  \n  const result = await model.generateContent(prompt);\n  const response = result.response.text();\n  return JSON.parse(response.replace(/```json\\n?|```/g, ''));\n}",
        "python": "async def analyze_consumption(consumption_data):\n    prompt = f\"\"\"Analyze this 30-day food consumption data: {json.dumps(consumption_data)}.\n    \n    Return ONLY valid JSON with this structure:\n    {{\n      \"trends\": [{{\"category\": str, \"avgConsumption\": float, \"trend\": str}}],\n      \"flags\": [{{\"type\": str, \"category\": str, \"severity\": str, \"message\": str}}],\n      \"wasteRisk\": [{{\"itemId\": str, \"itemName\": str, \"riskScore\": int, \"daysUntilWaste\": int}}]\n    }}\"\"\"\n    \n    response = model.generate_content(prompt)\n    return json.loads(response.text.strip('```json\\n').strip('```'))"
      },

      "mealOptimization": {
        "node": "async function optimizeMealPlan(budget, inventory, dietaryNeeds) {\n  const prompt = `Create a weekly meal plan:\n  Budget: ${budget}\n  Current Inventory: ${JSON.stringify(inventory)}\n  Dietary Requirements: ${JSON.stringify(dietaryNeeds)}\n  \n  Rules:\n  - Prioritize items expiring within 5 days\n  - Ensure minimum: 50g protein/day, 5 veggie servings/day\n  - Stay within budget\n  - Minimize waste\n  \n  Return JSON:\n  {\n    \"mealPlan\": [{\"day\": string, \"meals\": [{\"name\": string, \"ingredients\": [string], \"cost\": number, \"nutrients\": {}}]}],\n    \"shoppingList\": [{\"item\": string, \"quantity\": string, \"estimatedCost\": number}],\n    \"totalCost\": number,\n    \"wasteReduction\": string\n  }`;\n  \n  const result = await model.generateContent(prompt);\n  return JSON.parse(result.response.text().replace(/```json\\n?|```/g, ''));\n}",
        "python": "async def optimize_meal_plan(budget, inventory, dietary_needs):\n    prompt = f\"\"\"Create optimal weekly meal plan.\n    Budget: ${budget}\n    Inventory: {json.dumps(inventory)}\n    Requirements: {json.dumps(dietary_needs)}\n    \n    Return ONLY valid JSON with meal plan structure.\"\"\"\n    \n    response = model.generate_content(prompt)\n    return json.loads(response.text.strip('```json\\n').strip('```'))"
      },

      "ocrWithGeminiVision": {
        "node": "async function extractFoodFromImage(imagePath) {\n  const visionModel = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });\n  \n  const imageData = fs.readFileSync(imagePath).toString('base64');\n  const imagePart = {\n    inlineData: {\n      data: imageData,\n      mimeType: 'image/jpeg'\n    }\n  };\n  \n  const prompt = `Extract food items from this image (receipt, label, or grocery list).\n  \n  Return ONLY a JSON array:\n  [{\n    \"itemName\": string,\n    \"quantity\": string (with unit),\n    \"expiryDate\": string (YYYY-MM-DD) or null\n  }]\n  \n  Be precise with item names. If no expiration date visible, use null.`;\n  \n  const result = await visionModel.generateContent([prompt, imagePart]);\n  const response = result.response.text();\n  return JSON.parse(response.replace(/```json\\n?|```/g, ''));\n}",
        "python": "async def extract_food_from_image(image_path):\n    vision_model = genai.GenerativeModel('gemini-1.5-flash')\n    \n    image = PIL.Image.open(image_path)\n    \n    prompt = \"\"\"Extract food items from this image.\n    Return ONLY JSON array: [{\"itemName\": str, \"quantity\": str, \"expiryDate\": str or null}]\"\"\"\n    \n    response = vision_model.generate_content([prompt, image])\n    return json.loads(response.text.strip('```json\\n').strip('```'))"
      },

      "chatbotWithFunctionCalling": {
        "node": "const tools = [\n  {\n    functionDeclarations: [\n      {\n        name: 'getUserInventory',\n        description: 'Get current food inventory for the user',\n        parameters: {\n          type: 'object',\n          properties: {\n            userId: { type: 'string', description: 'User ID' }\n          },\n          required: ['userId']\n        }\n      },\n      {\n        name: 'generateMealIdeas',\n        description: 'Generate meal ideas using specific ingredients',\n        parameters: {\n          type: 'object',\n          properties: {\n            ingredients: {\n              type: 'array',\n              items: { type: 'string' },\n              description: 'List of available ingredients'\n            }\n          },\n          required: ['ingredients']\n        }\n      }\n    ]\n  }\n];\n\nconst chatModel = genAI.getGenerativeModel({\n  model: 'gemini-1.5-pro',\n  systemInstruction: 'You are NourishBot, helping users reduce food waste and improve nutrition aligned with UN SDG 2 and 12. Provide practical, friendly advice.',\n  tools: tools\n});\n\nasync function chatWithNourishBot(userMessage, chatHistory) {\n  const chat = chatModel.startChat({\n    history: chatHistory\n  });\n  \n  const result = await chat.sendMessageStream(userMessage);\n  \n  let fullResponse = '';\n  for await (const chunk of result.stream) {\n    fullResponse += chunk.text();\n    // Stream to frontend in real-time\n  }\n  \n  // Check for function calls\n  const response = await result.response;\n  const functionCall = response.functionCall();\n  \n  if (functionCall) {\n    // Execute the function\n    const functionResult = await executeFunctionCall(functionCall);\n    \n    // Send function result back to model\n    const functionResponse = await chat.sendMessage([{\n      functionResponse: {\n        name: functionCall.name,\n        response: functionResult\n      }\n    }]);\n    \n    return functionResponse.response.text();\n  }\n  \n  return fullResponse;\n}",
        "python": "tools = [\n    genai.protos.Tool(\n        function_declarations=[\n            genai.protos.FunctionDeclaration(\n                name='get_user_inventory',\n                description='Get current food inventory',\n                parameters={'type': 'object', 'properties': {'userId': {'type': 'string'}}}\n            )\n        ]\n    )\n]\n\nchat_model = genai.GenerativeModel(\n    model_name='gemini-1.5-pro',\n    system_instruction='You are NourishBot...',\n    tools=tools\n)\n\nasync def chat_with_nourish_bot(user_message, chat_history):\n    chat = chat_model.start_chat(history=chat_history)\n    response = chat.send_message(user_message)\n    \n    # Handle function calls if any\n    if response.candidates[0].content.parts[0].function_call:\n        function_call = response.candidates[0].content.parts[0].function_call\n        result = await execute_function(function_call)\n        \n        # Send result back\n        response = chat.send_message(\n            genai.protos.Content(\n                parts=[genai.protos.Part(\n                    function_response=genai.protos.FunctionResponse(\n                        name=function_call.name,\n                        response={'result': result}\n                    )\n                )]\n            )\n        )\n    \n    return response.text"
      },

      "structuredOutputWithJSON": {
        "node": "// Force JSON output for consistent parsing\nconst model = genAI.getGenerativeModel({\n  model: 'gemini-1.5-pro',\n  generationConfig: {\n    responseMimeType: 'application/json',\n    responseSchema: {\n      type: 'object',\n      properties: {\n        trends: {\n          type: 'array',\n          items: {\n            type: 'object',\n            properties: {\n              category: { type: 'string' },\n              avgConsumption: { type: 'number' },\n              trend: { type: 'string' }\n            }\n          }\n        },\n        flags: { type: 'array' }\n      }\n    }\n  }\n});\n\nconst result = await model.generateContent(prompt);\nconst data = JSON.parse(result.response.text()); // Guaranteed valid JSON",
        "note": "Use responseSchema for guaranteed structured output - no need to strip markdown"
      },

      "errorHandlingAndFallback": {
        "node": "async function callGeminiWithFallback(prompt, retries = 3) {\n  for (let i = 0; i < retries; i++) {\n    try {\n      const result = await model.generateContent(prompt);\n      return result.response.text();\n    } catch (error) {\n      if (error.message.includes('RATE_LIMIT')) {\n        // Wait and retry\n        await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1)));\n        continue;\n      }\n      if (i === retries - 1) {\n        // Use rule-based fallback\n        console.error('Gemini API failed, using fallback:', error);\n        return rulBasedFallback(prompt);\n      }\n    }\n  }\n}"
      }
    }
  }
}