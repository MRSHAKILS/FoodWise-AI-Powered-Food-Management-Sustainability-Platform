{
  "project_context": {
    "name": "INNOVATEX Food Management Platform",
    "description": "AI-powered food management and sustainability platform for SDG 2 & 12",
    "phase": "Part 1 - Pre-Hackathon Foundation (No AI yet)",
    "note": "Design all data structures to be AI-ready for Part 2"
  },

  "PART_1_AUTHENTICATION_AND_USER_MANAGEMENT": {
    "feature": "User Registration and Login System",
    "priority": "CRITICAL - START HERE",
    "description": "Implement secure authentication with email/password",
    
    "requirements": [
      "User registration with validation",
      "Secure login system",
      "Password hashing with bcrypt (min 10 salt rounds)",
      "JWT or session-based authentication",
      "Protected route middleware"
    ],

    "user_data_model": {
      "User": {
        "fullName": "string, required, min 2 characters",
        "email": "string, required, unique, must be valid email format",
        "password": "string, required, min 8 characters, hashed before storage",
        "householdSize": "number, optional, min 1",
        "dietaryPreferences": "array of strings (vegetarian, vegan, halal, kosher, gluten-free, etc.)",
        "budgetRange": "string (low, medium, high) or number (monthly budget)",
        "location": "string (city, district, region for future local features)",
        "createdAt": "timestamp, auto-generated",
        "updatedAt": "timestamp, auto-generated"
      }
    },

    "validation_rules": {
      "email": "Must be valid email format (use regex or validator library)",
      "password": "Minimum 8 characters, must contain at least one letter and one number",
      "fullName": "Required, minimum 2 characters, no special characters except spaces",
      "householdSize": "If provided, must be positive integer",
      "dietaryPreferences": "Array can be empty but if provided, values must be from predefined list"
    },

    "api_endpoints": [
      {
        "method": "POST",
        "path": "/api/auth/register",
        "description": "Register new user",
        "request_body": {
          "fullName": "string",
          "email": "string",
          "password": "string",
          "householdSize": "number (optional)",
          "dietaryPreferences": "array (optional)",
          "budgetRange": "string (optional)",
          "location": "string (optional)"
        },
        "response_success": {
          "status": 201,
          "body": {
            "message": "User registered successfully",
            "user": "user object without password",
            "token": "JWT token (if using JWT)"
          }
        },
        "response_error": {
          "status": 400,
          "body": {
            "message": "Validation error description",
            "errors": "array of specific field errors"
          }
        }
      },
      {
        "method": "POST",
        "path": "/api/auth/login",
        "description": "Login existing user",
        "request_body": {
          "email": "string",
          "password": "string"
        },
        "response_success": {
          "status": 200,
          "body": {
            "message": "Login successful",
            "user": "user object without password",
            "token": "JWT token (if using JWT)"
          }
        },
        "response_error": {
          "status": 401,
          "body": {
            "message": "Invalid email or password"
          }
        }
      },
      {
        "method": "POST",
        "path": "/api/auth/logout",
        "description": "Logout user (clear session/token)",
        "response_success": {
          "status": 200,
          "body": {
            "message": "Logged out successfully"
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/auth/me",
        "description": "Get current authenticated user",
        "headers": "Authorization: Bearer {token} (if using JWT)",
        "response_success": {
          "status": 200,
          "body": {
            "user": "current user object without password"
          }
        },
        "response_error": {
          "status": 401,
          "body": {
            "message": "Not authenticated"
          }
        }
      }
    ],

    "implementation_steps": [
      "1. Install dependencies: bcrypt, jsonwebtoken (or express-session)",
      "2. Create User model/schema with all required fields",
      "3. Implement password hashing before saving user",
      "4. Create register endpoint with input validation",
      "5. Create login endpoint with password comparison",
      "6. Create authentication middleware to protect routes",
      "7. Create logout endpoint",
      "8. Create /auth/me endpoint to get current user",
      "9. Test all endpoints with valid and invalid data"
    ],

    "security_best_practices": [
      "Never store plain text passwords",
      "Use bcrypt.hash() with min 10 salt rounds",
      "Compare passwords using bcrypt.compare()",
      "Don't return password field in any API response",
      "Use JWT with expiration (e.g., 7 days) or secure sessions",
      "Validate all inputs before processing",
      "Return generic error messages for login failures (don't reveal if email exists)"
    ],

    "example_middleware": {
      "description": "Authentication middleware to protect routes",
      "usage": "Apply to routes that require authentication",
      "functionality": [
        "Extract token from Authorization header or session",
        "Verify token is valid",
        "Attach user object to request",
        "Return 401 if authentication fails"
      ]
    },

    "testing_checklist": [
      "✓ Can register with valid credentials",
      "✓ Cannot register with invalid email format",
      "✓ Cannot register with weak password (< 8 chars)",
      "✓ Cannot register with duplicate email",
      "✓ Can login with correct credentials",
      "✓ Cannot login with wrong password",
      "✓ Cannot login with non-existent email",
      "✓ Protected routes return 401 without token",
      "✓ Protected routes work with valid token",
      "✓ Password is hashed in database",
      "✓ Password is never returned in API responses"
    ]
  },

  "PART_2_USER_PROFILE_AND_FOOD_LOGGING": {
    "feature": "Profile Management and Consumption Logging",
    "priority": "HIGH - Do after authentication",
    "description": "Allow users to manage profiles and log daily food consumption",

    "data_models": {
      "FoodLog": {
        "userId": "ObjectId/foreign key reference to User, required",
        "itemName": "string, required, min 2 characters",
        "quantity": "number, required, must be positive",
        "unit": "string (kg, g, liters, ml, pieces, servings, etc.)",
        "category": "string (vegetable, fruit, dairy, grain, protein, snacks, beverages, etc.)",
        "logDate": "date, required, defaults to current date",
        "notes": "string, optional, max 500 characters",
        "createdAt": "timestamp, auto-generated"
      }
    },

    "profile_api_endpoints": [
      {
        "method": "GET",
        "path": "/api/profile",
        "description": "Get current user's profile",
        "authentication": "Required",
        "response": {
          "status": 200,
          "body": "user object with all profile fields"
        }
      },
      {
        "method": "PUT",
        "path": "/api/profile",
        "description": "Update user profile",
        "authentication": "Required",
        "request_body": {
          "fullName": "string (optional)",
          "householdSize": "number (optional)",
          "dietaryPreferences": "array (optional)",
          "budgetRange": "string/number (optional)",
          "location": "string (optional)"
        },
        "response": {
          "status": 200,
          "body": {
            "message": "Profile updated successfully",
            "user": "updated user object"
          }
        }
      }
    ],

    "food_log_api_endpoints": [
      {
        "method": "POST",
        "path": "/api/logs",
        "description": "Create new food consumption log",
        "authentication": "Required",
        "request_body": {
          "itemName": "string, required",
          "quantity": "number, required",
          "unit": "string, required",
          "category": "string, required",
          "logDate": "date (optional, defaults to today)",
          "notes": "string (optional)"
        },
        "response": {
          "status": 201,
          "body": {
            "message": "Food log created successfully",
            "log": "created log object"
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/logs",
        "description": "Get user's food consumption logs with filters",
        "authentication": "Required",
        "query_parameters": {
          "page": "number (default: 1)",
          "limit": "number (default: 20)",
          "category": "string (filter by category)",
          "startDate": "date (filter from date)",
          "endDate": "date (filter to date)",
          "sortBy": "string (logDate, createdAt)",
          "order": "string (asc, desc)"
        },
        "response": {
          "status": 200,
          "body": {
            "logs": "array of log objects",
            "pagination": {
              "page": "number",
              "limit": "number",
              "totalPages": "number",
              "totalLogs": "number"
            }
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/logs/:id",
        "description": "Get single food log by ID",
        "authentication": "Required",
        "response": {
          "status": 200,
          "body": "log object"
        }
      },
      {
        "method": "PUT",
        "path": "/api/logs/:id",
        "description": "Update food log",
        "authentication": "Required",
        "request_body": "any fields to update",
        "response": {
          "status": 200,
          "body": {
            "message": "Log updated successfully",
            "log": "updated log object"
          }
        }
      },
      {
        "method": "DELETE",
        "path": "/api/logs/:id",
        "description": "Delete food log",
        "authentication": "Required",
        "response": {
          "status": 200,
          "body": {
            "message": "Log deleted successfully"
          }
        }
      }
    ],

    "implementation_steps": [
      "1. Create FoodLog model/schema",
      "2. Implement profile GET and PUT endpoints",
      "3. Add validation for profile updates",
      "4. Implement food log POST endpoint with validation",
      "5. Implement food log GET endpoint with pagination and filters",
      "6. Implement food log GET by ID endpoint",
      "7. Implement food log PUT endpoint",
      "8. Implement food log DELETE endpoint",
      "9. Ensure all endpoints check user ownership (users can only access their own logs)",
      "10. Test all CRUD operations"
    ],

    "validation_rules": {
      "itemName": "Required, 2-100 characters",
      "quantity": "Required, must be positive number",
      "unit": "Required, must be from predefined list or free text",
      "category": "Required, should match predefined categories",
      "logDate": "Optional, if provided must be valid date, cannot be future date",
      "notes": "Optional, max 500 characters"
    },

    "ui_components_needed": [
      "Profile page with view and edit form",
      "Food log creation form (modal or separate page)",
      "Food logs list page with filters",
      "Edit log modal/page",
      "Delete confirmation dialog"
    ],

    "testing_checklist": [
      "✓ Can view own profile",
      "✓ Can update profile fields",
      "✓ Can create food log with valid data",
      "✓ Cannot create log with invalid data (negative quantity, empty name)",
      "✓ Can view list of own food logs",
      "✓ Can filter logs by category",
      "✓ Can filter logs by date range",
      "✓ Pagination works correctly",
      "✓ Can update own food log",
      "✓ Can delete own food log",
      "✓ Cannot view/edit/delete other users' logs"
    ]
  },

  "PART_3_INVENTORY_MANAGEMENT": {
    "feature": "User Inventory Tracking",
    "priority": "HIGH - Do after food logging",
    "description": "Allow users to maintain inventory of food items at home",

    "data_model": {
      "Inventory": {
        "userId": "ObjectId/foreign key reference to User, required",
        "itemName": "string, required, min 2 characters",
        "quantity": "number, required, must be positive",
        "unit": "string (kg, g, liters, ml, pieces, etc.)",
        "category": "string (vegetable, fruit, dairy, grain, protein, etc.)",
        "purchaseDate": "date, optional",
        "expirationDate": "date, optional",
        "cost": "number, optional (price paid for item)",
        "location": "string, optional (fridge, pantry, freezer)",
        "notes": "string, optional",
        "addedAt": "timestamp, auto-generated",
        "updatedAt": "timestamp, auto-generated"
      }
    },

    "api_endpoints": [
      {
        "method": "POST",
        "path": "/api/inventory",
        "description": "Add item to inventory",
        "authentication": "Required",
        "request_body": {
          "itemName": "string, required",
          "quantity": "number, required",
          "unit": "string, required",
          "category": "string, required",
          "purchaseDate": "date (optional)",
          "expirationDate": "date (optional)",
          "cost": "number (optional)",
          "location": "string (optional)",
          "notes": "string (optional)"
        },
        "response": {
          "status": 201,
          "body": {
            "message": "Item added to inventory",
            "item": "created inventory object"
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/inventory",
        "description": "Get user's inventory with filters",
        "authentication": "Required",
        "query_parameters": {
          "category": "string (filter by category)",
          "location": "string (filter by storage location)",
          "expiringWithinDays": "number (show items expiring within X days)",
          "sortBy": "string (expirationDate, addedAt, itemName)",
          "order": "string (asc, desc)"
        },
        "response": {
          "status": 200,
          "body": {
            "inventory": "array of inventory items",
            "summary": {
              "totalItems": "number",
              "totalValue": "number (sum of all costs)",
              "expiringCount": "number of items expiring soon"
            }
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/inventory/:id",
        "description": "Get single inventory item",
        "authentication": "Required",
        "response": {
          "status": 200,
          "body": "inventory item object"
        }
      },
      {
        "method": "PUT",
        "path": "/api/inventory/:id",
        "description": "Update inventory item (quantity, expiration, etc.)",
        "authentication": "Required",
        "request_body": "any fields to update",
        "response": {
          "status": 200,
          "body": {
            "message": "Inventory updated",
            "item": "updated item"
          }
        }
      },
      {
        "method": "DELETE",
        "path": "/api/inventory/:id",
        "description": "Remove item from inventory",
        "authentication": "Required",
        "response": {
          "status": 200,
          "body": {
            "message": "Item removed from inventory"
          }
        }
      }
    ],

    "implementation_steps": [
      "1. Create Inventory model/schema",
      "2. Implement POST endpoint to add inventory item",
      "3. Add validation for inventory data",
      "4. Implement GET endpoint with filters and summary calculation",
      "5. Implement GET by ID endpoint",
      "6. Implement PUT endpoint for updates",
      "7. Implement DELETE endpoint",
      "8. Add logic to calculate items expiring soon",
      "9. Ensure user ownership validation",
      "10. Test all CRUD operations"
    ],

    "special_features": {
      "expiration_tracking": {
        "description": "Identify items nearing expiration",
        "logic": "Compare expirationDate with current date",
        "thresholds": {
          "urgent": "expires within 2 days",
          "warning": "expires within 7 days",
          "safe": "expires after 7 days"
        }
      },
      "inventory_summary": {
        "description": "Calculate summary statistics",
        "metrics": [
          "Total number of items",
          "Total inventory value (sum of costs)",
          "Number of items expiring soon",
          "Items by category count"
        ]
      }
    },

    "ui_components_needed": [
      "Inventory list page with filters (category, location, expiring soon)",
      "Add inventory item form",
      "Edit inventory item form",
      "Inventory item detail view",
      "Visual indicators for expiring items (color coding)",
      "Inventory summary cards/widgets"
    ],

    "testing_checklist": [
      "✓ Can add item to inventory",
      "✓ Cannot add item with invalid data",
      "✓ Can view inventory list",
      "✓ Can filter by category",
      "✓ Can filter by storage location",
      "✓ Can filter items expiring soon",
      "✓ Can update inventory item quantity",
      "✓ Can update expiration date",
      "✓ Can delete inventory item",
      "✓ Summary shows correct totals",
      "✓ Expiring items are correctly identified"
    ]
  },

  "PART_4_FOOD_ITEMS_DATABASE": {
    "feature": "Seeded Food Items Database",
    "priority": "MEDIUM - Can do alongside other features",
    "description": "Create and seed database with common food items",

    "data_model": {
      "FoodItem": {
        "itemName": "string, required, unique",
        "category": "string (fruit, dairy, grain, vegetable, protein, snacks, beverages, etc.)",
        "typicalExpirationDays": "number (how many days item typically lasts)",
        "sampleCostPerUnit": "number (average cost)",
        "unit": "string (kg, liter, dozen, piece, etc.)",
        "nutritionalInfo": "object, optional {calories: number, protein: number, carbs: number, fat: number}",
        "storageInstructions": "string, optional (how to store properly)",
        "imageUrl": "string, optional (placeholder image URL)",
        "createdAt": "timestamp"
      }
    },

    "seed_data_minimum_20_items": [
      {"itemName": "Milk", "category": "dairy", "typicalExpirationDays": 7, "sampleCostPerUnit": 350, "unit": "liter", "storageInstructions": "Keep refrigerated at 4°C"},
      {"itemName": "Eggs", "category": "protein", "typicalExpirationDays": 21, "sampleCostPerUnit": 400, "unit": "dozen", "storageInstructions": "Store in refrigerator"},
      {"itemName": "Chicken Breast", "category": "protein", "typicalExpirationDays": 2, "sampleCostPerUnit": 800, "unit": "kg", "storageInstructions": "Keep frozen or use within 2 days"},
      {"itemName": "Rice (White)", "category": "grain", "typicalExpirationDays": 365, "sampleCostPerUnit": 200, "unit": "kg", "storageInstructions": "Store in cool, dry place"},
      {"itemName": "Bananas", "category": "fruit", "typicalExpirationDays": 5, "sampleCostPerUnit": 150, "unit": "kg", "storageInstructions": "Store at room temperature"},
      {"itemName": "Apples", "category": "fruit", "typicalExpirationDays": 30, "sampleCostPerUnit": 300, "unit": "kg", "storageInstructions": "Refrigerate for longer life"},
      {"itemName": "Tomatoes", "category": "vegetable", "typicalExpirationDays": 7, "sampleCostPerUnit": 100, "unit": "kg", "storageInstructions": "Store at room temperature"},
      {"itemName": "Potatoes", "category": "vegetable", "typicalExpirationDays": 30, "sampleCostPerUnit": 80, "unit": "kg", "storageInstructions": "Store in cool, dark place"},
      {"itemName": "Onions", "category": "vegetable", "typicalExpirationDays": 30, "sampleCostPerUnit": 70, "unit": "kg", "storageInstructions": "Store in cool, dry place"},
      {"itemName": "Carrots", "category": "vegetable", "typicalExpirationDays": 21, "sampleCostPerUnit": 90, "unit": "kg", "storageInstructions": "Refrigerate in plastic bag"},
      {"itemName": "Bread (Whole Wheat)", "category": "grain", "typicalExpirationDays": 5, "sampleCostPerUnit": 60, "unit": "loaf", "storageInstructions": "Store in cool, dry place or freeze"},
      {"itemName": "Yogurt", "category": "dairy", "typicalExpirationDays": 14, "sampleCostPerUnit": 120, "unit": "500g", "storageInstructions": "Keep refrigerated"},
      {"itemName": "Cheese (Cheddar)", "category": "dairy", "typicalExpirationDays": 30, "sampleCostPerUnit": 500, "unit": "500g", "storageInstructions": "Wrap tightly and refrigerate"},
      {"itemName": "Lentils (Red)", "category": "protein", "typicalExpirationDays": 365, "sampleCostPerUnit": 180, "unit": "kg", "storageInstructions": "Store in airtight container"},
      {"itemName": "Pasta", "category": "grain", "typicalExpirationDays": 730, "sampleCostPerUnit": 150, "unit": "500g", "storageInstructions": "Store in cool, dry place"},
      {"itemName": "Cooking Oil", "category": "other", "typicalExpirationDays": 180, "sampleCostPerUnit": 300, "unit": "liter", "storageInstructions": "Store in cool place away from light"},
      {"itemName": "Spinach", "category": "vegetable", "typicalExpirationDays": 5, "sampleCostPerUnit": 60, "unit": "bunch", "storageInstructions": "Refrigerate in plastic bag"},
      {"itemName": "Cucumber", "category": "vegetable", "typicalExpirationDays": 7, "sampleCostPerUnit": 40, "unit": "kg", "storageInstructions": "Refrigerate"},
      {"itemName": "Orange Juice", "category": "beverages", "typicalExpirationDays": 7, "sampleCostPerUnit": 200, "unit": "liter", "storageInstructions": "Keep refrigerated after opening"},
      {"itemName": "Butter", "category": "dairy", "typicalExpirationDays": 90, "sampleCostPerUnit": 350, "unit": "500g", "storageInstructions": "Keep refrigerated"}
    ],

    "api_endpoints": [
      {
        "method": "GET",
        "path": "/api/food-items",
        "description": "Get all food items with filters",
        "authentication": "Optional (can be public or protected)",
        "query_parameters": {
          "category": "string (filter by category)",
          "search": "string (search by name)",
          "sortBy": "string (itemName, category, typicalExpirationDays)",
          "order": "string (asc, desc)"
        },
        "response": {
          "status": 200,
          "body": {
            "foodItems": "array of food item objects",
            "categories": "array of unique categories"
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/food-items/:id",
        "description": "Get single food item details",
        "response": {
          "status": 200,
          "body": "food item object with all details"
        }
      }
    ],

    "implementation_steps": [
      "1. Create FoodItem model/schema",
      "2. Create seed script/file with 20+ food items",
      "3. Implement seeding function (can be run via npm script or on server start)",
      "4. Implement GET /api/food-items endpoint with filters",
      "5. Implement GET /api/food-items/:id endpoint",
      "6. Create UI page to browse food items",
      "7. Add search and filter functionality in UI",
      "8. Test that seed data loads correctly"
    ],

    "ui_components_needed": [
      "Food items browse page with grid or list view",
      "Search bar for food items",
      "Category filter dropdown",
      "Food item detail card/modal",
      "Display: name, category, expiration days, sample cost, storage tips"
    ],

    "seed_script_example": {
      "description": "Create a seed script that can be run to populate database",
      "usage": "npm run seed OR automatically on first server start",
      "behavior": "Check if food items already exist before inserting to avoid duplicates"
    },

    "testing_checklist": [
      "✓ Seed script runs without errors",
      "✓ At least 20 food items are in database",
      "✓ Can view all food items",
      "✓ Can search food items by name",
      "✓ Can filter by category",
      "✓ Can view single food item details",
      "✓ All seeded data has required fields"
    ]
  },

  "PART_5_RESOURCES_DATABASE": {
    "feature": "Educational Resources for Sustainability",
    "priority": "MEDIUM - Can do alongside other features",
    "description": "Seed database with resources for waste reduction, nutrition, budgeting",

    "data_model": {
      "Resource": {
        "title": "string, required",
        "description": "string, required, 100-500 characters",
        "url": "string, optional (external link to full resource)",
        "category": "string (waste_reduction, budget_tips, meal_planning, storage_tips, nutrition, sustainability)",
        "type": "string (article, video, infographic, guide, tip)",
        "tags": "array of strings (keywords for searching)",
        "relevantFoodCategories": "array of strings (dairy, vegetable, fruit, grain, protein, all)",
        "readTime": "number, optional (estimated minutes to read/watch)",
        "createdAt": "timestamp"
      }
    },

    "seed_data_minimum_20_resources": [
      {"title": "How to Store Dairy Products Properly", "description": "Learn the best practices for extending the shelf life of milk, cheese, and yogurt", "category": "storage_tips", "type": "article", "tags": ["dairy", "storage", "refrigeration"], "relevantFoodCategories": ["dairy"], "readTime": 5},
      {"title": "Meal Planning on a Budget", "description": "Weekly meal planning strategies to reduce waste and save money on groceries", "category": "budget_tips", "type": "guide", "tags": ["budget", "meal planning", "savings"], "relevantFoodCategories": ["all"], "readTime": 10},
      {"title": "Vegetable Storage Guide", "description": "Proper storage methods for different vegetables to keep them fresh longer", "category": "storage_tips", "type": "infographic", "tags": ["vegetables", "storage", "freshness"], "relevantFoodCategories": ["vegetable"], "readTime": 3},
      {"title": "Reducing Food Waste at Home", "description": "Simple techniques to minimize food waste in your household", "category": "waste_reduction", "type": "article", "tags": ["waste reduction", "sustainability"], "relevantFoodCategories": ["all"], "readTime": 7},
      {"title": "Understanding Food Expiration Dates", "description": "Learn the difference between sell-by, use-by, and best-before dates", "category": "waste_reduction", "type": "guide", "tags": ["expiration", "food safety"], "relevantFoodCategories": ["all"], "readTime": 5},
      {"title": "Freezing Food: What You Need to Know", "description": "Complete guide to freezing different food types safely", "category": "storage_tips", "type": "guide", "tags": ["freezing", "storage", "preservation"], "relevantFoodCategories": ["all"], "readTime": 8},
      {"title": "Protein on a Budget", "description": "Affordable protein sources and how to use them efficiently", "category": "budget_tips", "type": "article", "tags": ["protein", "budget", "nutrition"], "relevantFoodCategories": ["protein"], "readTime": 6},
      {"title": "Composting Kitchen Scraps", "description": "How to start composting to reduce organic waste", "category": "waste_reduction", "type": "video", "tags": ["composting", "waste reduction", "sustainability"], "relevantFoodCategories": ["all"], "readTime": 12},
      {"title": "Ripening and Storing Fruits", "description": "Tips for ripening fruits and keeping them fresh", "category": "storage_tips", "type": "article", "tags": ["fruits", "ripening", "storage"], "relevantFoodCategories": ["fruit"], "readTime": 5},
      {"title": "Batch Cooking for Busy Families", "description": "Save time and reduce waste with batch cooking techniques", "category": "meal_planning", "type": "guide", "tags": ["batch cooking", "meal prep", "efficiency"], "relevantFoodCategories": ["all"], "readTime": 10},
      {"title": "Understanding Nutritional Labels", "description": "How to read and understand food nutrition labels", "category": "nutrition", "type": "article", "tags": ["nutrition", "labels", "health"], "relevantFoodCategories": ["all"], "readTime": 6},
      {"title": "Storing Grains and Dry Foods", "description": "Best practices for storing rice, pasta, and other dry goods", "category": "storage_tips", "type": "tip", "tags": ["grains", "storage", "pantry"], "relevantFoodCategories": ["grain"], "readTime": 4},
      {"title": "Seasonal Eating Guide", "description": "Why eating seasonal produce is better for budget and environment", "category": "sustainability", "type": "guide", "tags": ["seasonal", "sustainability", "budget"], "relevantFoodCategories": ["fruit", "vegetable"], "readTime": 8},
      {"title": "Leftover Transformation Ideas", "description": "Creative ways to use leftovers and reduce waste", "category": "waste_reduction", "type": "article", "tags": ["leftovers", "recipes", "waste reduction"], "relevantFoodCategories": ["all"], "readTime": 7},
      {"title": "Shopping List Strategies", "description": "How to create efficient shopping lists that reduce waste", "category": "meal_planning", "type": "guide", "tags": ["shopping", "planning", "waste reduction"], "relevantFoodCategories": ["all"], "readTime": 5},
      {"title": "Portion Control Basics", "description": "Understanding portion sizes to avoid overcooking and waste", "category": "nutrition", "type": "article", "tags": ["portions", "nutrition", "waste reduction"], "relevantFoodCategories": ["all"], "readTime": 6},
      {"title": "Herb and Spice Storage", "description": "Keeping herbs and spices fresh and flavorful", "category": "storage_tips", "type": "tip", "tags": ["herbs", "spices", "storage"], "relevantFoodCategories": ["other"], "readTime": 3},
      {"title": "Budget-Friendly Vegetarian Meals", "description": "Nutritious vegetarian meal ideas that won't break the bank", "category": "budget_tips", "type": "guide", "tags": ["vegetarian", "budget", "recipes"], "relevantFoodCategories": ["vegetable", "protein"], "readTime": 9},
      {"title": "First In, First Out (FIFO) Method", "description": "Organize your pantry and fridge to reduce expiration waste", "category": "waste_reduction", "type": "tip", "tags": ["organization", "FIFO", "waste reduction"], "relevantFoodCategories": ["all"], "readTime": 4},
      {"title": "Hydration and Nutrition Basics", "description": "Understanding daily nutritional needs and staying hydrated", "category": "nutrition", "type": "article", "tags": ["nutrition", "health", "hydration"], "relevantFoodCategories": ["all"], "readTime": 7}
    ],

    "api_endpoints": [
      {
        "method": "GET",
        "path": "/api/resources",
        "description": "Get all resources with filters",
        "query_parameters": {
          "category": "string (filter by category)",
          "type": "string (filter by type)",
          "tags": "string (filter by tag)",
          "relevantFoodCategories": "string (filter by relevant food category)",
          "search": "string (search in title and description)"
        },
        "response": {
          "status": 200,
          "body": {
            "resources": "array of resource objects",
            "categories": "array of unique categories",
            "types": "array of unique types"
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/resources/:id",
        "description": "Get single resource details",
        "response": {
          "status": 200,
          "body": "resource object with all details"
        }
      }
    ],

    "implementation_steps": [
      "1. Create Resource model/schema",
      "2. Create seed script with 20+ resources",
      "3. Implement seeding function",
      "4. Implement GET /api/resources endpoint with filters",
      "5. Implement GET /api/resources/:id endpoint",
      "6. Create Resources page in UI",
      "7. Add category and type filters",
      "8. Add search functionality",
      "9. Test that seed data loads correctly"
    ],

    "ui_components_needed": [
      "Resources browse page with card layout",
      "Category filter (tabs or dropdown)",
      "Type filter (article, video, guide, etc.)",
      "Search bar",
      "Resource card showing: title, description, type, category, read time",
      "Resource detail view/modal",
      "External link button if URL exists"
    ],

    "testing_checklist": [
      "✓ Seed script runs without errors",
      "✓ At least 20 resources are in database",
      "✓ Can view all resources",
      "✓ Can filter by category",
      "✓ Can filter by type",
      "✓ Can search resources",
      "✓ Can view single resource details",
      "✓ External links work (if provided)"
    ]
  },

  "PART_6_BASIC_TRACKING_LOGIC": {
    "feature": "Simple Rule-Based Recommendation System",
    "priority": "MEDIUM - Do after logs and inventory are working",
    "description": "Implement non-AI tracking logic to recommend resources based on user activity",

    "logic_rules": {
      "rule_1_category_matching": {
        "description": "Recommend resources based on logged food categories",
        "logic": "If user logs items in 'dairy' category, recommend resources with relevantFoodCategories containing 'dairy'",
        "reason_text": "Related to: {category} - You recently logged {category} items"
      },
      "rule_2_expiration_warning": {
        "description": "Alert users about items expiring soon",
        "logic": "Check inventory for items with expirationDate within 2-7 days",
        "thresholds": {
          "urgent": "2 days or less (red alert)",
          "warning": "3-7 days (yellow warning)"
        }
      },
      "rule_3_frequent_category": {
        "description": "Recommend budget tips for frequently logged categories",
        "logic": "Count logs by category in last 30 days, find top category, recommend budget_tips resources for that category",
        "reason_text": "You frequently log {category} items - here are budget tips"
      },
      "rule_4_waste_reduction": {
        "description": "Recommend waste reduction resources to all users",
        "logic": "Always show 2-3 waste reduction resources with category 'waste_reduction'",
        "reason_text": "General waste reduction tips for sustainable living"
      },
      "rule_5_storage_tips": {
        "description": "Recommend storage tips based on inventory items",
        "logic": "Check user's inventory categories, recommend storage_tips for those categories",
        "reason_text": "Storage tips for items in your inventory"
      }
    },

    "dashboard_summary_calculation": {
      "total_inventory_items": "Count of all items in user's inventory",
      "total_inventory_value": "Sum of (quantity * cost) for all inventory items where cost exists",
      "recent_logs_count": "Count of food logs in last 7 days",
      "items_expiring_soon": "Count of inventory items with expirationDate within next 7 days",
      "most_logged_category": "Category with highest log count in last 30 days",
      "average_daily_logs": "Total logs / days since first log"
    },

    "api_endpoints": [
      {
        "method": "GET",
        "path": "/api/dashboard/summary",
        "description": "Get dashboard summary statistics",
        "authentication": "Required",
        "response": {
          "status": 200,
          "body": {
            "totalInventoryItems": "number",
            "totalInventoryValue": "number",
            "recentLogsCount": "number (last 7 days)",
            "itemsExpiringSoon": "number (within 7 days)",
            "expiringItems": "array of items expiring soon with details",
            "mostLoggedCategory": "string",
            "categoryBreakdown": "object {category: count}",
            "recentLogs": "array of last 5 logs"
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/recommendations",
        "description": "Get personalized resource recommendations with reasoning",
        "authentication": "Required",
        "response": {
          "status": 200,
          "body": {
            "recommendations": [
              {
                "resource": "resource object",
                "reason": "string explaining why recommended",
                "relevanceScore": "number 1-10",
                "matchedRule": "string (category_match, expiration_warning, etc.)"
              }
            ]
          }
        }
      }
    ],

    "implementation_steps": [
      "1. Create dashboard summary calculation function",
      "2. Implement GET /api/dashboard/summary endpoint",
      "3. Create recommendation engine function with rules",
      "4. Implement GET /api/recommendations endpoint",
      "5. Test each rule individually",
      "6. Test that recommendations change based on user activity",
      "7. Display recommendations on dashboard with reasons",
      "8. Add visual indicators for expiring items"
    ],

    "recommendation_algorithm_pseudocode": {
      "step_1": "Fetch user's recent food logs (last 30 days)",
      "step_2": "Extract categories from logs",
      "step_3": "Fetch user's current inventory",
      "step_4": "Extract categories from inventory",
      "step_5": "Query resources matching log categories (rule 1)",
      "step_6": "Query resources matching inventory categories for storage tips (rule 5)",
      "step_7": "Find most frequent category and get budget tips (rule 3)",
      "step_8": "Always add 2-3 general waste reduction resources (rule 4)",
      "step_9": "Deduplicate recommendations",
      "step_10": "Sort by relevance score",
      "step_11": "Return top 5-10 recommendations with reasons"
    },

    "ui_components_needed": [
      "Dashboard summary cards (total items, total value, logs, expiring items)",
      "Expiring items alert section with urgency colors",
      "Recommendations section with resource cards",
      "Each recommendation shows: resource info + reason for recommendation",
      "Visual charts (optional): category breakdown pie chart, logs over time"
    ],

    "testing_checklist": [
      "✓ Dashboard summary shows correct counts",
      "✓ Total inventory value calculates correctly",
      "✓ Expiring items are identified correctly",
      "✓ Most logged category is accurate",
      "✓ Recommendations appear for logged categories",
      "✓ Storage tips recommended for inventory categories",
      "✓ Budget tips recommended for frequent categories",
      "✓ Each recommendation has clear reason text",
      "✓ Recommendations change when user adds new logs/inventory",
      "✓ No duplicate recommendations"
    ]
  },

  "PART_7_IMAGE_UPLOAD": {
    "feature": "Receipt and Food Label Image Upload",
    "priority": "LOW - Can do last (UI only, no processing)",
    "description": "Allow users to upload receipt or food label images for future AI processing",

    "data_model": {
      "Upload": {
        "userId": "ObjectId/foreign key reference to User, required",
        "fileName": "string, required (original filename)",
        "fileUrl": "string, required (URL or path where file is stored)",
        "fileType": "string (receipt, food_label, other)",
        "mimeType": "string (image/jpeg, image/png)",
        "fileSize": "number (in bytes)",
        "associatedInventoryId": "ObjectId reference to Inventory, optional",
        "associatedLogId": "ObjectId reference to FoodLog, optional",
        "uploadDate": "timestamp, auto-generated",
        "notes": "string, optional",
        "processed": "boolean, default false (for future AI processing in Part 2)"
      }
    },

    "storage_options": {
      "option_1_local": {
        "description": "Store files in server's file system",
        "path": "uploads/ folder in project root",
        "pros": "Simple, no external dependencies",
        "cons": "Not suitable for production deployment"
      },
      "option_2_cloudinary": {
        "description": "Use Cloudinary for image storage",
        "pros": "Free tier available, CDN, image transformations",
        "setup": "npm install cloudinary, get API keys"
      },
      "option_3_aws_s3": {
        "description": "Use AWS S3 for storage",
        "pros": "Scalable, reliable",
        "cons": "Requires AWS account setup"
      },
      "recommendation": "Use Cloudinary or local storage for hackathon. Local is quickest to implement."
    },

    "api_endpoints": [
      {
        "method": "POST",
        "path": "/api/uploads",
        "description": "Upload image file",
        "authentication": "Required",
        "request": "multipart/form-data with file and metadata",
        "form_fields": {
          "file": "image file (JPG/PNG, max 5MB)",
          "fileType": "string (receipt, food_label)",
          "notes": "string (optional)"
        },
        "response": {
          "status": 201,
          "body": {
            "message": "File uploaded successfully",
            "upload": "upload object with fileUrl"
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/uploads",
        "description": "Get user's uploaded files",
        "authentication": "Required",
        "query_parameters": {
          "fileType": "string (filter by type)",
          "associated": "boolean (show only associated uploads)"
        },
        "response": {
          "status": 200,
          "body": {
            "uploads": "array of upload objects"
          }
        }
      },
      {
        "method": "GET",
        "path": "/api/uploads/:id",
        "description": "Get single upload details",
        "authentication": "Required",
        "response": {
          "status": 200,
          "body": "upload object"
        }
      },
      {
        "method": "PUT",
        "path": "/api/uploads/:id",
        "description": "Update upload associations or notes",
        "authentication": "Required",
        "request_body": {
          "associatedInventoryId": "string (optional)",
          "associatedLogId": "string (optional)",
          "notes": "string (optional)",
          "fileType": "string (optional)"
        },
        "response": {
          "status": 200,
          "body": {
            "message": "Upload updated",
            "upload": "updated upload object"
          }
        }
      },
      {
        "method": "DELETE",
        "path": "/api/uploads/:id",
        "description": "Delete uploaded file",
        "authentication": "Required",
        "response": {
          "status": 200,
          "body": {
            "message": "Upload deleted successfully"
          }
        }
      }
    ],

    "implementation_steps": [
      "1. Install multer (for file uploads) - npm install multer",
      "2. If using Cloudinary: npm install cloudinary and configure",
      "3. Create Upload model/schema",
      "4. Set up multer middleware for file uploads",
      "5. Implement POST /api/uploads endpoint",
      "6. Store file and save metadata to database",
      "7. Implement GET /api/uploads endpoint",
      "8. Implement PUT endpoint for associations",
      "9. Implement DELETE endpoint (delete file and database record)",
      "10. Create upload UI with file picker and preview"
    },

    "file_validation": {
      "allowed_types": ["image/jpeg", "image/jpg", "image/png"],
      "max_file_size": "5MB (5 * 1024 * 1024 bytes)",
      "validation_errors": {
        "invalid_type": "Only JPG and PNG images are allowed",
        "file_too_large": "File size must be less than 5MB"
      }
    },

    "ui_components_needed": [
      "Upload page or modal with file picker",
      "Drag-and-drop zone (optional but nice)",
      "File type selector (receipt or food label)",
      "Notes input field",
      "Upload progress indicator",
      "Uploads gallery showing all uploaded images",
      "Image preview",
      "Associate upload button (link to inventory or log)",
      "Delete upload confirmation"
    ],

    "association_workflow": {
      "description": "Allow users to manually link uploads to inventory or logs",
      "steps": [
        "1. User uploads image",
        "2. User views upload in gallery",
        "3. User clicks 'Associate with inventory' or 'Associate with log'",
        "4. Modal/dropdown shows user's inventory items or recent logs",
        "5. User selects item/log to associate",
        "6. Association is saved"
      ]
    },

    "testing_checklist": [
      "✓ Can upload JPG image",
      "✓ Can upload PNG image",
      "✓ Cannot upload other file types",
      "✓ Cannot upload files larger than 5MB",
      "✓ Uploaded file is stored correctly",
      "✓ Can view list of uploads",
      "✓ Can view single upload with image preview",
      "✓ Can associate upload with inventory item",
      "✓ Can associate upload with food log",
      "✓ Can delete upload (file and database record removed)",
      "✓ Only own uploads are visible to user"
    ],

    "note_for_part_2": "In Part 2, these uploads will be processed with AI for receipt parsing and label reading. Keep the structure ready for adding 'extractedData' field and 'processed' status."
  },

  "PART_8_DOCUMENTATION_AND_DEPLOYMENT": {
    "feature": "README and Code Quality",
    "priority": "CRITICAL - Must do before submission",
    "description": "Complete documentation and ensure code quality",

    "readme_structure": {
      "section_1_project_overview": {
        "description": "2-3 line summary of the project",
        "example": "INNOVATEX Food Management Platform is a full-stack web application designed to help individuals and families reduce food waste, track consumption, and promote sustainable eating habits. Built for SDG 2 (Zero Hunger) and SDG 12 (Responsible Consumption)."
      },
      "section_2_tech_stack": {
        "description": "List all technologies used",
        "format": [
          "Frontend: React, Tailwind CSS, etc.",
          "Backend: Node.js, Express, etc.",
          "Database: MongoDB/PostgreSQL/etc.",
          "Authentication: JWT/Session",
          "File Upload: Multer, Cloudinary",
          "Other: Any additional libraries"
        ]
      },
      "section_3_prerequisites": {
        "description": "What must be installed before setup",
        "items": [
          "Node.js (v16 or higher)",
          "npm or yarn",
          "W