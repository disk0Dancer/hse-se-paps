#!/bin/bash

# Test script for authentication flow
# This script tests the complete flow from registration to authenticated API access
# Including the token auto-refresh functionality

set -e
API_BASE_URL="http://localhost:8000"
EMAIL="test$(date +%s)@example.com"
LOGIN="testuser$(date +%s)"
PASSWORD="password123456"
AUTH_TOKEN=""
REFRESH_TOKEN=""
USER_GUID=""

echo "Starting authentication flow test..."


# Step 1: Register a new user
echo "1. Registering a new user: $LOGIN"
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE_URL/user/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"login\":\"$LOGIN\",\"password\":\"$PASSWORD\"}")

USER_GUID=$(echo $REGISTER_RESPONSE | grep -o '"guid":"[^"]*' | sed 's/"guid":"//')
if [ -z "$USER_GUID" ]; then
  echo "Error: Failed to extract user GUID from registration response"
  echo "Response: $REGISTER_RESPONSE"
  exit 1
fi

echo "User registered successfully with GUID: $USER_GUID"
echo $REGISTER_RESPONSE | python3 -m json.tool


# Step 2: Authenticate and get a token
echo "2. Authenticating user to get token"
TOKEN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$LOGIN&password=$PASSWORD")

AUTH_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"refresh_token":"[^"]*' | sed 's/"refresh_token":"//')
if [ -z "$AUTH_TOKEN" ]; then
  echo "Error: Failed to extract access token from response"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "Authentication successful! Access and refresh tokens received."
echo $TOKEN_RESPONSE | python3 -m json.tool

echo "Access token: $AUTH_TOKEN"
