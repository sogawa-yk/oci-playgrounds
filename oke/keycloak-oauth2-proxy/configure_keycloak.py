import requests
import json
import sys

BASE_URL = "http://localhost:8080/auth"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"

def get_admin_token():
    url = f"{BASE_URL}/realms/master/protocol/openid-connect/token"
    payload = {
        "client_id": "admin-cli",
        "username": ADMIN_USER,
        "password": ADMIN_PASS,
        "grant_type": "password"
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def create_realm(token, realm_name):
    url = f"{BASE_URL}/admin/realms"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # Check if realm exists
    check = requests.get(f"{url}/{realm_name}", headers=headers)
    if check.status_code == 200:
        print(f"Realm {realm_name} already exists.")
        return

    payload = {
        "realm": realm_name,
        "enabled": True
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Realm {realm_name} created.")
    else:
        print(f"Failed to create realm: {response.text}")
        sys.exit(1)

def create_client(token, realm_name, client_id, client_secret):
    url = f"{BASE_URL}/admin/realms/{realm_name}/clients"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Check if client exists to avoid duplicates (need to list or get by query)
    # Simple check: Try to create and catch 409
    
    payload = {
        "clientId": client_id,
        "enabled": True,
        "clientAuthenticatorType": "client-secret",
        "secret": client_secret,
        "serviceAccountsEnabled": True,
        "standardFlowEnabled": True,
        "directAccessGrantsEnabled": True,
        "redirectUris": ["*"],
        "webOrigins": ["*"],
        "publicClient": False,
        "protocol": "openid-connect"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Client {client_id} created.")
    elif response.status_code == 409:
        print(f"Client {client_id} already exists.")
    else:
        print(f"Failed to create client: {response.text}")
        sys.exit(1)

def create_user(token, realm_name, username, password):
    url = f"{BASE_URL}/admin/realms/{realm_name}/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Check if user exists
    search = requests.get(f"{url}?username={username}", headers=headers)
    if search.json():
        print(f"User {username} already exists.")
        return

    payload = {
        "username": username,
        "enabled": True,
        "firstName": "Demo",
        "lastName": "User",
        "credentials": [{
            "type": "password",
            "value": password,
            "temporary": False
        }]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"User {username} created.")
    else:
        print(f"Failed to create user: {response.text}")

if __name__ == "__main__":
    try:
        token = get_admin_token()
        create_realm(token, "lab")
        create_client(token, "lab", "oauth2-proxy", "eRRhRnBEPzKauIIVVtn0gisSFTuQtqS")
        create_user(token, "lab", "user", "password")
        print("Keycloak configuration completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
