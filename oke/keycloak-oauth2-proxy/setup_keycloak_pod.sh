#!/bin/bash

# Keycloak Pod Name
POD_NAME="keycloak-keycloakx-0"
KC_ADM="/opt/keycloak/bin/kcadm.sh"
KC_SERVER="http://localhost:8080/auth"
ADMIN_USER="admin"
ADMIN_PASS="admin"

echo "Configuring Keycloak on pod $POD_NAME..."

# 1. Authenticate
kubectl exec -i $POD_NAME -- $KC_ADM config credentials --server $KC_SERVER --realm master --user $ADMIN_USER --password $ADMIN_PASS

# 2. Disable SSL for Master Realm
echo "Disabling SSL for master realm..."
kubectl exec -i $POD_NAME -- $KC_ADM update realms/master -s sslRequired=NONE

# 3. Create Lab Realm (if not exists) & Disable SSL
echo "Creating/Updating 'lab' realm..."
kubectl exec -i $POD_NAME -- $KC_ADM create realms -s realm=lab -s enabled=true -s sslRequired=NONE || \
kubectl exec -i $POD_NAME -- $KC_ADM update realms/lab -s enabled=true -s sslRequired=NONE

# 4. Create OAuth2-Proxy Client
echo "Creating 'oauth2-proxy' client..."
kubectl exec -i $POD_NAME -- $KC_ADM create clients -r lab \
  -s clientId=oauth2-proxy \
  -s enabled=true \
  -s 'redirectUris=["http://lab.40.233.98.237.sslip.io/oauth2/callback"]' \
  -s secret=eRRhRnBEPzKauIIVVtn0gisSFTuQtqS \
  -s protocol=openid-connect \
  -s publicClient=false \
  -s directAccessGrantsEnabled=true

# 5. Create Test User
echo "Creating test user 'user'..."
kubectl exec -i $POD_NAME -- $KC_ADM create users -r lab -s username=user -s enabled=true
kubectl exec -i $POD_NAME -- $KC_ADM set-password -r lab --username user --new-password password

echo "Keycloak configuration complete."
