# tests/test_cli_parser.py

import pytest
from cli_parser import parse_user_intent
from schemas import IntentPlan, AddTaskIntent, LogFinanceIntent, GeneralChatIntent

def test_parse_task_intent():
    prompt = "Add a high priority task to prepare board slides"
    plan = parse_user_intent(prompt)
    
    assert isinstance(plan, IntentPlan)
    assert len(plan.actions) >= 1
    
    task_action = plan.actions[0]
    assert task_action.action == "add_task"
    assert "board slides" in task_action.title.lower()
    assert task_action.priority == "High"

def test_parse_finance_intent():
    prompt = "Log $500 spent on marketing ads"
    plan = parse_user_intent(prompt)
    
    assert isinstance(plan, IntentPlan)
    assert len(plan.actions) >= 1
    
    finance_action = plan.actions[0]
    assert finance_action.action == "log_finance"
    assert finance_action.amount == 500.0
    assert finance_action.trans_type == "EXPENSE"

def test_parse_unmapped_general_chat_intent():
    prompt = "How should I structure founder vesting schedules?"
    plan = parse_user_intent(prompt)
    
    assert isinstance(plan, IntentPlan)
    assert len(plan.actions) >= 1
    
    chat_action = plan.actions[0]
    assert chat_action.action == "general_chat"
    assert len(chat_action.reply) > 0

def test_parse_multi_intent():
    prompt = "Add a high priority task to check server logs, then show my current tasks"
    plan = parse_user_intent(prompt)
    
    assert isinstance(plan, IntentPlan)
    assert len(plan.actions) == 2
    assert plan.actions[0].action == "add_task"
    assert plan.actions[1].action == "list_tasks"