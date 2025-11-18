
import re, httpx, asyncio
from typing import List, Dict

# Simple parser to split a raw unified diff into per-file changed hunks.
def parse_raw_diff(raw_diff: str) -> List[str]:
    # For demo we will split by diff headers 'diff --git' keeping context
    parts = []
    current = []
    for line in raw_diff.splitlines():
        if line.startswith('diff --git'):
            if current:
                parts.append('\n'.join(current))
                current = []
        current.append(line)
    if current:
        parts.append('\n'.join(current))
    return parts

async def fetch_diffs_from_pr(pr_url: str, token: str | None = None) -> List[str]:
    '''
    Fetch the PR diff using GitHub REST. Accepts full PR URL like:
    https://github.com/owner/repo/pull/123
    This function uses the PR .diff URL endpoint (appending .diff).
    '''
    # Convert PR URL to .diff URL
    if pr_url.endswith('/'):
        pr_url = pr_url[:-1]
    diff_url = pr_url + '.diff'
    headers = {'Accept': 'application/vnd.github.v3.diff'}
    if token:
        headers['Authorization'] = f'token {token}'
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(diff_url, headers=headers)
        r.raise_for_status()
        raw = r.text
    return parse_raw_diff(raw)
