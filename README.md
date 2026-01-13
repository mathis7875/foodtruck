# 🚚 SF Food Truck API - Test Suite & Search Engine

This project provides a **.NET 8 Web API** (containerized via Docker) that parses San Francisco Mobile Food Facility permit data. It includes a comprehensive **Python Pytest** suite with **Allure Reporting** and **Performance Testing**.

---

## 🏗 Project Architecture

* **API:** .NET 8 Minimal API (Runs inside Docker).
* **Data Source:** `Mobile_Food_Facility_Permit.csv` (San Francisco Open Data).
* **Tests:** Python 3.9+ using `pytest`, `requests`, and `allure-pytest`.
* **Environment:** Managed via `.env` file for easy configuration.

---

## 🚀 Setup Instructions

### 1. Prerequisites

* **Docker Desktop** (Installed and running).
* **Python 3.9+** (With a virtual environment).
* **Allure Commandline:**
* **macOS:** `brew install allure`
* **Windows:** `scoop install allure` or manual download from [Allure GitHub](https://github.com/allure-framework/allure2/releases).
* **Clone project to local**** :  git clone



### 2. Environment Configuration (`.env`)

Create a `.env` file in the root directory. This tells the Python tests where the API is hosted:

```text
API_BASE_URL=http://localhost:5000

```

### 3. The Data File

Ensure your CSV is located at: `./data/Mobile_Food_Facility_Permit.csv`.
The API specifically maps the following columns:

* `Applicant` → `applicant` (JSON)
* `Address` → `address` (JSON)
* `LocationDescription` → `locationDescription` (JSON)

---

## 🐳 Docker Configuration (Cross-Platform)

The **Dockerfile** uses a multi-stage build to keep the image lean.

### 🖥️ CPU Architecture Note (macOS arm64 vs. Windows x86)

Docker handles architecture translation automatically most of the time, but for the best performance:

* **macOS (Apple Silicon M1/M2/M3):** Docker uses `linux/arm64`. The `.NET 8` image supports this natively.
* **Windows / Older Macs:** Docker uses `linux/amd64`.

**To ensure you build for the correct platform specifically:**

```bash
# For Apple Silicon (M1/M2/M3):
docker build --platform linux/arm64 -t food-truck-api .

# For Windows/Intel Macs:
docker build --platform linux/amd64 -t food-truck-api .

```

**Run the container:**

```bash
docker run -d -p 5000:5000 --name food-truck-container food-truck-api

```

---

## 🧪 Running Tests & Allure Reports

### 1. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install pytest requests python-dotenv allure-pytest

```

### 2. Execute Tests

Run all functional and performance tests while generating Allure results:

```bash
pytest tests/ -v --alluredir=allure-results

```

### 3. Generate & View Allure Report

This command processes the raw data and opens an interactive dashboard in your browser:

```bash
allure serve allure-results

```

---

## 🛠 Troubleshooting

| Issue | Solution |
| --- | --- |
| **ConnectionError** | Ensure Docker is running and port 5000 is mapped (`-p 5000:5000`). |
| **KeyError: 'applicant'** | Ensure the API is returning camelCase. Check the Dockerfile's `Program.cs`. |
| **NotOpenSSLWarning** | Run `pip install "urllib3<2.0"` to resolve macOS LibreSSL conflicts. |
| **Allure command not found** | Ensure you ran `brew install allure` and restarted your terminal. |

---
## 🧹 Code Quality (Linting)

To maintain high code quality, we use **Flake8** for linting and **Black** for formatting.

- **Check for style issues:**
  ```bash
  flake8 .
  
---

## 📊 Test Coverage Info

1. **Infrastructure (6 Tests):** Verifies Swagger UI, OpenAPI JSON, and static CSS assets.
2. **Data Validation (3 Tests):** Verifies search results against real CSV entries (e.g., "The Geez Freeze").
3. **Performance (3 Tests):** Checks API latency (under 500ms) and coordinate boundary validation (returns `400` for invalid Lat/Lon).


To make your project truly "interview-ready," your README should clearly explain the **Service Virtualization** (Mocking) aspect. This shows you understand how to test dependencies that aren't under your control.

Here is the updated **Mock Setup** section to add to your `README.md`.

---

## 🛠 Mock Server Setup (WireMock)

To simulate external third-party API dependencies (3rd party services), this project uses **WireMock**. This allows us to test how the API handles external successes, failures, and timeouts without needing a real internet connection.

### 1. Manual Setup (CLI)

If you are adding new mocks, ensure the following directory structure exists:

```bash
mkdir -p wiremock/mappings

```

### 2. Defining a "Stub"

Create a JSON file in `wiremock/mappings/` to define a canned response.
**Example:** `wiremock/mappings/truck_status.json`

```json
{
  "request": {
    "method": "GET",
    "url": "/external-check/truck-permit-status"
  },
  "response": {
    "status": 200,
    "body": "{ \"permit_valid\": true, \"status\": \"ACTIVE\" }",
    "headers": { "Content-Type": "application/json" }
  }
}

```

### 3. Running with the Mock Server

The mock server is integrated into the Docker Compose workflow. To start the API, the Mock Server, and the Tests all at once:

```bash
docker-compose up --build --exit-code-from tester

```

### 4. Verifying the Mock

You can verify that the mock server is healthy and see all registered "stubs" by visiting the WireMock admin panel while the containers are running:

* **Admin URL:** `http://localhost:8081/__admin`
* **Direct Mock Endpoint:** `http://localhost:8081/external-check/truck-permit-status`

---

## 🧪 Running Specific Tests

As a Lead QA, you might want to run only specific parts of the suite.

* **Run all tests:**
`docker-compose run tester pytest`
* **Run only Search tests:**
`docker-compose run tester pytest tests/test_food_trucks.py`
* **Run only Mock/Integration tests:**
`docker-compose run tester pytest tests/test_mock_integration.py`

To show that your framework is "enterprise-ready," adding a Database section to your **README.md** is a great touch. It signals to other engineers that the framework is designed for full E2E validation (API + DB).

Here is the section you can copy and paste into your README.

---

## Database Integration 

The framework includes a `SQLiteHelper` in `utils/db_helper.py` to perform data integrity checks directly against the database.

### 1. Connection Setup

To connect to a real SQLite database, ensure your `.db` file is placed in the `data/` directory. The helper defaults to looking for `food_trucks.db`.

```python
from utils.db_helper import SQLiteHelper

# Initialize the helper (defaults to environment variable DATABASE_PATH)
db = SQLiteHelper()

# Example: Verify a record exists after an API POST request
exists = db.verify_truck_exists("Nite Owl Food Truck")

```

### 2. Environment Configuration

If your database file is named differently or located elsewhere, set the `DATABASE_PATH` environment variable:

**Local (Mac/Windows):**

```bash
export DATABASE_PATH="./my_custom_db.sqlite"

```

**Docker Compose:**
The `tester` service is configured to mount the database volume. Ensure your `docker-compose.yml` includes:

```yaml
services:
  tester:
    volumes:
      - ./data:/tests/data
    environment:
      - DATABASE_PATH=/tests/data/food_trucks.db

```

### 3. Running Database Tests

Tests requiring a database are marked with `@pytest.mark.database`. By default, these are skipped if no database is detected. To run them:

```bash
pytest -m database
