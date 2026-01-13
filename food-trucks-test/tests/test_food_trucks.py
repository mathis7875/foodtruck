import pytest
import requests
import time
import os
import allure
from dotenv import load_dotenv
from utils.db_helper import SQLiteHelper

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

# --- INFRASTRUCTURE TESTS ---

@allure.feature("API Infrastructure")
@allure.story("Swagger UI Availability")
def test_swagger_ui_page_loads():
    """Verify the Swagger UI HTML page is accessible."""
    url = f"{BASE_URL}/swagger/"
    with allure.step(f"GET request to {url}"):
        try:
            response = None
            for i in range(10):  # Retry loop for container startup
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        break
                except requests.exceptions.ConnectionError:
                    time.sleep(1)
            
            assert response is not None and response.status_code == 200
            assert "Swagger UI" in response.text
            allure.attach(response.text, name="Swagger HTML", attachment_type=allure.attachment_type.HTML)
            print(f"\n🚀 API Online at: {BASE_URL}")
        except Exception as e:
            pytest.fail(f"Swagger UI Test failed: {e}")

@allure.feature("API Infrastructure")
@allure.story("OpenAPI Specification")
def test_openapi_spec_is_valid_json():
    """Verify that the openapi.json file is being served."""
    url = f"{BASE_URL}/swagger/v1/swagger.json" 
    with allure.step(f"Checking OpenAPI JSON at {url}"):
        try:
            response = requests.get(url, timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert "openapi" in data or "swagger" in data
            print("OpenAPI specification found!")
        except Exception as e:
            pytest.fail(f"OpenAPI Spec Test failed: {e}")

@allure.feature("API Infrastructure")
@allure.story("Endpoint Documentation")
def test_api_endpoints_are_documented():
    """Verify that the Swagger spec documents at least one path."""
    url = f"{BASE_URL}/swagger/v1/swagger.json"
    with allure.step("Verifying documented paths"):
        try:
            response = requests.get(url, timeout=5)
            paths = response.json().get("paths", {})
            assert len(paths) > 0
            print(f"Found {len(paths)} documented endpoints.")
        except Exception as e:
            pytest.fail(f"Documentation Test failed: {e}")

@allure.feature("API Infrastructure")
@allure.story("Static Assets")
def test_swagger_static_assets():
    """Verify that Swagger UI CSS assets are loading."""
    url = f"{BASE_URL}/swagger/swagger-ui.css"
    with allure.step("Checking CSS asset"):
        try:
            response = requests.get(url, timeout=5)
            assert response.status_code == 200
            assert "text/css" in response.headers.get("Content-Type", "")
            print("Static assets accessible.")
        except Exception as e:
            pytest.fail(f"Static Assets Test failed: {e}")

@allure.feature("API Infrastructure")
@allure.story("Endpoint Connectivity")
def test_search_endpoint_returns_data():
    """Check if search endpoint responds correctly to a basic name query."""
    url = f"{BASE_URL}/api/food_trucks/search?name=taco"
    with allure.step("Testing basic search connectivity"):
        try:
            response = requests.get(url, timeout=5)
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            print("Basic search endpoint functional.")
        except Exception as e:
            pytest.fail(f"Search endpoint check failed: {e}")

@allure.feature("API Infrastructure")
@allure.story("Metadata Validation")
def test_food_truck_data_is_accessible():
    """Verify the API metadata name in the spec."""
    url = f"{BASE_URL}/swagger/v1/swagger.json"
    with allure.step("Checking API Title in Spec"):
        try:
            response = requests.get(url, timeout=5)
            assert "FoodTruckApi" in response.text
            print("API Metadata verified.")
        except Exception as e:
            pytest.fail(f"Metadata check failed: {e}")

# --- DATA VALIDATION TESTS ---

@allure.feature("Food Truck Search")
@allure.story("Search by Name")
def test_search_by_name_exact_match():
    """Verify searching by name returns the correct applicant from CSV."""
    with allure.step("Querying name 'Geez Freeze'"):
        try:
            response = requests.get(f"{BASE_URL}/api/food_trucks/search?name=Geez Freeze", timeout=5)
            data = response.json()
            allure.attach(str(data), name="API Response", attachment_type=allure.attachment_type.JSON)
            
            assert len(data) > 0
            assert "The Geez Freeze" in data[0]['applicant']
            print(f"Data Match: Found {data[0]['applicant']}")
        except Exception as e:
            pytest.fail(f"Name data match failed: {e}")

@allure.feature("Food Truck Search")
@allure.story("Search by Street")
def test_search_by_street_query():
    """Verify filtering by street works against the Address column."""
    with allure.step("Querying street '18TH ST'"):
        try:
            response = requests.get(f"{BASE_URL}/api/food_trucks/search?street=18TH ST", timeout=5)
            data = response.json()
            assert len(data) > 0
            assert "18TH ST" in data[0]['address'].upper()
            print(f"Street Search Match: {data[0]['address']}")
        except Exception as e:
            pytest.fail(f"Street query failed: {e}")

@allure.feature("Food Truck Search")
@allure.story("Multi-parameter Search")
def test_combined_multi_param_query():
    """Verify combined filtering for name and street narrows results correctly."""
    with allure.step("Querying MOMO on CALIFORNIA ST"):
        try:
            url = f"{BASE_URL}/api/food_trucks/search?name=MOMO&street=CALIFORNIA"
            response = requests.get(url, timeout=5)
            data = response.json()
            assert len(data) > 0
            assert "MOMO" in data[0]['applicant'].upper()
            assert "CALIFORNIA" in data[0]['address'].upper()
            print(" Combined filtering verified!")
        except Exception as e:
            pytest.fail(f"Combined query failed: {e}")

@allure.feature("Food Truck Search")
@allure.story("Database query test")
@pytest.mark.skip(reason="Database infrastructure not yet implemented")
def test_truck_data_integrity():
    db = SQLiteHelper()
    
    # 1. Check DB directly
    trucks = db.execute_query("SELECT applicant FROM food_trucks LIMIT 1")
    truck_name = trucks[0]['applicant']            