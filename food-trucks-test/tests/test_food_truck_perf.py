import pytest
import requests
import os
import allure
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

@allure.feature("Performance & Edge Cases")
class TestFoodTrucksExtended:

    @allure.story("Coordinate Boundary Testing")
    @pytest.mark.parametrize("lat, lon, expected_status", [
        (90.0, 180.0, 200),
        (-90.0, -180.0, 200),
        (90.1, 0, 400),   # Expecting 400 Bad Request
        (0, 180.1, 400)   # Expecting 400 Bad Request
    ])
    def test_coordinate_boundaries(self, lat, lon, expected_status):
        url = f"{BASE_URL}/api/food_trucks/search?lat={lat}&lon={lon}"
        with allure.step(f"Testing coordinates: {lat}, {lon}"):
            try:
                response = requests.get(url, timeout=5)
                allure.attach(f"Status: {response.status_code}\nBody: {response.text}", 
                              name="API Response", attachment_type=allure.attachment_type.TEXT)
                assert response.status_code == expected_status
            except Exception as e:
                pytest.fail(f"Boundary test failed: {e}")

    @allure.story("Latency Threshold")
    def test_api_latency_threshold(self):
        url = f"{BASE_URL}/api/food_trucks/search?name=taco"
        try:
            response = requests.get(url, timeout=1)
            latency = response.elapsed.total_seconds() * 1000
            assert latency < 500 # Increased slightly for local Docker variance
        except Exception as e:
            pytest.fail(f"Latency test failed: {e}")

    @allure.story("Character Encoding")
    def test_non_ascii_search(self):
        try:
            response = requests.get(f"{BASE_URL}/api/food_trucks/search?name=José")
            assert response.status_code == 200
        except Exception as e:
            pytest.fail(f"Encoding test failed: {e}")