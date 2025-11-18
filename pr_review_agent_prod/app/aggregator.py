
from typing import List, Dict, Any
import itertools
def aggregate_agent_outputs(agent_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    '''
    Simple aggregator:
    - flatten comments from agents
    - dedupe by (file, line_start, message substring)
    - compute simple summary and metrics
    '''
    all_comments = []
    for entry in agent_outputs:
        for c in entry.get("raw_agent_comments", []):
            all_comments.append(c)
    # dedupe
    seen = set()
    deduped = []
    for c in all_comments:
        key = (c.get("file"), c.get("line_start"), c.get("message")[:60])
        if key in seen:
            continue
        seen.add(key)
        # normalize confidence and severity defaults
        c.setdefault("confidence", 0.5)
        c.setdefault("severity", "medium")
        deduped.append(c)
    # simple summary
    counts = {}
    for c in deduped:
        counts[c.get("category", "other")] = counts.get(c.get("category", "other"), 0) + 1
    summary = " | ".join([f"{k}: {v}" for k,v in counts.items()]) or "No issues found"
    metrics = {"num_comments": len(deduped)}
    return {"summary": summary, "comments": deduped, "metrics": metrics}
