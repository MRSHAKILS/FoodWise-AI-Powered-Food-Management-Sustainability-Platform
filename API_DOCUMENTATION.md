# AI-Powered Food Management Platform - API Documentation

## Overview

This document describes all AI-powered API endpoints available in the Food Management & Sustainability Platform.

## Base URL

```
http://localhost:8000
```

## Authentication

All API endpoints require authentication. Include session cookie or JWT token in requests.

---

## AI Features API Endpoints

### 1. Consumption Pattern Analyzer

**Endpoint:** `POST /food/api/analyze/consumption/`

**Description:** Analyzes last 30 days of consumption data using AI to identify trends, detect over/under-consumption patterns, predict waste risks, and flag nutritional imbalances.

**Request:**

```json
POST /food/api/analyze/consumption/
Content-Type: application/json
Authorization: Session/JWT Token

No body required - automatically fetches user's consumption data
```

**Response:**

```json
{
  "success": true,
  "data": {
    "trends": [
      {
        "category": "vegetable",
        "avgConsumption": 2.5,
        "trend": "increasing"
      }
    ],
    "flags": [
      {
        "type": "over_consumption",
        "category": "snack",
        "severity": "medium",
        "message": "Snack consumption above recommended levels"
      }
    ],
    "wasteRisk": [
      {
        "itemId": "123",
        "itemName": "Milk",
        "riskScore": 85,
        "daysUntilWaste": 2
      }
    ],
    "insights": "Your vegetable consumption has increased by 15% this month..."
  },
  "period": {
    "start": "2025-10-21",
    "end": "2025-11-21",
    "total_logs": 45
  }
}
```

---

### 2. AI Meal Optimization Engine

**Endpoint:** `POST /food/api/optimize/meal-plan/`

**Description:** Generates optimized weekly meal plan based on budget, inventory, and dietary preferences using AI.

**Request:**

```json
POST /food/api/optimize/meal-plan/
Content-Type: application/json

{
  "budget": 100.00,
  "days": 7,
  "dietary_preferences": {
    "vegetarian": false,
    "allergies": ["nuts"],
    "min_protein": 50,
    "min_veggies": 5
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "mealPlan": [
      {
        "day": "Monday",
        "meals": [
          {
            "name": "Vegetable Stir Fry",
            "ingredients": ["broccoli", "carrots", "rice"],
            "cost": 5.5,
            "nutrients": {
              "protein": 12,
              "carbs": 45,
              "fat": 8
            }
          }
        ]
      }
    ],
    "shoppingList": [
      {
        "item": "Broccoli",
        "quantity": "500g",
        "estimatedCost": 3.5
      }
    ],
    "totalCost": 85.0,
    "wasteReduction": "Reduces waste by 25% by using expiring items",
    "nutritionScore": 82
  },
  "meal_plan_id": 42
}
```

---

### 3. NourishBot Chatbot

**Endpoint:** `POST /food/api/chat/nourish-bot/`

**Description:** Chat with AI assistant for food sustainability guidance, recipe suggestions, and waste reduction tips.

**Request:**

```json
POST /food/api/chat/nourish-bot/
Content-Type: application/json

{
  "message": "I have leftover rice, chicken, and broccoli. What can I make?",
  "session_id": "optional-uuid-for-continuing-conversation"
}
```

**Response:**

```json
{
  "success": true,
  "response": "Great ingredients! Here are 3 meal ideas:\n\n1. Chicken Fried Rice...",
  "session_id": "abc-123-def-456"
}
```

**Use Cases:**

- Recipe suggestions: "What can I make with [ingredients]?"
- Nutrition advice: "How can I increase my protein intake?"
- Waste reduction: "How do I reduce food waste?"
- Storage tips: "How should I store tomatoes?"

---

### 4. Waste Estimation Model

**Endpoint:** `GET /food/api/estimate/waste/`

**Description:** Get waste estimation metrics, projections, and comparison with community averages.

**Request:**

```
GET /food/api/estimate/waste/
```

**Response:**

```json
{
  "success": true,
  "data": {
    "currentWeek": {
      "totalWasteKg": 1.2,
      "totalWasteCost": 15.5,
      "itemsWasted": 3
    },
    "currentMonth": {
      "totalWasteKg": 4.8,
      "totalWasteCost": 62.0,
      "itemsWasted": 12,
      "wastePercentage": 8.5
    },
    "projection": {
      "nextMonthKg": 5.0,
      "trend": "stable"
    },
    "comparison": {
      "communityAverage": 30,
      "yourPerformance": 21.5,
      "message": "You're wasting 21.5% less than average"
    }
  }
}
```

---

### 5. SDG Impact Scoring

**Endpoint:** `GET /food/api/score/sdg/`

**Description:** Calculate user's SDG (Sustainable Development Goals) impact score with AI-generated insights.

**Request:**

```
GET /food/api/score/sdg/
```

**Response:**

```json
{
  "success": true,
  "data": {
    "totalScore": 78,
    "breakdown": {
      "wasteReduction": 85,
      "nutritionBalance": 72,
      "budgetEfficiency": 80,
      "communityEngagement": 65
    },
    "weeklyChange": 5,
    "insights": "Great progress! Your waste reduction improved by 10% this week...",
    "recommendations": [
      "Try meal planning to further reduce waste",
      "Increase variety in vegetable consumption",
      "Consider sharing surplus food with neighbors"
    ]
  }
}
```

**Score Components:**

- Waste Reduction (40%): Based on waste logs vs inventory
- Nutrition Balance (30%): Diversity and adequacy of consumption
- Budget Efficiency (20%): Cost optimization and value
- Community Engagement (10%): Food sharing activities

---

### 6. OCR Food Extraction

**Endpoint:** `POST /uploads/api/ocr/extract/`

**Description:** Extract food items from uploaded images (receipts, labels, groceries) using AI vision.

**Request:**

```
POST /uploads/api/ocr/extract/
Content-Type: multipart/form-data

Form Data:
- image: [file] (JPG, PNG image)
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully detected and added 5 food items to inventory",
  "upload_id": 123,
  "created_count": 5,
  "items": [
    {
      "id": 456,
      "name": "Banana",
      "quantity": 6.0,
      "unit": "pcs",
      "category": "fruit",
      "expiration_date": "2025-11-28",
      "price": 2.5
    }
  ]
}
```

---

## Dashboard & Recommendations (Part 6)

### 7. Dashboard Summary

**Endpoint:** `GET /food/api/dashboard/summary/`

**Description:** Get comprehensive dashboard statistics including inventory metrics, expiring items, and consumption stats.

**Response:**

```json
{
  "total_inventory_items": 25,
  "total_inventory_value": 150.5,
  "recent_logs_count": 12,
  "items_expiring_soon": 3,
  "expiring_items": [
    {
      "id": 123,
      "name": "Milk",
      "quantity": 1.0,
      "unit": "liter",
      "category": "dairy",
      "expiration_date": "2025-11-23",
      "days_left": 2,
      "urgency": "high"
    }
  ],
  "most_logged_category": "vegetable",
  "category_breakdown": [
    { "category": "vegetable", "count": 15, "percentage": 35.5 }
  ]
}
```

---

### 8. Resource Recommendations

**Endpoint:** `GET /food/api/recommendations/`

**Description:** Get personalized resource recommendations based on user's consumption patterns and goals.

**Response:**

```json
[
  {
    "resource": {
      "id": 1,
      "title": "10 Ways to Reduce Food Waste",
      "description": "...",
      "category": "waste_reduction",
      "category_display": "Waste Reduction",
      "type": "article",
      "url": "https://...",
      "tags": ["waste", "tips"],
      "read_time": 5
    },
    "reason": "You have 3 items expiring soon",
    "relevance_score": 95,
    "matched_rule": "expiring_items"
  }
]
```

---

## Error Responses

All endpoints return consistent error format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

---

## Rate Limiting

AI endpoints use Google Gemini API with following limits:

- **Free Tier**: 15 requests per minute (RPM), 1M tokens per minute
- Exceeded requests return 429 error
- Automatic retry with exponential backoff

---

## Caching

Certain endpoints use caching to improve performance:

- Consumption analysis: 30 minutes
- SDG scores: Calculated once per week
- Dashboard summary: 5 minutes

---

## Data Models

### MealPlan

```python
{
  "week_start_date": "2025-11-21",
  "meals_data": [...],
  "shopping_list": [...],
  "total_cost": 85.00,
  "budget_limit": 100.00,
  "nutrition_score": 82,
  "waste_reduction_estimate": "...",
  "generated_by": "AI"
}
```

### SDGScore

```python
{
  "score": 78,
  "waste_reduction_score": 85.0,
  "nutrition_score": 72.0,
  "budget_efficiency_score": 80.0,
  "community_engagement_score": 65.0,
  "insights": "...",
  "recommendations": [...],
  "week_number": 47,
  "year": 2025
}
```

### WasteLog

```python
{
  "item_name": "Tomatoes",
  "quantity": 3.0,
  "unit": "pcs",
  "category": "vegetable",
  "estimated_cost": 5.00,
  "reason": "expired",
  "waste_date": "2025-11-21",
  "notes": "..."
}
```

### ChatSession

```python
{
  "session_id": "abc-123-def-456",
  "messages": [
    {
      "role": "user",
      "content": "What can I cook?",
      "timestamp": "2025-11-21T10:30:00"
    },
    {
      "role": "assistant",
      "content": "Here are some ideas...",
      "timestamp": "2025-11-21T10:30:05"
    }
  ],
  "is_active": true
}
```

---

## Testing with cURL

### Example: Analyze Consumption

```bash
curl -X POST http://localhost:8000/food/api/analyze/consumption/ \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

### Example: Generate Meal Plan

```bash
curl -X POST http://localhost:8000/food/api/optimize/meal-plan/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"budget": 100, "days": 7, "dietary_preferences": {}}'
```

### Example: Chat with NourishBot

```bash
curl -X POST http://localhost:8000/food/api/chat/nourish-bot/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"message": "How can I reduce food waste?"}'
```

### Example: Upload Image for OCR

```bash
curl -X POST http://localhost:8000/uploads/api/ocr/extract/ \
  -F "image=@/path/to/food_image.jpg" \
  -b cookies.txt
```

---

## Integration Examples

### JavaScript/Fetch

```javascript
// Analyze consumption
const analyzeConsumption = async () => {
  const response = await fetch("/food/api/analyze/consumption/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    credentials: "include",
  });
  const data = await response.json();
  console.log(data);
};

// Generate meal plan
const generateMealPlan = async (budget) => {
  const response = await fetch("/food/api/optimize/meal-plan/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    credentials: "include",
    body: JSON.stringify({
      budget: budget,
      days: 7,
      dietary_preferences: {},
    }),
  });
  return await response.json();
};

// Chat with NourishBot
const chatWithBot = async (message, sessionId) => {
  const response = await fetch("/food/api/chat/nourish-bot/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    credentials: "include",
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
    }),
  });
  return await response.json();
};
```

### Python/Requests

```python
import requests

session = requests.Session()
session.cookies.update({'sessionid': 'your-session-id'})

# Analyze consumption
response = session.post(
    'http://localhost:8000/food/api/analyze/consumption/',
    json={}
)
data = response.json()

# Generate meal plan
response = session.post(
    'http://localhost:8000/food/api/optimize/meal-plan/',
    json={
        'budget': 100,
        'days': 7,
        'dietary_preferences': {}
    }
)
meal_plan = response.json()

# Chat with NourishBot
response = session.post(
    'http://localhost:8000/food/api/chat/nourish-bot/',
    json={
        'message': 'What should I cook tonight?'
    }
)
bot_response = response.json()
```

---

## Environment Variables Required

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

---

## Support & Troubleshooting

### Common Issues

**1. "GEMINI_API_KEY not found"**

- Add `GEMINI_API_KEY` to your `.env` file
- Restart Django server

**2. "Rate limit exceeded"**

- Free tier: 15 requests/minute
- Wait 1 minute before retrying
- Consider upgrading API tier

**3. "No consumption data found"**

- User needs at least 1 consumption log
- Add sample data for testing

**4. "OCR extraction failed"**

- Ensure image is clear and well-lit
- Supported formats: JPG, PNG
- Max file size: 10MB

---

## Changelog

### Version 2.0 (November 2025)

- Added AI Consumption Pattern Analyzer
- Added AI Meal Optimization Engine
- Added NourishBot Chatbot with function calling
- Added Waste Estimation Model
- Added SDG Impact Scoring System
- Added Gemini Vision OCR for food extraction
- Implemented rate limiting and caching
- Added comprehensive error handling

### Version 1.0 (October 2025)

- Basic food inventory management
- Consumption logging
- Dashboard and recommendations
- Food database
- Upload infrastructure

---

## License

Copyright © 2025 AI-Powered Food Management Platform
