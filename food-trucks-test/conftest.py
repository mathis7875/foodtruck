import pytest
import subprocess
import os
import time
import socket

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@pytest.fixture(scope="session", autouse=True)
def build_and_run_docker():
    image_name = "foodtrucksapi"
    container_name = "foodtrucks-container"
    
    # 1. PATH VALIDATION (The most likely culprit)
    # Since this is in the root, it looks for the 'data' folder in the root.
    csv_path = os.path.join(os.getcwd(), "data", "Mobile_Food_Facility_Permit.csv")
    if not os.path.exists(csv_path):
        pytest.exit(f"\nFILE NOT FOUND: {csv_path}\nMake sure your CSV is inside a folder named 'data'.")

    # 2. CLEANUP
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    
    # 3. BUILD
    print(f"\n🚀 Building Docker image from: {os.getcwd()}")
    # We remove 'capture_output' here so you can see the REAL error in the terminal
    result = subprocess.run(["docker", "build", "-t", image_name, "."])
    
    if result.returncode != 0:
        pytest.exit("\n Docker build failed. Look at the red text above to see why.")

    # 4. RUN
    subprocess.run([
        "docker", "run", "-d", "--name", container_name, "-p", "5000:5000", image_name
    ], check=True)

    # 5. WAIT
    print("⏳ Waiting for port 5000...")
    for _ in range(20):
        if is_port_open(5000):
            print("API is online!")
            time.sleep(2)
            break
        time.sleep(1)
    else:
        pytest.exit("\n Timeout: Port 5000 never opened.")

    yield