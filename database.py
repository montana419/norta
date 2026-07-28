import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("Database")

# Get Neon PostgreSQL connection string
DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    """Returns a connection to Neon PostgreSQL using dictionary-like row formatting."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is missing from your .env file!")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    """Initializes PostgreSQL database tables for employees and tasks."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Employees table schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    client_name VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    role VARCHAR(255) NOT NULL,
                    salary NUMERIC DEFAULT 0.0,
                    chain_id VARCHAR(50) DEFAULT '1952'
                );
            """)

            # Tasks table schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    client_name VARCHAR(255) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    priority VARCHAR(50) DEFAULT 'Medium'
                );
            """)
            conn.commit()
    logger.info("Neon PostgreSQL tables initialized successfully.")


# --- EMPLOYEE OPERATIONS ---

def register_employee(
    client_name: str,
    name: str,
    role: str,
    salary: float,
    chain_id: str = "1952",
) -> int:
    """Registers a new employee and returns their inserted database ID."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO employees (client_name, name, role, salary, chain_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (client_name, name, role, salary, chain_id))
            employee_id = cursor.fetchone()['id']
            conn.commit()
            return employee_id


def resolve_employee(query: str, client_name: str = "Default Client") -> Optional[Dict[str, Any]]:
    """Resolves an employee by ID or partial/full name match."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            if str(query).isdigit():
                cursor.execute("""
                    SELECT * FROM employees WHERE id = %s AND client_name = %s;
                """, (int(query), client_name))
            else:
                cursor.execute("""
                    SELECT * FROM employees WHERE LOWER(name) LIKE LOWER(%s) AND client_name = %s;
                """, (f"%{query}%", client_name))

            row = cursor.fetchone()
            return dict(row) if row else None


def get_all_employees(client_name: str = "Default Client") -> List[Dict[str, Any]]:
    """Fetches all registered employees for a specific client."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM employees WHERE client_name = %s;", (client_name,))
            return [dict(row) for row in cursor.fetchall()]


def get_employees_by_client(client_name: str) -> List[Dict[str, Any]]:
    """Alias for get_all_employees."""
    return get_all_employees(client_name)


# --- TASK OPERATIONS ---

def add_task(client_name: str, title: str, priority: str = "Medium") -> str:
    """Adds a new task for the given client to the database."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tasks (client_name, title, priority)
                VALUES (%s, %s, %s);
            """, (client_name, title, priority))
            conn.commit()
            return f"Task '{title}' added successfully with priority '{priority}'."


def get_tasks(client_name: str = "Default Client") -> List[Dict[str, Any]]:
    """Retrieves all active tasks for a specific client."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks WHERE client_name = %s;", (client_name,))
            return [dict(row) for row in cursor.fetchall()]