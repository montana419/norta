import json
import logging
from typing import Dict, Any, Callable, List, Optional

# Import DAL module
import database as db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SkillsRegistry")


class SkillsRegistry:
    """Central registry for AI Agent skills, exposing executable functions 
    and generating LLM tool schemas.
    """

    def __init__(self):
        self._skills: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._register_default_skills()

    def register_skill(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        """Registers a Python function as an executable agent skill with JSON schema metadata."""
        self._skills[name] = func
        self._schemas[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        logger.debug(f"Registered skill: {name}")

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Returns all registered skill schemas in OpenAI function-calling format."""
        return list(self._schemas.values())

    def execute_skill(self, name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a registered skill safely by name with provided arguments."""
        if name not in self._skills:
            logger.error(f"Attempted execution of unknown skill: {name}")
            return {
                "status": "error",
                "message": f"Skill '{name}' is not registered in the registry."
            }

        try:
            logger.info(f"Executing skill '{name}' with params: {kwargs}")
            result = self._skills[name](**kwargs)
            return {
                "status": "success",
                "skill": name,
                "data": result
            }
        except Exception as e:
            logger.exception(f"Error executing skill '{name}': {str(e)}")
            return {
                "status": "error",
                "skill": name,
                "message": str(e)
            }

    def _register_default_skills(self):
        """Registers active database DAL services as callable agent skills."""

        # ---------------------------------------------------------
        # 1. CLIENT SKILLS
        # ---------------------------------------------------------
        self.register_skill(
            name="register_or_get_client",
            description="Register a new client account or retrieve an existing client by name or wallet address.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The client or business name."},
                    "wallet_address": {"type": "string", "description": "The EVM wallet address for the client."}
                },
                "required": ["name", "wallet_address"]
            },
            func=db.register_or_get_client
        )

        # ---------------------------------------------------------
        # 2. TASK MANAGEMENT SKILLS
        # ---------------------------------------------------------
        self.register_skill(
            name="add_task",
            description="Create and assign a task to a specific client.",
            parameters={
                "type": "object",
                "properties": {
                    "client_name": {"type": "string", "description": "Client name assigning the task."},
                    "title": {"type": "string", "description": "Task description or title."},
                    "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Urgent"], "default": "Medium"}
                },
                "required": ["client_name", "title"]
            },
            func=db.add_task
        )

        self.register_skill(
            name="get_tasks",
            description="Retrieve tasks, optionally filtered by client name.",
            parameters={
                "type": "object",
                "properties": {
                    "client_name": {"type": "string", "description": "Optional client name to filter tasks."}
                }
            },
            func=db.get_tasks
        )

        # ---------------------------------------------------------
        # 3. EMPLOYEE MANAGEMENT SKILLS
        # ---------------------------------------------------------
        self.register_skill(
            name="register_employee",
            description="Register a new employee/contractor under a client.",
            parameters={
                "type": "object",
                "properties": {
                    "client_name": {"type": "string", "description": "Client name employing the individual."},
                    "name": {"type": "string", "description": "Employee or contractor full name."},
                    "role": {"type": "string", "description": "Job title or role description."},
                    "salary": {"type": "number", "description": "Payout salary or wage amount."},
                    "wallet_address": {"type": "string", "description": "EVM wallet address."}
                },
                "required": ["client_name", "name", "role", "salary", "wallet_address"]
            },
            func=db.register_employee
        )

        self.register_skill(
            name="get_all_employees",
            description="Fetch a list of all registered employees, optionally filtered by client name.",
            parameters={
                "type": "object",
                "properties": {
                    "client_name": {"type": "string", "description": "Optional client name filter."}
                }
            },
            func=db.get_all_employees
        )

        self.register_skill(
            name="resolve_employee",
            description="Search and resolve an employee by numeric ID, full/partial name, or EVM wallet address.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query: Employee ID, name, or 0x wallet address."},
                    "client_name": {"type": "string", "description": "Optional client name to narrow search context."}
                },
                "required": ["query"]
            },
            func=db.resolve_employee
        )


# Global singleton instance
registry = SkillsRegistry()


if __name__ == "__main__":
    db.init_db()
    schemas = registry.get_tool_schemas()
    print(f"Registered {len(schemas)} skills successfully.")
    print("Registered Skill Names:", [s["function"]["name"] for s in schemas])