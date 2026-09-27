"""
agents/report_writer_agent.py
--------------------------------
Agent 4 of 4: Report Writer Agent

Role: the final synthesis step. Takes the structured policy brief, the
research findings, and the stakeholder impact analysis, and writes a single
cohesive, BALANCED impact report - i.e. it must present both benefits and
risks/criticisms fairly rather than advocating for or against the policy.

No tools are used here - this is a pure synthesis/writing step over the
outputs already produced by Agents 1-3.
"""

from llm_utils import call_llm
from config import log

SYSTEM_PROMPT = """You are the Report Writer agent in a multi-agent policy \
impact analysis system. You will be given three prior agents' outputs:
1. A structured policy brief
2. Research findings on comparable real-world policies
3. A stakeholder-by-stakeholder impact analysis

Synthesize these into a single, well-organized "Policy Impact Analysis \
Report" in markdown with these sections:

# Policy Impact Analysis Report
## 1. Policy Overview
## 2. Comparable Policies & Precedents
## 3. Stakeholder Impact Summary
## 4. Balanced Assessment (Benefits vs. Risks)
## 5. Overall Recommendation

Requirements:
- Be BALANCED: section 4 must list genuine benefits AND genuine risks/\
criticisms - do not omit or downplay either side.
- Section 5 should give a measured recommendation (e.g. proceed, proceed \
with modifications, pilot first, or reconsider) with a one-line justification \
- it should not simply repeat section 4.
- Keep the whole report under ~600 words. Use markdown formatting \
(headings, bullet points) throughout.
"""


def run(policy_summary: dict, research_findings: str, stakeholder_analysis: str) -> str:
    log("ReportWriter", "synthesizing final balanced report...")
    user_prompt = (
        f"1) Policy brief:\n{policy_summary}\n\n"
        f"2) Research findings:\n{research_findings}\n\n"
        f"3) Stakeholder impact analysis:\n{stakeholder_analysis}"
    )
    report = call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.4)
    log("ReportWriter", "done")
    return report
