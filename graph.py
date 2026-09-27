"""
graph.py
--------
Orchestration layer, built with LangGraph.

Defines the shared PipelineState that flows between agents, wires the four
agents into a StateGraph, and adds one conditional branch (basic
orchestration logic, not just a straight-line pipeline):

    START
      |
      v
   validate_input  --(policy text missing/too short)--> END (error)
      |
      v (ok)
   analyze_policy
      |
      v
   research_precedents
      |
      v
   analyze_stakeholders
      |
      v
   write_report
      |
      v
     END

Each node function takes the current state dict, calls the matching agent,
and returns only the keys it updates - LangGraph merges those into state.
"""

from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END

from agents import (
    policy_analyzer_agent,
    research_agent,
    stakeholder_agent,
    report_writer_agent,
)
from config import log


class PipelineState(TypedDict, total=False):
    policy_text: str
    policy_summary: dict
    research_findings: str
    stakeholder_analysis: str
    final_report: str
    error: Optional[str]


# --- Nodes ---------------------------------------------------------------

def validate_input(state: PipelineState) -> dict:
    text = (state.get("policy_text") or "").strip()
    if len(text) < 30:
        return {"error": "policy_text is missing or too short (< 30 chars)."}
    return {}


def analyze_policy(state: PipelineState) -> dict:
    summary = policy_analyzer_agent.run(state["policy_text"])
    return {"policy_summary": summary}


def research_precedents(state: PipelineState) -> dict:
    findings = research_agent.run(state["policy_summary"])
    return {"research_findings": findings}


def analyze_stakeholders(state: PipelineState) -> dict:
    analysis = stakeholder_agent.run(
        state["policy_summary"], state["research_findings"]
    )
    return {"stakeholder_analysis": analysis}


def write_report(state: PipelineState) -> dict:
    report = report_writer_agent.run(
        state["policy_summary"],
        state["research_findings"],
        state["stakeholder_analysis"],
    )
    return {"final_report": report}


# --- Conditional routing ---------------------------------------------------

def route_after_validation(state: PipelineState) -> str:
    return "invalid" if state.get("error") else "valid"


# --- Build the graph -------------------------------------------------------

def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("validate_input", validate_input)
    graph.add_node("analyze_policy", analyze_policy)
    graph.add_node("research_precedents", research_precedents)
    graph.add_node("analyze_stakeholders", analyze_stakeholders)
    graph.add_node("write_report", write_report)

    graph.add_edge(START, "validate_input")
    graph.add_conditional_edges(
        "validate_input",
        route_after_validation,
        {"valid": "analyze_policy", "invalid": END},
    )
    graph.add_edge("analyze_policy", "research_precedents")
    graph.add_edge("research_precedents", "analyze_stakeholders")
    graph.add_edge("analyze_stakeholders", "write_report")
    graph.add_edge("write_report", END)

    return graph.compile()


def run_pipeline(policy_text: str) -> PipelineState:
    app = build_graph()
    log("Orchestrator", "starting pipeline run")
    final_state = app.invoke({"policy_text": policy_text})
    log("Orchestrator", "pipeline finished")
    return final_state
