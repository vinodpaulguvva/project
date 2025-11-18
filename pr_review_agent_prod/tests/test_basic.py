
import asyncio
from app.github_utils import parse_raw_diff
from app.aggregator import aggregate_agent_outputs

def test_parse_raw_diff():
    sample = "diff --git a/foo.py b/foo.py\nindex 123..456\n--- a/foo.py\n+++ b/foo.py\n@@ -1,3 +1,4 @@\n+print('x')"
    parts = parse_raw_diff(sample)
    assert len(parts) == 1
    assert "foo.py" in parts[0]

def test_aggregator_empty():
    out = aggregate_agent_outputs([])
    assert out['summary'] == 'No issues found' or isinstance(out['summary'], str)
    assert out['metrics']['num_comments'] == 0
