import base64
import os
import subprocess
import sys

from cli_parser import parse_user_intent
from database import (
    add_task,
    get_all_employees,
    get_tasks,
    init_db,
    register_employee,
    resolve_employee,
)

import visualizer  # Imports matplotlib rendering tools

# ANSI Colors for clean CLI formatting
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    print(f"{CYAN}{BOLD}")
    print("==================================================")
    print("        🤖 ATLAS AGENT — CLI TERMINAL            ")
    print("==================================================")
    print(f"{RESET}")


def save_and_open_image(b64_string: str, filename: str):
    """Decodes a base64 string, saves it locally, and opens it using the default system viewer."""
    if not b64_string:
        print(f"{RED}⚠️ No image data was generated.{RESET}")
        return

    filepath = os.path.abspath(filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(b64_string))

    print(f"{GREEN}✅ Saved visual graphic to: {filepath}{RESET}")

    try:
        if sys.platform.startswith("darwin"):  # macOS
            subprocess.run(["open", filepath], check=False)
        elif sys.platform.startswith("win"):  # Windows
            os.startfile(filepath)
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.run(["xdg-open", filepath], check=False)
    except Exception as e:
        print(f"{YELLOW}ℹ️ Image saved. Open manually at: {filepath}{RESET}")


def menu_add_task(client_name: str = "Default Client"):
    """Interactive menu prompt to add a task directly."""
    print(f"\n{BOLD}--- 📝 Add New Task ({client_name}) ---{RESET}")
    title = input("Enter Task Title: ").strip()
    if not title:
        print(f"{RED}❌ Task title cannot be empty!{RESET}")
        return

    print("Select Priority:")
    print("  [1] Low")
    print("  [2] Medium")
    print("  [3] High")
    print("  [4] Critical")
    priority_choice = input("Choice (1-4, default 2): ").strip()

    priority_map = {"1": "Low", "2": "Medium", "3": "High", "4": "Critical"}
    priority = priority_map.get(priority_choice, "Medium")

    try:
        res = add_task(client_name=client_name, title=title, priority=priority)
        print(f"{GREEN}✅ {res}{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error adding task: {e}{RESET}")


def menu_add_employee(client_name: str = "Default Client"):
    """Interactive menu prompt to register a new employee."""
    print(f"\n{BOLD}--- 👥 Register New Employee ({client_name}) ---{RESET}")
    name = input("Enter Full Name (e.g. Sarah Connor): ").strip()
    if not name:
        print(f"{RED}Name is required!{RESET}")
        return

    role = input("Enter Role/Position (e.g. Smart Contract Auditor): ").strip()
    salary_str = input("Enter Monthly Salary in USD (default 6500): ").strip()
    salary = float(salary_str) if salary_str else 6500.0

    try:
        emp_id = register_employee(
            client_name=client_name,
            name=name,
            role=role,
            salary=salary,
        )
        print(f"{GREEN}✅ Registered '{name}' (ID: {emp_id}){RESET}")
    except Exception as e:
        print(f"{RED}❌ Error adding employee: {e}{RESET}")


def view_task_list(client_name: str = "Default Client"):
    """Displays active tasks in text format and offers Matplotlib visualization."""
    print(f"\n{BOLD}--- 📋 Task List ({client_name}) ---{RESET}")
    tasks = get_tasks(client_name)

    if not tasks:
        print(f"{YELLOW}(No active tasks found){RESET}")
        return

    print(f"{CYAN}[ Active Tasks ]{RESET}")
    for t in tasks:
        task_id = t.get("id", "N/A")
        print(
            f"  • ID: {task_id} | Priority: {t['priority']} | Title: {t['title']}"
        )

    choice = (
        input(f"\nRender and open color-coded task image? (y/N): ")
        .strip()
        .lower()
    )
    if choice == "y":
        try:
            img_b64 = visualizer.generate_task_list_image(
                tasks, client_name=client_name
            )
            save_and_open_image(img_b64, "task_list.png")
        except Exception as e:
            print(f"{RED}❌ Error generating task graphic: {e}{RESET}")


def view_employee_directory(client_name: str = "Default Client"):
    """Displays registered personnel in text format and offers Matplotlib visualization."""
    print(f"\n{BOLD}--- 👥 Employee Directory ({client_name}) ---{RESET}")
    employees = get_all_employees(client_name)

    if not employees:
        print(f"{YELLOW}(No employees registered yet){RESET}")
        return

    print(f"{CYAN}[ Personnel Records ]{RESET}")
    for emp in employees:
        print(
            f"  • ID: {emp['id']} | Name: {emp['name']} | Role: {emp['role']} | Salary: ${emp.get('salary', 0):,.2f}"
        )

    choice = (
        input(f"\nRender and open employee directory table image? (y/N): ")
        .strip()
        .lower()
    )
    if choice == "y":
        try:
            img_b64 = visualizer.generate_employee_list_image(
                employees, client_name=client_name
            )
            save_and_open_image(img_b64, "employee_directory.png")
        except Exception as e:
            print(f"{RED}❌ Error generating directory graphic: {e}{RESET}")


def menu_view_db(client_name: str = "Default Client"):
    """Full database overview menu option."""
    print(f"\n{BOLD}--- 📊 Live Database State ({client_name}) ---{RESET}")

    employees = get_all_employees(client_name)
    print(f"\n{CYAN}[ Registered Employees ({len(employees)}) ]{RESET}")
    if employees:
        for emp in employees:
            print(
                f"  • ID: {emp['id']} | Name: {emp['name']} | Role: {emp['role']} | Salary: ${emp.get('salary', 0):,.2f}"
            )
    else:
        print("  (No employees registered yet)")

    tasks = get_tasks(client_name)
    print(f"\n{CYAN}[ Pending Tasks ({len(tasks)}) ]{RESET}")
    if tasks:
        for t in tasks:
            print(
                f"  • ID: {t.get('id', 'N/A')} | Priority: {t['priority']} | Title: {t['title']}"
            )
    else:
        print("  (No tasks found)")


def process_natural_language(prompt: str, client_name: str = "Default Client"):
    print(f"\n{YELLOW}⚡ Parsing intent with Gemini...{RESET}")
    try:
        plan = parse_user_intent(prompt, client_name=client_name)
        print(f"\n{BOLD}🎯 Extracted Actions & Execution:{RESET}")

        for action in plan.actions:
            act_type = action.action

            if act_type == "add_task":
                title = getattr(action, "title", "Untitled Task")
                priority = getattr(action, "priority", "Medium")
                res = add_task(
                    client_name=client_name, title=title, priority=priority
                )
                print(
                    f"  📋 {BOLD}ADD TASK{RESET} -> Title: '{title}' (Priority: {priority})"
                )
                print(f"     {GREEN}└─ {res}{RESET}")

            elif act_type == "list_tasks":
                view_task_list(client_name)

            elif act_type == "register_employee":
                emp_name = getattr(action, "name", "New Employee")
                emp_role = getattr(action, "role", "Contractor")
                emp_salary = getattr(action, "salary", 5000.0)

                emp_id = register_employee(
                    client_name=client_name,
                    name=emp_name,
                    role=emp_role,
                    salary=emp_salary,
                )
                print(
                    f"  👤 {BOLD}REGISTER EMPLOYEE{RESET} -> {emp_name} ({emp_role})"
                )
                print(
                    f"     {GREEN}└─ Registered ID {emp_id} | Salary: ${emp_salary:.2f}{RESET}"
                )

            elif act_type == "list_employees":
                view_employee_directory(client_name)

            elif act_type == "view_database":
                menu_view_db(client_name)

            elif act_type == "general_chat":
                reply = getattr(
                    action, "reply", "How can I assist you today?"
                )
                print(f"  💬 {BOLD}CHAT RESPONSE{RESET}: {reply}")

    except Exception as e:
        print(f"{RED}❌ Error processing command: {e}{RESET}")


def main():
    init_db()
    print_banner()

    print(f"{BOLD}--- Startup Configuration ---{RESET}")
    active_client = input(
        "Enter Active Client Name (or press Enter for 'Default Client'): "
    ).strip()
    if not active_client:
        active_client = "Default Client"

    while True:
        print(f"\n{BOLD}Choose an option [{active_client}]:{RESET}")
        print("  [1] View Task List")
        print("  [2] View Employee Directory")
        print("  [3] View Full Database State")
        print("  [4] Register New Employee / Contractor")
        print("  [5] Add New Task")
        print("  [6] Run Natural Language Prompt")
        print("  [7] Exit")

        choice = input("\nEnter choice (1-7): ").strip()

        if choice == "1":
            view_task_list(active_client)

        elif choice == "2":
            view_employee_directory(active_client)

        elif choice == "3":
            menu_view_db(active_client)

        elif choice == "4":
            menu_add_employee(active_client)

        elif choice == "5":
            menu_add_task(active_client)

        elif choice == "6":
            prompt = input(
                "\n💬 Enter command (e.g. 'Show Sarah Connor details and list tasks'): "
            ).strip()
            if prompt:
                process_natural_language(prompt, active_client)

        elif choice == "7":
            print(f"\n{CYAN}Goodbye! 👋{RESET}")
            sys.exit(0)

        else:
            print(f"{RED}Invalid option, try again.{RESET}")


if __name__ == "__main__":
    main()