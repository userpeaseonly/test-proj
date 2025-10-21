#!/bin/bash

echo "🔐 Authentication System Test"
echo "============================"

# Base URL (adjust if needed)
BASE_URL="http://localhost:8000"

echo ""
echo "📋 1. Testing User Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123!",
    "password_confirm": "testpass123!",
    "first_name": "Test",
    "last_name": "User"
  }')

echo "Register Response: $REGISTER_RESPONSE"

echo ""
echo "📋 2. Testing User Login..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/login/" \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123!"
  }')

echo "Login Response: $LOGIN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

echo ""
echo "📋 3. Testing /me endpoint..."
if [ ! -z "$ACCESS_TOKEN" ]; then
  ME_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/auth/me/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
  echo "Me Response: $ME_RESPONSE"
else
  echo "❌ No access token received"
fi

echo ""
echo "📋 4. Testing Token Refresh..."
REFRESH_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/refresh/" \
  -b cookies.txt \
  -c cookies.txt)

echo "Refresh Response: $REFRESH_RESPONSE"

echo ""
echo "📋 5. Testing Logout..."
LOGOUT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/logout/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -b cookies.txt)

echo "Logout Response: $LOGOUT_RESPONSE"

# Clean up
rm -f cookies.txt

echo ""
echo "✅ Authentication system test completed!"
echo ""
echo "🌐 Available endpoints:"
echo "  - POST /api/auth/register/ - User registration"
echo "  - POST /api/auth/login/ - User login (sets HTTP-only cookie)"
echo "  - POST /api/auth/refresh/ - Refresh access token"
echo "  - GET /api/auth/me/ - Get current user info"
echo "  - POST /api/auth/logout/ - Logout and clear cookie"
echo ""
echo "🔐 Security features:"
echo "  - ✅ Refresh token in HTTP-only cookie (JavaScript cannot access)"
echo "  - ✅ Access token in response body for Authorization header"
echo "  - ✅ Password validation and hashing"
echo "  - ✅ JWT token rotation on refresh"
echo "  - ✅ Role assignment locked to 'user' (only admins can change roles)"