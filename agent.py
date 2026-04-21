"""
agent.py
---------
Two-Track Pricing Agent.

A small, readable agent built on the Claude Agent SDK pattern:

  User question
      |
      v
  Claude (LLM)  <-->  Tools (quote_package, project_revenue, ...)
      |
      v
  Natural-language answer, with numbers grounded in tool output

Run:
    export ANTHROPIC_API_KEY=sk-ant-...
    python agent.py                                # interactive REPL
    python agent.py "Quote a Pro + Creator Pro bundle"
"""

import os
import sys
import json
from anthropic import Anthropic

from tools import TOOL_SCHEMAS, TOOL_REGISTRY


MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a Two-Track Pricing Agent for a B2B SaaS platform.

Your job is to help GTM, finance, and leadership teams:
  1. Quote pricing for a prospective company.
  2. Project revenue across customer mixes.
  3. Recommend the right Hiring and/or Creator tier.
  4. Answer sales-enablement questions about what each tier includes.

Ground rules:
  - NEVER invent prices. Always call a tool to fetch authoritative numbers.
  - When asked "how much" or "what would it cost", call quote_package.
  - When asked "what if" revenue questions, call project_revenue.
  - When asked "which tier fits", call recommend_tier.
  - Present results as clean, readable summaries with key numbers highlighted.
  - If the user hasn't given enough info, ask a focused follow-up question
    before guessing.

The pricing tracks are:
  - Track 1 (Hiring): Starter $999 / Pro $3,999 / Elite $11,999 / Enterprise $25k+
  - Track 2 (Creator): Creator Starter $2,999 / Creator Pro $7,999 / Enterprise $20k+
  - All-Access bundle: 20% off when both a Hiring tier and a Creator tier are
    purchased together.
"""


def run_agent(user_message: str, client: Anthropic, max_turns: int = 6) -> str:
    """Agent loop. Keeps iterating tool calls until the model produces a final answer."""
    messages = [{"role": "user", "content": user_message}]

    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return "".join(
                block.text for block in response.content if block.type == "text"
            )

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                fn = TOOL_REGISTRY[block.name]
                try:
                    result = fn(**block.input)
                except Exception as e:
                    result = {"error": str(e)}
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, default=str),
                })

        messages.append({"role": "user", "content": tool_results})

    return "[agent exceeded max turns without finishing]"


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY first.")
        sys.exit(1)

    client = Anthropic()

    if len(sys.argv) > 1:
        print(run_agent(" ".join(sys.argv[1:]), client))
        return

    print("Two-Track Pricing Agent. Type 'quit' to exit.\n")
    while True:
        try:
            q = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() in {"quit", "exit"}:
            break
        print(f"\nAgent > {run_agent(q, client)}\n")


if __name__ == "__main__":
    main()
