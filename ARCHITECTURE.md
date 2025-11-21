# AI-Powered Food Management Platform - Architecture

## System Overview

This platform combines traditional food inventory management with advanced AI capabilities to help users reduce food waste, optimize nutrition, and achieve UN Sustainable Development Goals (SDG 2 & SDG 12).

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  (Django Templates + Tailwind CSS + JavaScript)             │
├─────────────────────────────────────────────────────────────┤
│                     Django Views Layer                       │
│  • food/views.py        - AI API endpoints                  │
│  • uploads/views.py     - OCR processing                    │
│  • users/views.py       - Authentication                    │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ AI Services  │  │ Utilities    │  │ Predictors   │     │
│  │ Module       │  │ Module       │  │ Module       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                      Data Layer                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Django ORM + SQLite/PostgreSQL                       │  │
│  │ • FoodItem  • ConsumptionLog  • MealPlan            │  │
│  │ • SDGScore  • WasteLog        • ChatSession         │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                  External Services Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Google       │  │ Google       │  │ Redis        │     │
│  │ Gemini API   │  │ OAuth2       │  │ (Caching)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. AI Services Module (`food/ai_services.py`)

**Purpose**: Centralized AI integration layer providing reusable Gemini API functions.

**Key Features**:

- Rate limiting (15 RPM for free tier)
- Error handling with exponential backoff
- Response caching (30 min for analysis, per-week for scores)
- JSON parsing with markdown cleanup
- Fallback to rule-based logic when AI unavailable

**Main Class**:

```python
class GeminiService:
    - __init__(model_name='gemini-2.0-flash-exp')
    - generate_content(prompt, temperature, expect_json, cache_key)
    - generate_with_images(prompt, images)
    - _check_rate_limit()
    - _parse_json_response(text)
```

**Convenience Functions**:

- `analyze_consumption_patterns()`
- `generate_meal_plan()`
- `chat_with_nourish_bot()`
- `calculate_sdg_score()`
- `extract_food_from_image()`

### 2. Data Models

#### Core Food Models

```python
FoodItem
├─ user: ForeignKey(User)
├─ name, quantity, unit, category
├─ purchase_date, expiration_date, price
├─ Properties: is_expired, days_until_expiration, is_expiring_soon
└─ Methods: __str__

ConsumptionLog
├─ user, item_name, quantity, unit, category
├─ consumption_date, notes
└─ Tracks daily food usage

FoodItemDatabase
├─ Master database of common food items
├─ typical_expiration_days, sample_cost_per_unit
├─ nutritional_info (JSON), storage_instructions
└─ Used for quick item addition
```

#### AI-Powered Models

```python
MealPlan
├─ user, week_start_date
├─ meals_data (JSON): daily meal schedule
├─ shopping_list (JSON): required ingredients
├─ total_cost, budget_limit, nutrition_score
├─ waste_reduction_estimate
└─ generated_by: 'AI' | 'Manual'

SDGScore
├─ user, score (0-100)
├─ Breakdown: waste_reduction, nutrition, budget, community
├─ Metrics: waste_reduced_kg, waste_cost_saved
├─ AI insights and recommendations (JSON)
├─ week_number, year
└─ Unique per user per week

WasteLog
├─ user, item_name, quantity, category
├─ estimated_cost, reason (expired/spoiled/excess)
├─ waste_date, notes
└─ Used for waste estimation and SDG scoring

ChatSession
├─ user, session_id (UUID)
├─ messages (JSON): [{role, content, timestamp}]
├─ context_data (JSON): user's inventory snapshot
├─ is_active
└─ Methods: add_message(role, content)
```

### 3. API Endpoints Architecture

#### Pattern: RESTful JSON APIs with Django Views

All AI endpoints follow this pattern:

```python
@login_required
@require_http_methods(["POST"])
def ai_endpoint(request):
    try:
        # 1. Parse input
        data = json.loads(request.body)

        # 2. Validate & fetch user data
        user_data = fetch_user_context(request.user)

        # 3. Call AI service
        result = ai_service_function(user_data, data)

        # 4. Fallback if AI fails
        if not result:
            result = rule_based_fallback(user_data)

        # 5. Save to database if needed
        save_result_to_db(result)

        # 6. Return JSON response
        return JsonResponse({'success': True, 'data': result})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
```

#### Endpoint Summary

| Endpoint                         | Method | Purpose          | AI Model             |
| -------------------------------- | ------ | ---------------- | -------------------- |
| `/food/api/analyze/consumption/` | POST   | Pattern analysis | gemini-2.0-flash-exp |
| `/food/api/optimize/meal-plan/`  | POST   | Meal planning    | gemini-2.0-flash-exp |
| `/food/api/chat/nourish-bot/`    | POST   | Chatbot          | gemini-exp-1206      |
| `/food/api/estimate/waste/`      | GET    | Waste metrics    | Rule-based           |
| `/food/api/score/sdg/`           | GET    | SDG scoring      | gemini-2.0-flash-exp |
| `/uploads/api/ocr/extract/`      | POST   | Image OCR        | gemini-2.0-flash-exp |

### 4. AI Integration Strategy

#### Model Selection

- **gemini-2.0-flash-exp**: Latest experimental flash model - fast, cost-effective for analysis, meal planning, OCR
- **gemini-exp-1206**: Latest experimental model - better reasoning for chatbot, complex queries
- **gemini-1.5-flash**: Stable fallback option

#### Prompt Engineering Patterns

**1. Consumption Analysis Prompt**

```
Analyze this 30-day food consumption data: {data}
Identify:
1. Weekly trends by category
2. Over/under-consumption patterns
3. Items likely to waste
4. Nutritional imbalances

Return JSON: {trends, flags, wasteRisk, insights}
```

**2. Meal Planning Prompt**

```
Create {days}-day meal plan:
Budget: ${budget}
Inventory: {items}
Requirements: {dietary_needs}

Rules:
- Prioritize items expiring within 5 days
- Ensure min nutrition
- Stay within budget
- Minimize waste

Return JSON: {mealPlan, shoppingList, totalCost, wasteReduction}
```

**3. Chatbot System Instruction**

```
You are NourishBot, helping users reduce food waste and
improve nutrition aligned with UN SDG 2 & 12.
Provide practical, friendly advice.
Context: {user_inventory, recent_consumption, budget}
```

**4. OCR Vision Prompt**

```
Analyze this food image (receipt/label/groceries).
Extract items with: name, quantity, category, expiry date.
Return JSON array: [{itemName, quantity, expiryDate, category}]
Be precise. If no expiry visible, set null.
```

#### Error Handling & Fallbacks

```python
# Retry with exponential backoff
for attempt in range(retry_count):
    try:
        result = gemini_api_call()
        return result
    except RateLimitError:
        wait_time = 2 ** attempt
        time.sleep(wait_time)
    except APIError:
        if attempt == retry_count - 1:
            return rule_based_fallback()
```

**Fallback Strategies**:

1. **Consumption Analysis**: Simple category counting, basic stats
2. **Meal Planning**: Template-based plans with inventory substitution
3. **Chatbot**: Predefined responses for common queries
4. **SDG Score**: Formula-based calculation without AI insights

### 5. Caching Strategy

#### Cache Keys & TTL

```python
# Consumption analysis - 30 minutes
cache_key = f"consumption_analysis:{hash(data)}"
cache_timeout = 1800

# SDG scores - Calculated once per week
unique_together = ['user', 'year', 'week_number']

# Dashboard summary - 5 minutes
cache.set('dashboard_summary:{user_id}', data, 300)

# Chat sessions - No caching
# Responses must be real-time
```

#### Cache Backend

- Django's default cache (MemCache/Redis recommended)
- Redis preferred for production (SESSION + CACHE)

### 6. Rate Limiting Implementation

```python
class GeminiService:
    RATE_LIMIT_WINDOW = 60  # seconds
    MAX_REQUESTS_PER_WINDOW = 15

    def _check_rate_limit(self):
        cache_key = f"gemini_rate_limit:requests"
        current_count = cache.get(cache_key, 0)

        if current_count >= self.MAX_REQUESTS_PER_WINDOW:
            return False

        cache.set(cache_key, current_count + 1, self.RATE_LIMIT_WINDOW)
        return True
```

**Free Tier Limits**:

- 15 requests per minute (RPM)
- 1M tokens per minute (TPM)
- Automatic exponential backoff on 429 errors

### 7. Security Considerations

#### API Key Management

```python
# .env file (never commit)
GEMINI_API_KEY=your_key_here

# settings.py
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ai_services.py
genai.configure(api_key=GEMINI_API_KEY)
```

#### Input Validation

- Sanitize all user inputs before AI prompts
- Validate JSON structures
- Limit input sizes (max 10MB for images)
- Escape special characters

#### Output Sanitization

- Parse and validate AI responses
- Remove markdown code blocks
- Validate JSON schemas
- Handle malformed responses gracefully

#### Authentication

- All AI endpoints require `@login_required`
- Session-based authentication
- CSRF protection enabled
- Rate limiting per user

### 8. Database Schema Relationships

```
User (Django Auth)
  ├── FoodItem (1:N) - Inventory
  ├── ConsumptionLog (1:N) - Daily usage
  ├── MealPlan (1:N) - Generated plans
  ├── SDGScore (1:N) - Weekly scores
  ├── WasteLog (1:N) - Waste tracking
  ├── ChatSession (1:N) - Bot conversations
  └── Upload (1:N) - Image uploads

FoodItemDatabase (Global)
  └── Reference data for all users

Upload
  ├── associated_inventory (FK to FoodItem)
  └── associated_log (FK to ConsumptionLog)
```

### 9. Performance Optimization

#### Query Optimization

```python
# Use select_related for foreign keys
items = FoodItem.objects.select_related('user').filter(...)

# Use prefetch_related for reverse relationships
users = User.objects.prefetch_related('food_items', 'consumption_logs')

# Index frequently queried fields
class Meta:
    indexes = [
        models.Index(fields=['user', 'expiration_date']),
        models.Index(fields=['consumption_date']),
    ]
```

#### Response Compression

- Enable gzip compression in production
- Use pagination for large datasets
- Lazy load images and heavy content

#### Asynchronous Processing

```python
# Future enhancement: Use Celery for long-running tasks
@shared_task
def generate_meal_plan_async(user_id, params):
    result = generate_meal_plan(params)
    notify_user(user_id, result)
```

### 10. Testing Strategy

#### Unit Tests

```python
# Test AI service functions with mocked responses
@mock.patch('google.generativeai.GenerativeModel')
def test_consumption_analysis(mock_model):
    mock_model.generate_content.return_value = mock_response
    result = analyze_consumption_patterns(test_data)
    assert result['success'] == True
```

#### Integration Tests

```python
# Test API endpoints
def test_analyze_consumption_api(client, user):
    client.force_login(user)
    response = client.post('/food/api/analyze/consumption/')
    assert response.status_code == 200
    assert 'data' in response.json()
```

#### Load Tests

- Test rate limiting under high concurrency
- Verify cache effectiveness
- Monitor API quota usage

### 11. Deployment Architecture

#### Development

```
Django Dev Server (runserver)
  ├── SQLite database
  ├── Local file storage (media/)
  └── Django cache (memory)
```

#### Production (Recommended)

```
Nginx (Reverse Proxy)
  ├── Gunicorn/uWSGI (Django App Server)
  │     ├── PostgreSQL (Database)
  │     ├── Redis (Cache + Sessions)
  │     └── AWS S3/Cloudinary (Media Storage)
  ├── Static Files (CDN)
  └── SSL/TLS Certificate
```

#### Environment Variables (Production)

```bash
DEBUG=False
SECRET_KEY=long_random_string
DATABASE_URL=postgres://...
REDIS_URL=redis://...
GEMINI_API_KEY=your_key
AWS_STORAGE_BUCKET_NAME=...
ALLOWED_HOSTS=yourdomain.com
```

### 12. Monitoring & Logging

#### Logging Configuration

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'ai_services.log',
        },
    },
    'loggers': {
        'food.ai_services': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

#### Metrics to Track

- AI API call success/failure rates
- Response times per endpoint
- Cache hit/miss ratios
- Rate limit violations
- User engagement with AI features
- SDG score trends over time

### 13. Future Enhancements

#### Short-term (3-6 months)

- [ ] Nutrient gap prediction
- [ ] Local food sharing marketplace
- [ ] Advanced meal plan customization
- [ ] Multi-language support (i18n)
- [ ] Mobile app (React Native/Flutter)

#### Long-term (6-12 months)

- [ ] Computer vision for automatic portion detection
- [ ] Voice assistant integration
- [ ] Community challenges and gamification
- [ ] Blockchain for food provenance tracking
- [ ] Integration with smart kitchen appliances
- [ ] Machine learning for personalized recommendations

### 14. Technology Stack Summary

| Layer          | Technology                  | Purpose               |
| -------------- | --------------------------- | --------------------- |
| Backend        | Django 5.2                  | Web framework         |
| Database       | SQLite/PostgreSQL           | Data persistence      |
| Cache          | Django Cache/Redis          | Performance           |
| Frontend       | Django Templates + Tailwind | UI                    |
| AI             | Google Gemini API           | NLP, Vision, Analysis |
| Authentication | Django Auth + Allauth       | User management       |
| File Storage   | Django Media/S3             | Image uploads         |
| Task Queue     | Celery (future)             | Async processing      |
| Monitoring     | Django Debug Toolbar        | Development           |

### 15. API Design Principles

1. **Consistency**: All endpoints return `{success, data/error}` format
2. **RESTful**: Use appropriate HTTP methods (GET, POST, PUT, DELETE)
3. **Versioning**: Future-proof with `/api/v1/` prefix (planned)
4. **Documentation**: OpenAPI/Swagger spec (planned)
5. **Rate Limiting**: Enforce limits at application level
6. **Error Handling**: Descriptive error messages with codes
7. **Authentication**: Session-based with JWT option (planned)
8. **Pagination**: For large datasets (planned)

---

## Conclusion

This architecture provides a scalable, maintainable foundation for AI-powered food management. The modular design allows easy integration of new AI features while maintaining system stability through fallbacks, caching, and comprehensive error handling.

For questions or contributions, please refer to the main README.md and API_DOCUMENTATION.md files.

---

**Last Updated**: November 21, 2025  
**Version**: 2.0  
**Author**: AI-Powered Food Management Platform Team
