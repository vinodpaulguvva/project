
# PR Review Agent — Production-ready Prototype

This repository contains a production-focused backend prototype for an automated GitHub Pull Request Review Agent.

## Features
- FastAPI backend with `/review` endpoint
- GitHub PR diff fetching (via `.diff` endpoint)
- Multi-agent orchestration (style, logic, security)
- Aggregator to dedupe & summarize LLM outputs
- Dockerfile and CI workflow template

## Running locally
1. (optional) create virtualenv:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
2. Install:
   ```
   pip install -r requirements.txt
   ```
3. Set environment variables for production LLM usage (optional):
   - `OPENAI_API_KEY`
   - `GITHUB_TOKEN` (if fetching private PRs)
   - `OPENAI_MODEL` (optional)
4. Run:
   ```
   uvicorn app.main:app --reload
   ```
5. POST to `/review` with JSON:
   ```
   {
     "raw_diff": "diff --git a/foo.py b/foo.py\n...",
     "mode": "quick"
   }
   ```

## Notes
- If `OPENAI_API_KEY` is not provided or `openai` package isn't available, the service will return mocked LLM outputs so you can demo locally without costs.
- For production use: replace in-memory DB with Redis/Postgres, protect endpoints, add authentication, rate-limiting, and queue-based processing for large PRs.

## Demo script (what to record)
1. Intro (15s)
2. Show POST /review with sample diff (60s)
3. Show results & explain agents (45s)
4. Next steps & conclusion (15s)
