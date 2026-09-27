"""
agents/policy_analyzer_agent.py
--------------------------------
Agent 1 of 4: Policy Analyzer

Role: read the raw, free-text policy proposal supplied by the user and
turn it into a compact, structured brief (title, domain, objectives, key
provisions, target population). Every downstream agent works off this
structured summary instead of re-reading the raw text, which keeps their
prompts shorter and their outputs more consistent.

No tools are used here - this is a pure LLM reasoning/extraction step.
"""

import json
from llm_utils import call_llm
from config import log

SYSTEM_PROMPT = """You are the Policy Analyzer agent in a multi-agent policy \
impact analysis system. Read the proposed policy text and extract a \
structured brief.

Respond with ONLY a valid JSON object (no markdown fences, no commentary) \
with exactly these keys:
{
  "title": "short descriptive title for the policy",
  "domain": "one of: Legal, Governance & Public Policy | Healthcare | \
Environment | Economy | Education | Technology | Other",
  "objectives": ["objective 1", "objective 2", ...],
  "key_provisions": ["provision 1", "provision 2", ...],
  "target_population": "who the policy is primarily aimed at"
}
"""


def run(policy_text: str) -> dict:
    log("PolicyAnalyzer", "extracting structured brief from policy text...")
    raw = call_llm(SYSTEM_PROMPT, policy_text, temperature=0.1)

    try:
        summary = json.loads(raw)
    except json.JSONDecodeError:
        # Model occasionally wraps JSON in prose/fences despite instructions;
        # fall back to a minimal, still-usable structure rather than crashing.
        log("PolicyAnalyzer", "WARNING: could not parse JSON, using raw text fallback")
        summary = {
            "title": "Unparsed policy",
            "domain": "Other",
            "objectives": [],
            "key_provisions": [],
            "target_population": "Unknown",
            "raw_model_output": raw,
        }

    log("PolicyAnalyzer", f"done -> domain={summary.get('domain')!r}")
    return summary
