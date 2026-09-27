"""
agents/research_agent.py
--------------------------
Agent 2 of 4: Policy Research Agent

Role: given the structured policy brief from the Policy Analyzer, find
real-world precedents - similar policies that have already been tried
elsewhere - and summarize what happened (outcomes, criticisms, results).

This agent is the clearest demonstration of *tool calling*: it is given
the `search_similar_policies` tool and decides for itself, via OpenAI
function calling, what to search for and how many times.
"""

from llm_utils import run_agent_with_tools
from tools.search_tool import TOOL_SCHEMA, AVAILABLE_TOOLS
from config import log

SYSTEM_PROMPT = """You are the Policy Research agent in a multi-agent \
policy impact analysis system. You have access to a `search_similar_policies` \
tool that searches the live web.

Given a structured policy brief, do the following:
1. Call the search tool at least once (and again with a refined query if the \
first results are weak) to find real-world precedents for this policy - \
similar laws/programs adopted in other cities, states, or countries.
2. Once you have enough information, STOP calling tools and write a concise \
research summary (250-400 words) covering:
   - 2-4 comparable policies/precedents you found, with where/when they were used
   - Reported outcomes or results (positive and negative) where available
   - Any notable criticisms or controversies
Cite the source titles you used inline in parentheses.
"""


def run(policy_summary: dict) -> str:
    log("ResearchAgent", "researching comparable policies...")
    user_prompt = (
        "Structured policy brief to research precedents for:\n\n"
        f"{policy_summary}"
    )
    findings = run_agent_with_tools(
        agent_name="ResearchAgent",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        tool_schemas=[TOOL_SCHEMA],
        tool_registry=AVAILABLE_TOOLS,
        temperature=0.3,
    )
    log("ResearchAgent", "done")
    return findings
