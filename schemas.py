from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


class AddTaskIntent(BaseModel):
    action: Literal["add_task"] = "add_task"
    client_name: str = Field(description="The client name this task belongs to")
    title: str = Field(description="Brief summary of the task")
    priority: Literal["Low", "Medium", "High", "Urgent"] = Field(default="Medium")


class ListTasksIntent(BaseModel):
    action: Literal["list_tasks"] = "list_tasks"
    client_name: Optional[str] = Field(
        default=None, 
        description="Optional client name to filter the tasks by"
    )


class RegisterEmployeeIntent(BaseModel):
    action: Literal["register_employee"] = "register_employee"
    client_name: str = Field(description="The client employing the contractor/employee")
    name: str = Field(description="Full name of the employee or contractor")
    role: str = Field(description="Job title or role description")
    salary: float = Field(description="Agreed salary or payment amount")


class ListEmployeesIntent(BaseModel):
    action: Literal["list_employees"] = "list_employees"
    client_name: Optional[str] = Field(
        default=None,
        description="Optional client name to filter employee list by"
    )


class ViewDatabaseIntent(BaseModel):
    action: Literal["view_database"] = "view_database"
    client_name: Optional[str] = Field(
        default=None,
        description="Optional client name to inspect full database state for"
    )


class GeneralChatIntent(BaseModel):
    action: Literal["general_chat"] = "general_chat"
    reply: str = Field(description="Response to standard non-actionable chat")


# Union of all supported actions that the Agent can take
AgentAction = Union[
    AddTaskIntent, 
    ListTasksIntent, 
    RegisterEmployeeIntent,
    ListEmployeesIntent,
    ViewDatabaseIntent,
    GeneralChatIntent,
]


class IntentPlan(BaseModel):
    actions: List[AgentAction] = Field(
        description="Ordered list of actions to execute based on user request"
    )