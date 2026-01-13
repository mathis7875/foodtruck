import os
import requests
import pytest
import allure

# Global Configuration
VALID_HEADERS = {"X-API-KEY": "test-key-123"}
INVALID_HEADERS = {"X-API-KEY": "wrong-secret-key"}

def get_endpoint():
    """Detect if we are inside the Docker network or running on the Mac host."""
    if os.path.exists('/.dockerenv'):
        return "http://mock-provider:8080/external-check/truck-permit-status"
    return "http://localhost:8081/external-check/truck-permit-status"

# --- HAPPY PATH & SCHEMA TESTS ---

@allure.feature("Infrastructure")
@allure.story("Direct Mock Verification")
def test_mock_direct():
    """Verify the Happy Path with correct authorization."""
    endpoint = get_endpoint()
    
    with allure.step(f"Direct GET request to Mock: {endpoint}"):
        try:
            # Added headers=VALID_HEADERS so this passes the security layer
            response = requests.get(endpoint, headers=VALID_HEADERS, timeout=5)
            assert response.status_code == 200
            assert response.json()["status"] == "ACTIVE"
        except requests.exceptions.ConnectionError:
            pytest.fail(f"Connection failed at {endpoint}. Ensure 'docker-compose up mock-provider' is running.")

@allure.feature("Infrastructure")
@allure.story("Data Integrity")
def test_mock_schema_validation():
    """Verify that the mock response contains the exact contract fields."""
    endpoint = get_endpoint()
    with allure.step("Validating JSON Schema fields"):
        response = requests.get(endpoint, headers=VALID_HEADERS, timeout=5)
        data = response.json()
        
        assert response.status_code == 200
        assert "status" in data
        assert "permit_valid" in data
        assert isinstance(data["permit_valid"], bool)

# --- SECURITY TESTS ---

@allure.feature("Infrastructure")
@allure.story("Security")
def test_mock_unauthorized_access():
    """Verify the Mock rejects requests missing an API Key."""
    endpoint = get_endpoint()
    with allure.step("Requesting without headers"):
        response = requests.get(endpoint, timeout=5)
        # Should return 401 based on your security mapping
        assert response.status_code == 401

@allure.feature("Infrastructure")
@allure.story("Security")
def test_mock_invalid_token():
    """Verify the Mock rejects incorrect API Keys."""
    endpoint = get_endpoint()
    with allure.step("Requesting with incorrect API Key"):
        response = requests.get(endpoint, headers=INVALID_HEADERS, timeout=5)
        # WireMock may return 401 or 404 for unmatched headers; both are secure rejections
        assert response.status_code in [401, 404]

# --- NEGATIVE TESTING ---

@allure.feature("Infrastructure")
@allure.story("Negative Testing")
def test_mock_not_found():
    """Verify how the mock responds to an unregistered route."""
    base_url = get_endpoint().rsplit('/', 1)[0]
    endpoint = f"{base_url}/invalid-route-123"
    
    with allure.step(f"Checking invalid route: {endpoint}"):
        response = requests.get(endpoint, headers=VALID_HEADERS, timeout=5)
        assert response.status_code == 404