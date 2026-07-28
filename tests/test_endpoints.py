# tests/test_endpoints.py

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_task():
    response = client.post("/tasks/add", json={"title": "Review Q3 deck", "priority": "High"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["agent"] == "Atlas"

def test_list_tasks():
    # First add a task
    client.post("/tasks/add", json={"title": "Write unit tests", "priority": "Medium"})
    
    # Then verify listing
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["tasks"], list)

def test_register_and_pay_employee():
    # Register employee
    reg_res = client.post("/employees/register", json={
        "name": "Alex Smith",
        "role": "Fullstack Engineer",
        "salary": 110000.0,
        "wallet_address": "0x71C...89"
    })
    assert reg_res.status_code == 200
    emp_id = reg_res.json().get("employee_id")
    assert emp_id is not None

    # Pay salary to registered employee
    pay_res = client.post("/employees/pay-salary", json={"employee_id": emp_id})
    assert pay_res.status_code == 200
    assert pay_res.json()["payout"]["execution"] == "EXECUTED"

def test_pay_nonexistent_employee():
    response = client.post("/employees/pay-salary", json={"employee_id": 99999})
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee record not found."

def test_log_finance():
    response = client.post("/finance/log", json={
        "trans_type": "EXPENSE",
        "amount": 450.0,
        "category": "Software",
        "description": "AWS Hosting"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_general_chat_endpoint(monkeypatch):
    """Mocks atlas_tools fallback response to test endpoint wiring cleanly."""
    class MockResponse:
        text = "This is a mocked Atlas general advice response."

    # Prevent calling live Gemini API during fast unit testing
    monkeypatch.setattr("atlas_tools.generate_content_with_fallback", lambda contents: MockResponse())

    response = client.post("/agent/chat", json={"prompt": "What's top of mind?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "mocked Atlas general advice" in data["response"]