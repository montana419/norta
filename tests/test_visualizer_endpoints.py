# tests/test_visualizer_endpoints.py
from fastapi.testclient import TestClient
from main import app
import database

client = TestClient(app)

def test_visual_employee_list():
    # Setup data
    client.post("/employees/register", json={"name": "Alice", "role": "CTO", "salary": 200000.0, "wallet_address": "0x123...abc"})
    client.post("/employees/register", json={"name": "Bob", "role": "CFO", "salary": 180000.0, "wallet_address": "0x456...def"})

    # Test visual endpoint
    response = client.get("/employees/directory/image")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["type"] == "employee_list"
    assert data["image_base64"] is not None # Core Verification
    assert data["image_base64"].startswith("iVBORw0KGgo") # PNG structure check


def test_visual_invoice_on_payment():
    # Setup data
    reg_res = client.post("/employees/register", json={"name": "Charlie", "role": "Frontend", "salary": 110000.0, "wallet_address": "0x789...ghi"})
    emp_id = reg_res.json()["employee_id"]

    # Test payment/invoice endpoint
    response = client.post("/employees/pay-salary/image", json={"employee_id": emp_id})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["type"] == "invoice"
    assert data["image_base64"] is not None
    assert f"paid to Charlie" in data["description"]


def test_visual_treasury_charts():
    # Setup finance data
    client.post("/finance/log", json={"trans_type": "INCOME", "amount": 1000000.0, "category": "Series A"})
    client.post("/finance/log", json={"trans_type": "EXPENSE", "amount": 350000.0, "category": "Operation Cost"})

    # Test financial charts endpoint
    response = client.get("/finance/treasury-position/image")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["type"] == "treasury_summary"
    assert data["image_base64"] is not None


def test_visual_task_list():
    # Setup task data
    client.post("/tasks/add", json={"title": "Prepare Board Deck", "priority": "High"})
    client.post("/tasks/add", json={"title": "Launch v2.1 Staging", "priority": "Medium"})
    client.post("/tasks/add", json={"title": "Review Marketing Strategy", "priority": "Low"})

    # Test task visualization endpoint
    response = client.get("/tasks/list/image")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["type"] == "task_list"
    assert data["image_base64"] is not None