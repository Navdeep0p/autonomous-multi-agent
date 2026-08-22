from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import Literal
from app.core.config import get_agent_llm
from app.core.state import AgentState

class RouterDecision(BaseModel):
    next_node: Literal["retriever", "researcher", "coder", "reviewer", "FINISH"] = Field(
        description="The target node to route execution to."
    )
    reasoning: str = Field(description="Explanation of the chosen route.")
    current_plan: list[str] = Field(default_factory=list, description="Step-by-step execution plan.")

SUPERVISOR_SYSTEM_PROMPT = """You are the Supervisor of an autonomous multi-agent system.
Analyze the recent conversation history and current user goal to understand the TRUE intent.

Follow-up Guidelines:
- If the user provides a short or elliptical follow-up (e.g., previous prompt asked for a website link or calculation, and the new input is just a name like 'gemini?'), infer that the user wants the same task performed for the new entity.
- If web links or real-time info are requested and not yet gathered, route to 'researcher'.
- If the query is an isolated general concept or definition, route to 'reviewer' (Fast Path).
- If internal documents are needed, route to 'retriever'.
- If code execution or math is needed, route to 'coder'.
"""

def supervisor_node(state: AgentState) -> dict:
    llm = get_agent_llm("supervisor", temperature=0.0)
    structured_llm = llm.with_structured_output(RouterDecision)

    has_retrieved = state.get("retrieval_grade") is not None
    has_research = bool(state.get("research_data"))
    has_code = bool(state.get("code_output"))

    # Extract recent conversation turns for context
    messages = state.get("messages", [])
    history_lines = []
    for m in messages[-5:]:
        role = "User" if m.type == "human" else "Assistant"
        history_lines.append(f"{role}: {m.content}")
    history_context = "\n".join(history_lines) if history_lines else "None"

    context = (
        f"Recent Conversation History:\n{history_context}\n\n"
        f"Current User Goal: {state.get('user_goal', '')}\n"
        f"Retrieval Grade: {state.get('retrieval_grade', 'Not Attempted')}\n"
        f"Web Research: {'Present' if has_research else 'None'}\n"
        f"Code Sandbox: {'Present' if has_code else 'None'}\n"
        f"Review Feedback: {state.get('review_feedback', 'None')}\n"
        f"Iteration: {state.get('iteration_count', 0)}"
    )

    try:
        decision: RouterDecision = structured_llm.invoke([
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(content=context)
        ])
        next_step = decision.next_node
        plan = decision.current_plan
    except Exception:
        next_step = "reviewer"
        plan = state.get("plan", ["Direct evaluation"])

    # Circuit breakers
    if next_step == "retriever" and has_retrieved:
        next_step = "researcher" if state.get("retrieval_grade") == "fallback_needed" else "reviewer"
    elif next_step == "researcher" and has_research:
        next_step = "reviewer"
    elif next_step == "coder" and has_code:
        next_step = "reviewer"

    return {
        "next_step": next_step,
        "plan": plan
    }