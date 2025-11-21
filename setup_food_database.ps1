# Setup script for Part 4 - Food Items Database
# Run this script to initialize the food database

$separator = "=" * 60

Write-Host "Starting Food Database Setup..." -ForegroundColor Green
Write-Host $separator -ForegroundColor Green

# Step 1: Run migrations
Write-Host "`n1. Running migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Migrations completed successfully" -ForegroundColor Green
}
else {
    Write-Host "   ✗ Migration failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Seed food database
Write-Host "`n2. Seeding food database with 60 items..." -ForegroundColor Yellow
python manage.py seed_food

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Food database seeded successfully" -ForegroundColor Green
}
else {
    Write-Host "   ✗ Seeding failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Verify setup
Write-Host "`n3. Verifying setup..." -ForegroundColor Yellow
Write-Host "   Checking database..." -ForegroundColor Cyan

python -c "from food.models import FoodItemDatabase; count = FoodItemDatabase.objects.count(); print(f'   Found {count} food items in database')"

# Summary
Write-Host ""
Write-Host $separator -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "What was created:" -ForegroundColor Cyan
Write-Host "  ✓ FoodItemDatabase model with 8 fields" -ForegroundColor White
Write-Host "  ✓ 60+ food items across 8 categories" -ForegroundColor White
Write-Host "  ✓ Food database browsing views and templates" -ForegroundColor White
Write-Host "  ✓ Advanced search functionality" -ForegroundColor White
Write-Host "  ✓ Inventory form integration with auto-fill" -ForegroundColor White

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start the server: python manage.py runserver" -ForegroundColor White
Write-Host "  2. Visit: http://127.0.0.1:8000/food/food-database/" -ForegroundColor White
Write-Host "  3. Browse and search food items" -ForegroundColor White
Write-Host "  4. Add items to your inventory with auto-fill" -ForegroundColor White

Write-Host ""
Write-Host $separator -ForegroundColor Green
