#!/bin/bash

# Test script for authentication flow
# This script tests the complete flow from registration to authenticated API access
# Including the token auto-refresh functionality

set -e
API_BASE_URL="http://localhost:8000"
EMAIL="test@example.com"
LOGIN="testuser$(date +%s)"
PASSWORD="password123456"
AUTH_TOKEN=""
REFRESH_TOKEN=""
USER_GUID=""

echo "Starting authentication flow test..."

# Step 1: Register a new user
echo "1. Registering a new user: $LOGIN"
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE_URL/user/user/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"login\":\"$LOGIN\",\"password\":\"$PASSWORD\"}")
echo "Registration response:\n{$REGISTER_RESPONSE}"

# Extract the user GUID from the response
USER_GUID=$(echo $REGISTER_RESPONSE | grep -o '"guid":"[^"]*' | sed 's/"guid":"//')

if [ -z "$USER_GUID" ]; then
  echo "Error: Failed to extract user GUID from registration response"
  echo "Response: $REGISTER_RESPONSE"
  exit 1
fi

echo "User registered successfully with GUID: $USER_GUID"

# Step 2: Authenticate and get a token
echo "2. Authenticating user to get token"
TOKEN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$LOGIN&password=$PASSWORD")

# Extract the access token and refresh token
AUTH_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"refresh_token":"[^"]*' | sed 's/"refresh_token":"//')

if [ -z "$AUTH_TOKEN" ]; then
  echo "Error: Failed to extract access token from response"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "Authentication successful! Access and refresh tokens received."

# Step 3: Access a protected endpoint (user profile endpoint)
echo "3. Accessing protected endpoint with the token"
PROFILE_RESPONSE=$(curl -s -X GET "$API_BASE_URL/users/me" \
  -H "Authorization: Bearer $AUTH_TOKEN")

echo "Protected endpoint response:"
echo $PROFILE_RESPONSE | python3 -m json.tool

# Step 4: Try to access user's data using the token
echo "4. Accessing user data by GUID"
USER_RESPONSE=$(curl -s -X GET "$API_BASE_URL/user/user/$USER_GUID" \
  -H "Authorization: Bearer $AUTH_TOKEN")

echo "User data response:"
echo $USER_RESPONSE | python3 -m json.tool

# Step 5: Test token refresh
echo "5. Testing token refresh functionality"
REFRESH_RESPONSE=$(curl -s -X POST "$API_BASE_URL/token/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

NEW_AUTH_TOKEN=$(echo $REFRESH_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
NEW_REFRESH_TOKEN=$(echo $REFRESH_RESPONSE | grep -o '"refresh_token":"[^"]*' | sed 's/"refresh_token":"//')

if [ -z "$NEW_AUTH_TOKEN" ]; then
  echo "Error: Failed to get new access token"
  echo "Response: $REFRESH_RESPONSE"
  exit 1
fi

echo "Token refresh successful! New access and refresh tokens received."

# Step 6: Use the new token to access protected data
echo "6. Accessing protected endpoint with the new token"
NEW_PROFILE_RESPONSE=$(curl -s -X GET "$API_BASE_URL/users/me" \
  -H "Authorization: Bearer $NEW_AUTH_TOKEN")

echo "Protected endpoint response with new token:"
echo $NEW_PROFILE_RESPONSE | python3 -m json.tool

echo "Auto-refresh authentication flow test completed successfully!"
