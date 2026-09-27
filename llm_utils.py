"""
llm_utils.py
------------
Shared helpers for talking to the LLM.

`call_llm`        - a plain, single-turn chat completion (no tools).
`run_agent_with_tools` - the reusable "agent loop": send messages + tool
                    schemas to the model, execute any tool calls it asks
                    for, feed the results back, and repeat until the model
                    returns a final text answer (or we hit a safety cap).

Putting this here means every agent file stays focused on *what* it asks
the model to do, not *how* tool calling is wired up.
"""

import json
from typing import Callable, Dict, List

from config import client, MODEL_NAME, MAX_TOOL_ITERATIONS, log


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """Single request/response call, no tools. Used for pure reasoning steps."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def run_agent_with_tools(
    agent_name: str,
    system_prompt: str,
    user_prompt: str,
    tool_schemas: List[Dict],
    tool_registry: Dict[str, Callable],
    temperature: float = 0.3,
) -> str:
    """
    Runs the classic agentic tool-calling loop:

        1. Send the conversation + available tool schemas to the model.
        2. If the model responds with tool_calls, execute each one locally
           using `tool_registry`, and append the results as `tool` messages.
        3. Send the updated conversation back to the model.
        4. Repeat until the model answers with plain text (no more tool
           calls) or MAX_TOOL_ITERATIONS is reached.

    Returns the model's final text answer.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for step in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=temperature,
            messages=messages,
            tools=tool_schemas,
        )
        message = response.choices[0].message

        # No tool calls -> the model is done, return its answer.
        if not message.tool_calls:
            return message.content or ""

        # The model wants to call one or more tools. Record its request...
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
        )

        # ...then actually execute each requested tool and report results back.
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            try:
                fn_args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                fn_args = {}

            log(agent_name, f"tool call -> {fn_name}({fn_args})")

            fn = tool_registry.get(fn_name)
            if fn is None:
                result = {"error": f"Unknown tool '{fn_name}'"}
            else:
                result = fn(**fn_args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                }
            )

    # Safety valve: if the model keeps calling tools past the iteration cap,
    # force a final plain-text answer with no tools available.
    log(agent_name, "hit MAX_TOOL_ITERATIONS, forcing a final answer")
    messages.append(
        {
            "role": "user",
            "content": "Please give your final answer now, without calling any more tools.",
        }
    )
    response = client.chat.completions.create(
        model=MODEL_NAME, temperature=temperature, messages=messages
    )
    return response.choices[0].message.content or ""
