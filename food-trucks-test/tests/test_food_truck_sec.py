import os
import requests
import pytest
import allure

# Constants for the security tests
VALID_HEADERS = {"X-API-KEY": "test-key-123"}
INVALID_HEADERS = {"X-API-KEY": "wrong-secret-key"}

def get_endpoint():
    """Selects the correct endpoint based on the execution environment."""
    if os.path.exists('/.dockerenv'):
        # Container-to-container networking
        return "http://mock-provider:8080/external-check/truck-permit-status"
    # Local Mac host networking
    return "http://localhost:8081/external-check/truck-permit-status"

@allure.feature("Infrastructure")
@allure.story("Security")
def test_mock_unauthorized_access():
    """
    Scenario: Missing API Key
    Result: 401 Unauthorized
    """
    endpoint = get_endpoint()
    
    with allure.step("Attempting GET request without X-API-KEY header"):
        # We send NO headers here
        response = requests.get(endpoint, timeout=5)
        
        # Verify the mock blocks the request
        assert response.status_code == 401, f"Expected 401 but got {response.status_code}"
        assert "Unauthorized" in response.text

@allure.feature("Infrastructure")
@allure.story("Security")
def test_mock_invalid_token():
    """
    Scenario: Provided API Key is incorrect
    Result: 401 Unauthorized or 404 Not Found
    """
    endpoint = get_endpoint()
    
    with allure.step("Attempting GET request with an invalid API Key"):
        response = requests.get(endpoint, headers=INVALID_HEADERS, timeout=5)
        
        # WireMock returns 404 if a header value doesn't match a specific mapping
        # but 401 if it's explicitly told to reject. We accept both as 'Blocked'.
        assert response.status_code in [401, 404], f"Expected security rejection but got {response.status_code}"

@allure.feature("Infrastructure")
@allure.story("Security")
def test_mock_authorized_access():
    """
    Scenario: Valid API Key provided
    Result: 200 OK
    """
    endpoint = get_endpoint()
    
    with allure.step("Attempting GET request with valid X-API-KEY"):
        response = requests.get(endpoint, headers=VALID_HEADERS, timeout=5)
        
        # This confirms that the security layer allows valid traffic through
        assert response.status_code == 200
        assert response.json()["status"] == "ACTIVE"