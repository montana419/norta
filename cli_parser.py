import logging
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
from schemas import IntentPlan

# Active Gemini models with fallback hierarchy
GEMINI_MODELS = [
    # Gemini 3 Series (Frontier)
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro",
    "gemini-3.1-flash-lite",
    "gemini-3-flash",
    # Gemini 2.5 Series Fallbacks
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]


def build_system_prompt(client_name: str = "Default Client") -> str:
    """Builds a client-aware system prompt covering all CLI functions."""
    return f"""
You are Atlas, a personal executive assistant operating on behalf of client '{client_name}'.
You analyze user prompts and map them into actionable database intents or structured general chat.

CRITICAL CONTEXT DIRECTIVES:
- The current operating client context is '{client_name}'.
- ALWAYS set `client_name` to '{client_name}' for any generated action unless a different client is explicitly named.
- NEVER default to general_chat if an actionable intent matches the user's intent.

Supported actions & trigger rules:
1. add_task(client_name, title, priority):
    * Trigger when creating, scheduling, or adding a task.
    * Priority options: "Low", "Medium", "High", "Critical".
2. list_tasks(client_name):
    * Trigger when viewing, showing, listing, or fetching active tasks, todos, or task lists.
3. register_employee(client_name, name, role, salary):
    * Trigger when onboarding, hiring, adding, or registering an employee or contractor.
    * name: Full name.
    * role: Position or title.
    * salary: Float value representing monthly compensation.
4. list_employees(client_name):
    * Trigger when viewing, listing, or showing employee directory, personnel records, or team members.
5. view_database(client_name):
    * Trigger when asking for full database state, live DB overview, total records, or summary of both employees and tasks.
6. general_chat(reply):
    * Conversational replies or general startup questions when no actionable intent applies.

For multi-part requests (e.g. "Register Sarah as Auditor for 5000 and show task list"), output multiple actions in logical execution order.
"""


def parse_user_intent(user_input: str, client_name: str = "Default Client") -> IntentPlan:
    """
    Parses natural language into structured execution intents using Gemini,
    falling back across Gemini model versions if an API error occurs.
    Scoped by client context.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Neither GEMINI_API_KEY nor GOOGLE_API_KEY environment variable is set.")

    client = genai.Client(api_key=api_key)
    system_prompt = build_system_prompt(client_name)
    last_exception = None

    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=IntentPlan,
                ),
            )
            return IntentPlan.model_validate_json(response.text)

        except APIError as e:
            logging.warning(
                f"API error with model '{model_name}': {e}. Trying fallback..."
            )
            last_exception = e
        except Exception as e:
            logging.warning(
                f"Unexpected error with model '{model_name}': {e}. Trying fallback..."
            )
            last_exception = e

    raise RuntimeError(
        f"All Gemini models in the fallback chain failed. Last error: {last_exception}"
    ) from last_exception