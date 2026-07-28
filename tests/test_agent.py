# tests/test_agent.py
from unittest.mock import patch
import pytest
from agent import execute_user_request
from schemas import IntentPlan, AddTaskIntent, GeneralChatIntent

def test_execute_add_task():
    # Mock parse_user_intent to return an AddTaskIntent
    fake_plan = IntentPlan(actions=[
        AddTaskIntent(title="Prepare quarterly report", priority="High")
    ])

    with patch("agent.parse_user_intent", return_value=fake_plan), \
         patch("agent.add_task", return_value="Task added successfully"):
        
        results = execute_user_request("Add a high priority task to prepare quarterly report")
        
        assert len(results) == 1
        assert results[0]["action"] == "add_task"
        assert results[0]["status"] == "success"
        assert "success" in results[0]["message"].lower()


def test_execute_general_chat():
    fake_plan = IntentPlan(actions=[
        GeneralChatIntent(reply="Hello! How can I assist you today?")
    ])

    with patch("agent.parse_user_intent", return_value=fake_plan):
        results = execute_user_request("Hi there!")
        
        assert len(results) == 1
        assert results[0]["action"] == "general_chat"
        assert results[0]["content"] == "Hello! How can I assist you today?"