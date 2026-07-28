import logging
import os
from typing import Any, Dict, Optional

# Attempt database import with a graceful fallback for local testing
try:
    import database
except ImportError:
    class MockDatabase:
        @staticmethod
        def resolve_employee(query: str, client_name: str) -> Optional[Dict[str, Any]]:
            return None

        @staticmethod
        def get_employees_by_client(client_name: str) -> list:
            return []

        @staticmethod
        def register_employee(client_name: str, name: str, role: str, salary: float) -> Dict[str, Any]:
            return {"status": "success", "message": f"Employee {name} registered."}

    database = MockDatabase()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EmployeeResolver")


def get_employee_info(client_name: str, employee_identifier: str) -> Dict[str, Any]:
    """
    Resolves employee info from the database without performing any wallet operations.
    """
    try:
        try:
            employee = database.resolve_employee(query=employee_identifier, client_name=client_name)
        except Exception as db_err:
            logger.error(f"DB lookup failed for employee '{employee_identifier}': {db_err}")
            employee = None

        if not employee:
            return {
                "status": "failed",
                "error": f"Execution Aborted: Employee '{employee_identifier}' not found for client '{client_name}'."
            }

        return {
            "status": "success",
            "client_name": client_name,
            "employee_name": employee.get("name", employee_identifier),
            "role": employee.get("role"),
            "salary": employee.get("salary")
        }

    except Exception as e:
        logger.error(f"Unhandled error during employee lookup: {e}")
        return {
            "status": "failed",
            "error": f"Lookup Exception: {str(e)}"
        }