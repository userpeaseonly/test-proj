#!/bin/bash

echo "🚀 Task Management System Setup Test"
echo "=================================="

echo "📋 1. Checking Django configuration..."
python manage.py check

echo ""
echo "📋 2. Creating migrations..."
python manage.py makemigrations

echo ""
echo "📋 3. Applying migrations..."
python manage.py migrate

echo ""
echo "📋 4. Creating admin user..."
python manage.py create_admin --email admin@test.com --password admin123

echo ""
echo "📋 5. Creating sample data..."
python manage.py create_sample_data

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Available endpoints:"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - Swagger: http://localhost:8000/swagger/"
echo "  - API: http://localhost:8000/api/"
echo ""
echo "🔑 Test credentials:"
echo "  - Admin: admin@test.com / admin123"
echo "  - User1: user1@example.com / testpass123"
echo "  - User2: user2@example.com / testpass123"
echo "  - User3: user3@example.com / testpass123"
echo ""
echo "🚀 Start server with: python manage.py runserver"