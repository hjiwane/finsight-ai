from typing import Annotated, Sequence, TypedDict
import json
import os
import asyncio

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agent.tools import tools
from app.core.config import settings

os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

_agent_semaphore = asyncio.Semaphore(1)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

chat_model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
).bind_tools(tools)

reactive_model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
).bind_tools(tools)

CHAT_SYSTEM_PROMPT = """You are FinSight, an AI personal finance assistant for Indian users.

Rules:
- Always use rupees for amounts.
- Keep responses short and clear.
- For spending, budget, or transaction questions, always use the relevant tool first.
- Call only ONE tool at a time.
- Base the final answer only on tool results. Never guess.
- Respond conversationally. Never use alert-style formatting.
"""

REACTIVE_SYSTEM_PROMPT = """You are FinSight, an AI personal finance assistant for Indian users.
You monitor UPI transactions and flag suspicious ones.

Rules:
- Always use rupees for amounts.
- Call only ONE tool at a time.
- When asked to flag a transaction, call flag_suspicious_transaction immediately.
- After flagging, respond with exactly one short sentence describing why it is suspicious.
- Never discuss budgets or summaries in reactive mode.
"""

def build_app(model):
    def model_call(state: AgentState) -> AgentState:
        messages = list(state["messages"])
        response = model.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if not getattr(last_message, "tool_calls", None):
            return "end"
        return "continue"

    graph = StateGraph(AgentState)
    graph.add_node("our_agent", model_call)
    graph.add_node("tools", ToolNode(tools=tools))
    graph.set_entry_point("our_agent")
    graph.add_conditional_edges(
        "our_agent",
        should_continue,
        {"continue": "tools", "end": END},
    )
    graph.add_edge("tools", "our_agent")
    return graph.compile()

chat_app     = build_app(chat_model)
reactive_app = build_app(reactive_model)


def is_suspicious(txn: dict) -> tuple[bool, str]:
    from datetime import datetime
    reasons = []
    if txn.get("amount", 0) > 15000:
        reasons.append(f"large amount {txn['amount']:.0f}")
    if txn.get("merchant", "").lower() == "unknown merch":
        reasons.append("unknown merchant")
    try:
        hour = datetime.fromisoformat(txn["timestamp"]).hour
        if 0 <= hour < 5:
            reasons.append("transaction at odd hour")
    except (KeyError, ValueError):
        pass
    return bool(reasons), ", ".join(reasons)


async def run_chat(user_message: str, history: list[dict]) -> str:
    messages = [SystemMessage(content=CHAT_SYSTEM_PROMPT)]
    for h in history[-10:]:
        if h["role"] == "user":
            messages.append(HumanMessage(content=h["content"]))
        elif h["role"] == "assistant":
            messages.append(AIMessage(content=h["content"]))
    messages.append(HumanMessage(content=user_message))

    async with _agent_semaphore:
        try:
            result = await chat_app.ainvoke({"messages": messages})
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage) and msg.content:
                    return msg.content.strip()
            return "I could not generate a response. Please try again."
        except Exception as e:
            print(f"[run_chat error] {e}")
            raise


async def run_reactive(transaction: dict) -> str:
    suspicious, reason = is_suspicious(transaction)
    if not suspicious:
        return ""

    prompt = (
        f"New UPI transaction:\n{json.dumps(transaction, indent=2)}\n\n"
        f"This transaction is suspicious because: {reason}.\n"
        f"Call flag_suspicious_transaction with transaction_id='{transaction['id']}' "
        f"and reason='{reason}'."
    )
    messages = [
        SystemMessage(content=REACTIVE_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]

    # if semaphore is locked (chat running), skip reactive silently
    if _agent_semaphore.locked():
        print("[Reactive] Skipped — agent busy with chat")
        return ""

    async with _agent_semaphore:
        try:
            result = await reactive_app.ainvoke({"messages": messages})
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage) and msg.content:
                    return msg.content.strip()
            return ""
        except Exception as e:
            print(f"[run_reactive error] {e}")
            return ""