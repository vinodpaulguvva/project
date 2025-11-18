
import asyncio, json
from typing import List, Dict, Any
from .llm_client import call_llm_structured

# Each agent receives a file-diff (string) and returns a list of structured comments (dicts)
async def style_agent(diff: str) -> Dict[str, Any]:
    system = "You are a code style reviewer. Return JSON list of issues with fields: file,line_start,line_end,category,severity,message,suggested_fix,confidence"
    prompt = f"Diff to analyze for style:\n{diff}\nReturn a JSON array of objects."
    return await call_llm_structured(prompt, system)

async def logic_agent(diff: str) -> Dict[str, Any]:
    system = "You are a logic/bug detection reviewer. Return JSON list of issues..."
    prompt = f"Diff to analyze for logic/bugs:\n{diff}\nReturn a JSON array of objects."
    return await call_llm_structured(prompt, system)

async def security_agent(diff: str) -> Dict[str, Any]:
    system = "You are a security-focused code reviewer. Return JSON list of issues..."
    prompt = f"Diff to analyze for security vulnerabilities:\n{diff}\nReturn a JSON array of objects."
    return await call_llm_structured(prompt, system)

async def run_all_agents_for_diffs(diffs: List[str], mode: str = "quick") -> List[Dict[str, Any]]:
    tasks = []
    for d in diffs:
        # For each diff, run agents in parallel
        tasks.append(_run_agents_for_single_diff(d, mode))
    results = await asyncio.gather(*tasks)
    return results

async def _run_agents_for_single_diff(diff: str, mode: str):
    # choose agents based on mode
    if mode == "quick":
        agents = [style_agent, logic_agent, security_agent]
    else:
        agents = [style_agent, logic_agent, security_agent]  # extend later
    res = await asyncio.gather(*(a(diff) for a in agents))
    # Normalize results: try to ensure lists
    normalized = []
    for r in res:
        if not r:
            continue
        if isinstance(r, dict) and r.get("mock"):
            # mocked single-text response -> convert to a simple note
            normalized.append([{
                "file": "unknown",
                "line_start": 1,
                "line_end": 1,
                "category": "info",
                "severity": "low",
                "message": r.get("text", "mocked output"),
                "suggested_fix": None,
                "confidence": 0.2
            }])
        elif isinstance(r, list):
            normalized.append(r)
        elif isinstance(r, dict) and "text" in r:
            normalized.append([{
                "file": "unknown",
                "line_start": 1,
                "line_end": 1,
                "category": "info",
                "severity": "low",
                "message": r["text"][:500],
                "suggested_fix": None,
                "confidence": 0.2
            }])
        else:
            # unknown shape -> stringify
            normalized.append([{
                "file": "unknown",
                "line_start": 1,
                "line_end": 1,
                "category": "info",
                "severity": "low",
                "message": str(r)[:500],
                "suggested_fix": None,
                "confidence": 0.2
            }])
    # flatten to a single list
    flat = [item for sub in normalized for item in sub]
    return {"diff": diff, "raw_agent_comments": flat}
