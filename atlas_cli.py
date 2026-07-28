import json
import requests
from google import genai
from google.genai import types

client = genai.Client()
ATLAS_BASE_URL = "http://127.0.0.1:8000"

LLM_FALLBACK_STACK = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro",
    "gemini-3.1-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
]

SYSTEM_INSTRUCTION = """
You are Atlas, an intent parsing agent for a startup founder.
Map user natural language to one of these endpoints:

1. ADD_TASK -> endpoint: "/tasks/add", method: "POST", data: {"title": str, "priority": "High"|"Medium"|"Low"}
2. REGISTER_EMPLOYEE -> endpoint: "/employees/register", method: "POST", data: {"name": str, "role": str, "salary": float, "wallet_address": str}
3. LOG_FINANCE -> endpoint: "/finance/log", method: "POST", data: {"trans_type": "INCOME"|"EXPENSE", "amount": float, "category": str, "description": str}
4. WELLNESS_TIPS -> endpoint: "/wellness/advice", method: "POST", data: {"sleep_hours": float, "work_hours": float, "stress_level": int}
5. PAY_SALARY -> endpoint: "/employees/pay-salary", method: "POST", data: {"employee_id": str, "amount": float, "chain_id": str}
6. TREASURY_ANALYSIS -> endpoint: "/finance/treasury-analysis", method: "GET", data: {}
7. GENERAL_CHAT -> endpoint: "/agent/chat", method: "POST", data: {"prompt": str}

CRITICAL DATA EXTRACTION RULES:
- If a dollar or monetary amount is mentioned (e.g., "$500", "500 USDC", "500.00"), ALWAYS parse it as a float into the `amount` field.
- Never leave `amount` null or empty if a dollar figure exists in the prompt.
- Do NOT include currency symbols or dollar signs inside `employee_id` or `name` fields.

If the user's input does not explicitly match items 1 through 6, route it to GENERAL_CHAT (item 7) with data: {"prompt": "<user prompt verbatim>"}.

Respond STRICTLY in valid raw JSON with keys: "endpoint", "method", "data".
"""


def parse_intent_with_fallback(user_prompt: str) -> dict:
    """Parses natural language user input into structured API execution intents using Gemini."""
    for model in LLM_FALLBACK_STACK:
        try:
            response = client.models.generate_content(
                model=model,
                contents=f"Founder Prompt: '{user_prompt}'",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"⚠️ CLI parser model '{model}' failed: {e}. Trying fallback...")

    raise RuntimeError("All models in the fallback stack failed to parse intent.")


def main():
    print("=" * 60)
    print("🌐 Atlas AI Agent Terminal Active (Full LLM Fallback Enabled)")
    print("Examples: 'Add a high priority task to review Q3 deck'")
    print("          'Log $500 spent on AWS hosting'")
    print("          'Disburse $500 to Alice on Polygon'")
    print("          'I slept 5.5h, worked 12h, stress is 8'")
    print("          'Analyze my treasury'")
    print("          'How do I structure equity splits?' (General Chat)")
    print("Type 'exit' to end session.")
    print("=" * 60)

    while True:
        try:
            prompt = input("\n🤖 Founder > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "quit"]:
                break

            intent = parse_intent_with_fallback(prompt)
            endpoint = intent.get("endpoint")

            # Fallback guard if an intent somehow still returns empty
            if not endpoint:
                print("\n⚠️ Atlas: I couldn't map that request to a supported action.")
                print("Try tasks, expenses, employee setup, wellness tips, or general startup questions.")
                continue

            url = f"{ATLAS_BASE_URL}{endpoint}"
            method = intent.get("method", "POST")
            data = intent.get("data", {})

            if method == "POST":
                res = requests.post(url, json=data)
            else:
                res = requests.get(url)

            print("\n⚡ [Atlas Response]:")
            if res.headers.get("content-type", "").startswith("application/json"):
                print(json.dumps(res.json(), indent=2))
            else:
                print(res.text)

        except Exception as e:
            print(f"⚠️ Error: {str(e)}")


if __name__ == "__main__":
    main()