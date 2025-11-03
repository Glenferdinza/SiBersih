# SiBersih Deployment Check Script (Windows)
# Run this before deploying to Sevalla

Write-Host "🔍 SiBersih Deployment Check" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "1. Python Version:" -ForegroundColor Yellow
python --version
Write-Host ""

# Check if requirements are installed
Write-Host "2. Checking Dependencies..." -ForegroundColor Yellow
pip list | Select-String -Pattern "Django|gunicorn|whitenoise|mysqlclient|Pillow"
Write-Host ""

# Generate SECRET_KEY
Write-Host "3. Generating new SECRET_KEY..." -ForegroundColor Yellow
python generate_secret_key.py
Write-Host ""

# Test Django settings
Write-Host "4. Testing Django Settings..." -ForegroundColor Yellow
python manage.py check --deploy
Write-Host ""

# Collect static files (dry run)
Write-Host "5. Collecting Static Files (dry-run)..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --dry-run
Write-Host ""

Write-Host "✅ Pre-deployment check complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy the SECRET_KEY above to .env file"
Write-Host "2. Update .env with production database credentials"
Write-Host "3. Test locally: python manage.py runserver"
Write-Host "4. Push to GitHub: git push origin main"
Write-Host "5. Deploy on Sevalla dashboard"
Write-Host ""
Write-Host "📖 Read SEVALLA_DEPLOYMENT.md for detailed instructions" -ForegroundColor Magenta
