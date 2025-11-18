
import os, json, asyncio
from typing import Dict, Any
# We support OpenAI via openai package. If OPENAI_API_KEY not set, we fallback to a mocked response.
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # change as needed

async def call_llm_structured(prompt: str, system: str, max_tokens: int = 500) -> Dict[str, Any]:
    '''
    Call the configured LLM and expect a JSON-ish response.
    Uses a safe fallback when API key or library not available.
    '''
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not OPENAI_AVAILABLE:
        # Mock response for offline/demo use
        await asyncio.sleep(0.05)
        return {"mock": True, "text": f"MOCKED ANALYSIS for prompt start: {prompt[:80]}..."}
    openai.api_key = api_key
    # Use Chat Completions async interface if available
    # Compose messages
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]
    # Async call
    try:
        resp = await openai.ChatCompletion.acreate(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.0
        )
        content = resp.choices[0].message.content
        # Try to parse JSON substring
        try:
            return json.loads(content)
        except Exception:
            return {"text": content}
    except Exception as e:
        return {"error": str(e)}
