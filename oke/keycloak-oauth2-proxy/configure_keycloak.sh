#!/bin/bash

BASE_URL="http://localhost:8080/auth"
ADMIN_USER="admin"
ADMIN_PASS="admin"

# 1. Get Access Token
echo "Getting Admin Token..."
TOKEN_RESPONSE=$(curl -s -X POST "${BASE_URL}/realms/master/protocol/openid-connect/token" \
  -d "client_id=admin-cli" \
  -d "username=${ADMIN_USER}" \
  -d "password=${ADMIN_PASS}" \
  -d "grant_type=password")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" == "null" ]; then
  echo "Failed to get access token."
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi
echo "Access Token retrieved."

# 2. Create Realm 'lab'
echo "Creating Realm 'lab'..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/admin/realms" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"realm": "lab", "enabled": true}')

if [ "$STATUS" == "201" ]; then
  echo "Realm 'lab' created."
elif [ "$STATUS" == "409" ]; then
  echo "Realm 'lab' already exists."
else
  echo "Failed to create realm. Status: $STATUS"
  exit 1
fi

# 3. Create Client 'oauth2-proxy'
echo "Creating Client 'oauth2-proxy'..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/admin/realms/lab/clients" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "oauth2-proxy",
    "enabled": true,
    "clientAuthenticatorType": "client-secret",
    "secret": "eRRhRnBEPzKauIIVVtn0gisSFTuQtqS",
    "serviceAccountsEnabled": true,
    "standardFlowEnabled": true,
    "directAccessGrantsEnabled": true,
    "redirectUris": ["*"],
    "webOrigins": ["*"],
    "publicClient": false,
    "protocol": "openid-connect"
  }')

if [ "$STATUS" == "201" ]; then
  echo "Client 'oauth2-proxy' created."
elif [ "$STATUS" == "409" ]; then
  echo "Client 'oauth2-proxy' already exists."
else
  echo "Failed to create client. Status: $STATUS"
  exit 1
fi

# 4. Create User 'user'
echo "Creating User 'user'..."
USER_JSON='{
  "username": "user",
  "enabled": true,
  "firstName": "Demo", 
  "lastName": "User",
  "email": "user@example.com",
  "emailVerified": true,
  "credentials": [{
      "type": "password",
      "value": "password",
      "temporary": false
  }]
}'

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/admin/realms/lab/users" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$USER_JSON")

if [ "$STATUS" == "201" ]; then
  echo "User 'user' created."
elif [ "$STATUS" == "409" ]; then
  echo "User 'user' already exists."
else
  echo "Failed to create user. Status: $STATUS"
  # Don't exit here, user might already exist which is fine
fi

echo "Keycloak configuration for 'lab' realm completed!"
