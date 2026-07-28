import logging
from typing import Any, Optional
from google import genai
from google.genai import types

logger = logging.getLogger("AtlasAI")

# Client automatically picks up GOOGLE_API_KEY from environment variables
client = genai.Client()

# Complete Active Gemini LLM Fallback Sequence (Ranked by speed/intelligence tier)
LLM_FALLBACK_STACK = [
    "gemini-3.6-flash",          # 1. Primary flagship (frontier speed & agentic reasoning)
    "gemini-3.5-flash",          # 2. General availability frontier model
    "gemini-3.5-flash-lite",     # 3. High-throughput subagent model
    "gemini-3.1-pro-preview",    # 4. Deep reasoning & complex math fallback
    "gemini-3.1-flash-lite",     # 5. Fast, lightweight automation model
    "gemini-2.5-pro",            # 6. Stable long-context reasoning workhorse
    "gemini-2.5-flash"           # 7. Production safety-net model
]


def generate_content_with_fallback(
    contents: Any, 
    config: Optional[types.GenerateContentConfig] = None,
    **kwargs
) -> types.GenerateContentResponse:
    """Executes a generate_content call sequentially trying all active Gemini LLMs."""
    last_exception = None

    for model in LLM_FALLBACK_STACK:
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
                **kwargs
            )
            return response
        except Exception as e:
            logger.warning(f"⚠️ Model '{model}' failed ({e}). Escalating to next fallback in stack...")
            last_exception = e

    raise RuntimeError(f"All {len(LLM_FALLBACK_STACK)} active Gemini LLM models failed. Last error: {last_exception}")


def get_health_advice(
    sleep_hours: float, 
    work_hours: float, 
    stress_level: int, 
    client_name: str = "Default Client"
) -> str:
    """Bio-hacking & Founder Wellness Routine with client context."""
    system_instruction = f"You are Atlas, an elite Bio-hacking & Founder Performance Specialist assisting '{client_name}'."
    
    prompt = f"""
    Current Founder Metrics for {client_name}:
    - Sleep: {sleep_hours} hours
    - Work: {work_hours} hours
    - Stress Level: {stress_level}/10

    Provide 2 concise, high-impact performance optimizations tailored for this client profile.
    Keep it direct and actionable.
    """
    
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3
    )

    response = generate_content_with_fallback(contents=prompt, config=config)
    return response.text