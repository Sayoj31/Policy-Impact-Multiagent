"""
agents/stakeholder_agent.py
-----------------------------
Agent 3 of 4: Stakeholder Impact Agent

Role: work out who is affected by the policy and how - both positively and
negatively - for each stakeholder group.

Uses the `get_stakeholder_groups` tool to fetch the standard checklist of
stakeholders for the policy's domain, then reasons about impact for each
one, grounded in the research findings from Agent 2.
"""

from llm_utils import run_agent_with_tools
from tools.stakeholder_tool import TOOL_SCHEMA, AVAILABLE_TOOLS
from config import log

SYSTEM_PROMPT = """You are the Stakeholder Impact agent in a multi-agent \
policy impact analysis system. You have access to a `get_stakeholder_groups` \
tool that returns the standard checklist of stakeholder groups for a given \
policy domain.

Given a structured policy brief and research findings about similar \
policies elsewhere, do the following:
1. Call `get_stakeholder_groups` with the policy's domain to get the \
checklist of groups to consider.
2. For EACH stakeholder group returned, write 1-3 sentences describing the \
likely impact (positive, negative, or mixed), grounded in the policy's \
provisions and the research findings where relevant.
3. Present your final answer as a markdown list, one bullet per stakeholder \
group, in the form:
   **<Stakeholder group>**: <impact assessment>
Do not call any more tools once you have the checklist - move straight to \
the impact analysis.
"""


def run(policy_summary: dict, research_findings: str) -> str:
    log("StakeholderAgent", "analyzing impact per stakeholder group...")
    user_prompt = (
        f"Policy brief:\n{policy_summary}\n\n"
        f"Research findings on comparable policies:\n{research_findings}"
    )
    analysis = run_agent_with_tools(
        agent_name="StakeholderAgent",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        tool_schemas=[TOOL_SCHEMA],
        tool_registry=AVAILABLE_TOOLS,
        temperature=0.3,
    )
    log("StakeholderAgent", "done")
    return analysis
