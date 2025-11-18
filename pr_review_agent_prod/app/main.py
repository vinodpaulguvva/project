
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uuid, asyncio, os
from .github_utils import fetch_diffs_from_pr, parse_raw_diff
from .agents import run_all_agents_for_diffs
from .aggregator import aggregate_agent_outputs
from .schemas import ReviewResult

app = FastAPI(title="PR Review Agent", version="1.0")

DB = {}  # simple demo datastore; replace with Redis/Postgres for production

class ReviewRequest(BaseModel):
    pr_url: str | None = None
    raw_diff: str | None = None
    mode: str = "quick"  # quick|deep

@app.post("/review", response_model=ReviewResult)
async def review(req: ReviewRequest, background_tasks: BackgroundTasks):
    if not (req.pr_url or req.raw_diff):
        raise HTTPException(status_code=400, detail="Provide pr_url or raw_diff")
    job_id = str(uuid.uuid4())
    DB[job_id] = {"status": "running"}
    # Fetch diffs (IO)
    if req.pr_url:
        diffs = await fetch_diffs_from_pr(req.pr_url, token=os.getenv("GITHUB_TOKEN"))
    else:
        diffs = parse_raw_diff(req.raw_diff)
    # Run agents and aggregator synchronously here to return final result in response.
    # In production you might push to a queue and return job id immediately.
    agent_outputs = await run_all_agents_for_diffs(diffs, mode=req.mode)
    aggregated = await aggregate_agent_outputs(agent_outputs)
    result = {
        "job_id": job_id,
        "summary": aggregated.get("summary", ""),
        "comments": aggregated.get("comments", []),
        "metrics": aggregated.get("metrics", {})
    }
    DB[job_id] = {"status": "done", "result": result}
    return result

@app.get("/review/{job_id}", response_model=ReviewResult)
async def get_review(job_id: str):
    job = DB.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id not found")
    if job["status"] != "done":
        raise HTTPException(status_code=202, detail="job still running")
    return job["result"]
