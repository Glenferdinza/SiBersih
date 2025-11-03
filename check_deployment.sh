#!/bin/bash
# Quick deployment check script

echo "🔍 SiBersih Deployment Check"
echo "=============================="
echo ""

# Check Python version
echo "1. Python Version:"
python --version
echo ""

# Check if requirements are installed
echo "2. Checking Dependencies..."
pip list | grep -E "Django|gunicorn|whitenoise|mysqlclient|Pillow"
echo ""

# Check SECRET_KEY
echo "3. Generating new SECRET_KEY..."
python generate_secret_key.py
echo ""

# Test settings import
echo "4. Testing Django Settings..."
python manage.py check --deploy
echo ""

# Collect static files
echo "5. Collecting Static Files..."
python manage.py collectstatic --noinput --dry-run
echo ""

echo "✅ Pre-deployment check complete!"
echo ""
echo "Next steps:"
echo "1. Copy the SECRET_KEY above to .env file"
echo "2. Update .env with production database credentials"
echo "3. Push to GitHub"
echo "4. Deploy on Sevalla"
echo ""
