"""
tools/stakeholder_tool.py
--------------------------
A lightweight lookup tool the Stakeholder Impact Agent can call to get a
starting checklist of stakeholder groups for a given policy domain, so the
LLM isn't inventing the taxonomy from scratch on every run.
"""

from typing import List, Dict

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_stakeholder_groups",
        "description": (
            "Return the standard checklist of stakeholder groups that "
            "should be considered for a policy in a given domain "
            "(e.g. 'Legal, Governance & Public Policy', 'Healthcare', "
            "'Environment')."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "The policy's domain/sector.",
                }
            },
            "required": ["domain"],
        },
    },
}

# A small default taxonomy. Unrecognized domains fall back to the
# "general" list so the tool always returns something useful.
_DOMAIN_STAKEHOLDERS: Dict[str, List[str]] = {
    "general": [
        "Citizens / General Public",
        "Government agencies implementing the policy",
        "Businesses / Industry affected",
        "Vulnerable or marginalized groups",
        "Civil society / advocacy organizations",
    ],
    "legal, governance & public policy": [
        "Citizens / General Public",
        "Legislative & regulatory bodies",
        "Judiciary / legal community",
        "Businesses subject to compliance",
        "Civil society & advocacy groups",
        "Local vs. national government levels",
    ],
    "healthcare": [
        "Patients",
        "Healthcare providers (doctors, nurses, clinics)",
        "Insurers / payers",
        "Pharmaceutical & medical device companies",
        "Public health agencies",
    ],
    "environment": [
        "Local residents / communities",
        "Industry & manufacturers",
        "Environmental regulators",
        "Future generations / long-term ecological impact",
        "NGOs & environmental advocacy groups",
    ],
    "economy": [
        "Consumers",
        "Small & medium businesses",
        "Large corporations / industry groups",
        "Workers / labor unions",
        "Government revenue & budget",
    ],
}


def get_stakeholder_groups(domain: str) -> List[str]:
    key = (domain or "").strip().lower()
    return _DOMAIN_STAKEHOLDERS.get(key, _DOMAIN_STAKEHOLDERS["general"])


AVAILABLE_TOOLS = {
    "get_stakeholder_groups": get_stakeholder_groups,
}
