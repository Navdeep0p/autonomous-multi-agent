from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import Literal
from app.core.config import GEMINI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from app.core.state import AgentState

class RouterDecision(BaseModel):
    next_node: Literal["researcher", "coder", "reviewer", "FINISH"] = Field(
        description="The next specialized agent node to route the task to."
    )
    reasoning: str = Field(description="Brief explanation of why this node was selected.")
    current_plan: list[str] = Field(description="The updated step-by-step execution plan.")

def supervisor_node(state: AgentState) -> dict:
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=DEFAULT_TEMPERATURE
    ).with_structured_output(RouterDecision)

    system_prompt = (
        "You are the Supervisor of an autonomous multi-agent engineering team.\n"
        "Your job is to progress through the plan sequentially:\n"
        "1. If web information/facts are needed and NOT yet collected, route to 'researcher'.\n"
        "2. If calculations, scripts, or programmatic tasks are needed and NOT yet executed, route to 'coder'.\n"
        "3. Once both research and code outputs are collected, route to 'reviewer'.\n"
        "DO NOT repeat a node if its task is already done."
    )

    context = (
        f"User Goal: {state['user_goal']}\n"
        f"Current Plan: {state.get('plan', [])}\n"
        f"Research Found: {state.get('research_data', 'None')}\n"
        f"Code Output: {state.get('code_output', 'None')}\n"
        f"Review Feedback: {state.get('review_feedback', 'None')}\n"
        f"Iteration Count: {state.get('iteration_count', 0)}"
    )

    decision: RouterDecision = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=context)
    ])

    return {
        "next_step": decision.next_node,
        "plan": decision.current_plan
    }