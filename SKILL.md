---
name: atlas_agent
description: Personal assistant and startup executive manager. Use when the user requests task scheduling, payroll disbursements, founder wellness routines, or treasury overview.
license: MIT
compatibility: Python >= 3.10, Streamlit, Google Gemini API
metadata:
  author: AtlasAI Team
  version: "1.0.0"
  category: Executive Assistant & Treasury
---

# Atlas Founder Agent Skill

## Overview
Atlas is an AI-powered assistant built for startup founders to manage operations, personnel, task tracking, performance routines, and Web3 payroll workflows.

## Capabilities & Triggers
Activate this skill whenever the user asks to:
1. **Manage Tasks:** "Add a high priority task", "List active tasks", "Show pending todos".
2. **Register Personnel:** "Onboard a contractor", "Register employee Sarah Connor as auditor".
3. **Founder Performance Routine:** "Analyze my sleep and stress", "Provide founder wellness advice".

## Required Environment Variables
- `GOOGLE_API_KEY` or `GEMINI_API_KEY`: API key for Gemini intent parsing.
- `OKX_API_KEY` (Optional): Required for live OKX wallet operations.

## Available Actions
- `add_task(client_name, title, priority)`
- `list_tasks(client_name)`
- `register_employee(client_name, name, role, salary)`
- `disburse_funds(client_name, recipient, amount)`
- `get_health_advice(sleep_hours, work_hours, stress_level)`