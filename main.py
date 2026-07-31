import logging
import os
from typing import Any, Dict, Optional, Set
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from google import genai
from google.genai import types

# --- Module Imports & Graceful Mock Fallbacks ---
try:
    import database
except ImportError:
    class MockDatabase:
        @staticmethod
        def resolve_employee(query: str, client_name: str) -> Optional[Dict[str, Any]]:
            return None

        @staticmethod
        def get_all_employees(client_name: str = "Default Client") -> list:
            return []

        @staticmethod
        def get_tasks(client_name: str = "Default Client") -> list:
            return []

        @staticmethod
        def add_task(client_name: str, title: str, priority: str = "Medium") -> str:
            return f"Task '{title}' added successfully."

        @staticmethod
        def register_employee(client_name: str, name: str, role: str, salary: float) -> str:
            return "emp_mock_123"

    database = MockDatabase()

try:
    import cli_parser
except ImportError:
    cli_parser = None

try:
    import visualizer
except ImportError:
    visualizer = None

# --- Configuration & Initialization ---
LLM_FALLBACK_STACK = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

logger = logging.getLogger("EmployeeManagement")

app = FastAPI(title="Atlas AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Explicit API Key Initialization for Free Tier ---
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    logger.warning("GEMINI_API_KEY environment variable is not set!")

# Passing api_key forces standard API Key auth instead of GCP OAuth credentials
client = genai.Client(api_key=api_key)

# In-memory registry for active client contexts
CLIENT_REGISTRY: Set[str] = {"fral", "Default Client"}


# --- Pydantic Schemas ---

class ClientCreateRequest(BaseModel):
    client_name: str

class TaskRequest(BaseModel):
    title: str
    priority: str = "Medium"
    client_name: str = "Default Client"

class EmployeeRequest(BaseModel):
    name: str
    role: str
    salary: float = 6500.0
    client_name: str = "Default Client"

class FinanceLogRequest(BaseModel):
    trans_type: str
    amount: float
    category: str
    description: str

class WellnessRequest(BaseModel):
    sleep_hours: float
    work_hours: float
    stress_level: int

class ChatRequest(BaseModel):
    prompt: str

class CommandRequest(BaseModel):
    prompt: str
    client_name: str = "Default Client"


# --- Client Management Endpoints ---

@app.get("/clients/list")
def list_clients():
    """Returns all registered client contexts."""
    return {"status": "success", "clients": sorted(list(CLIENT_REGISTRY))}

@app.post("/clients/create")
def create_client(data: ClientCreateRequest):
    """Registers a new client context dynamically."""
    name = data.client_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Client name cannot be empty.")
    
    CLIENT_REGISTRY.add(name)
    return {"status": "success", "message": f"Client '{name}' created.", "client_name": name}


# --- General & Database Endpoints ---

@app.get("/")
def read_root():
    return {"status": "Atlas API is active and listening"}

@app.post("/tasks/add")
def add_task_endpoint(data: TaskRequest):
    try:
        CLIENT_REGISTRY.add(data.client_name)
        res = database.add_task(
            client_name=data.client_name,
            title=data.title,
            priority=data.priority
        )
        return {
            "status": "success",
            "message": res,
            "task": data.model_dump()
        }
    except Exception as e:
        logger.error(f"Failed to add task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/list")
def list_tasks_endpoint(client_name: str = "Default Client"):
    try:
        CLIENT_REGISTRY.add(client_name)
        tasks = database.get_tasks(client_name=client_name)
        image_b64 = visualizer.generate_task_list_image(tasks, client_name=client_name) if visualizer else None
        
        return {
            "status": "success",
            "client_name": client_name,
            "tasks": tasks,
            "image": image_b64
        }
    except Exception as e:
        logger.error(f"Failed to fetch tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/employees/register")
def register_employee_endpoint(data: EmployeeRequest):
    """Registers a new employee and tracks the associated client without wallet_address."""
    try:
        CLIENT_REGISTRY.add(data.client_name)
        emp_id = database.register_employee(
            client_name=data.client_name,
            name=data.name,
            role=data.role,
            salary=data.salary
        )
        return {"status": "success", "employee_id": emp_id}
    except Exception as e:
        logger.error(f"Failed to register employee: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees/list")
def list_employees_endpoint(client_name: str = "Default Client"):
    try:
        CLIENT_REGISTRY.add(client_name)
        employees = database.get_all_employees(client_name=client_name)
        image_b64 = visualizer.generate_employee_list_image(employees, client_name=client_name) if visualizer else None

        return {
            "status": "success",
            "client_name": client_name,
            "employees": employees,
            "image": image_b64
        }
    except Exception as e:
        logger.error(f"Failed to fetch employees: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database/state")
def get_database_state(client_name: str = "Default Client"):
    try:
        CLIENT_REGISTRY.add(client_name)
        employees = database.get_all_employees(client_name=client_name)
        tasks = database.get_tasks(client_name=client_name)
        
        emp_img = visualizer.generate_employee_list_image(employees, client_name=client_name) if visualizer else None
        task_img = visualizer.generate_task_list_image(tasks, client_name=client_name) if visualizer else None

        return {
            "status": "success",
            "client_name": client_name,
            "state": {
                "employees": employees,
                "tasks": tasks
            },
            "images": {
                "employees": emp_img,
                "tasks": task_img
            }
        }
    except Exception as e:
        logger.error(f"Failed to fetch full database state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/command")
def process_agent_command(data: CommandRequest):
    if not cli_parser:
        raise HTTPException(status_code=500, detail="cli_parser module is not available.")
    
    try:
        CLIENT_REGISTRY.add(data.client_name)
        plan = cli_parser.parse_user_intent(data.prompt, client_name=data.client_name)
        executed_results = []

        for action in plan.actions:
            act_type = action.action

            if act_type == "add_task":
                title = getattr(action, "title", "Untitled Task")
                priority = getattr(action, "priority", "Medium")
                res = database.add_task(client_name=data.client_name, title=title, priority=priority)
                executed_results.append({"action": act_type, "result": res, "title": title, "priority": priority})

            elif act_type == "list_tasks":
                tasks = database.get_tasks(client_name=data.client_name)
                task_img = visualizer.generate_task_list_image(tasks, client_name=data.client_name) if visualizer else None
                executed_results.append({"action": act_type, "tasks": tasks, "image": task_img})

            elif act_type == "register_employee":
                emp_name = getattr(action, "name", "New Employee")
                emp_role = getattr(action, "role", "Contractor")
                emp_salary = getattr(action, "salary", 6500.0)
                emp_id = database.register_employee(
                    client_name=data.client_name,
                    name=emp_name,
                    role=emp_role,
                    salary=emp_salary
                )
                executed_results.append({"action": act_type, "employee_id": emp_id, "name": emp_name})

            elif act_type == "list_employees":
                employees = database.get_all_employees(client_name=data.client_name)
                emp_img = visualizer.generate_employee_list_image(employees, client_name=data.client_name) if visualizer else None
                executed_results.append({"action": act_type, "employees": employees, "image": emp_img})

            elif act_type == "view_database":
                employees = database.get_all_employees(client_name=data.client_name)
                tasks = database.get_tasks(client_name=data.client_name)
                emp_img = visualizer.generate_employee_list_image(employees, client_name=data.client_name) if visualizer else None
                task_img = visualizer.generate_task_list_image(tasks, client_name=data.client_name) if visualizer else None
                executed_results.append({
                    "action": act_type, 
                    "employees": employees, 
                    "tasks": tasks, 
                    "images": {"employees": emp_img, "tasks": task_img}
                })

            elif act_type == "general_chat":
                reply = getattr(action, "reply", "How can I assist you today?")
                executed_results.append({"action": act_type, "reply": reply})

        return {
            "status": "success",
            "prompt": data.prompt,
            "client_name": data.client_name,
            "actions_executed": executed_results
        }

    except Exception as e:
        logger.error(f"Failed to process agent command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)