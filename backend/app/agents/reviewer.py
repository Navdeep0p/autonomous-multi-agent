from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.core.config import get_agent_llm
from app.core.state import AgentState

class Evaluation(BaseModel):
    is_satisfactory: bool = Field(description="Set to True if results satisfy user objective.")
    feedback: Optional[str] = Field(default=None, description="Critique if not satisfactory.")
    final_response: Optional[str] = Field(default=None, description="Polished final answer.")

REVIEWER_SYSTEM_PROMPT = """You are a quality assurance evaluator and synthesizer.
Review the user objective, recent conversation context, and any gathered research or code outputs.
If the user's input was a follow-up (e.g. 'gemini?' following 'what is the link for deepseek?'), answer the implied question (provide the link for Gemini)."""

def reviewer_node(state: AgentState) -> dict:
    llm = get_agent_llm("reviewer")
    structured_llm = llm.with_structured_output(Evaluation)

    current_iterations = state.get("iteration_count", 0) + 1
    max_iterations_reached = current_iterations >= 3

    docs = state.get("documents", [])
    doc_text = "\n\n".join(docs) if docs else "None"

    # Format recent history
    messages = state.get("messages", [])
    history_lines = []
    for m in messages[-5:]:
        role = "User" if m.type == "human" else "Assistant"
        history_lines.append(f"{role}: {m.content}")
    history_context = "\n".join(history_lines) if history_lines else "None"

    user_content = (
        f"Conversation History:\n{history_context}\n\n"
        f"Current User Goal: {state.get('user_goal', 'N/A')}\n"
        f"Local Knowledge Context:\n{doc_text}\n"
        f"Web Research Summary: {state.get('research_data', 'N/A')}\n"
        f"Code Execution Output: {state.get('code_output', 'N/A')}\n"
        f"Current Iteration: {current_iterations} (Max: 3)"
    )

    eval_result: Evaluation = structured_llm.invoke([
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ])

    if eval_result.is_satisfactory or max_iterations_reached:
        final_output = eval_result.final_response or (
            f"{doc_text}\n{state.get('research_data', '')}\n{state.get('code_output', '')}"
        )
        return {
            "messages": [AIMessage(content=final_output)],
            "iteration_count": current_iterations,
            "final_output": final_output,
            "review_feedback": "Approved",
            "next_step": "FINISH"
        }

    return {
        "iteration_count": current_iterations,
        "review_feedback": eval_result.feedback or "Output incomplete.",
        "next_step": "supervisor"
    }