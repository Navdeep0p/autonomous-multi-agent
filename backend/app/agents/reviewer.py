from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from app.core.config import GEMINI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from app.core.state import AgentState

class Evaluation(BaseModel):
    is_satisfactory: bool = Field(description="True if the output satisfies the user objective completely.")
    feedback: str = Field(description="Constructive critique if not satisfactory, or synthesis notes if complete.")
    final_response: str = Field(description="The complete, polished final response if satisfactory.")

def reviewer_node(state: AgentState) -> dict:
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=DEFAULT_TEMPERATURE
    ).with_structured_output(Evaluation)

    current_iterations = state.get("iteration_count", 0) + 1

    prompt = (
        f"User Goal: {state['user_goal']}\n"
        f"Research Summary: {state.get('research_data', 'N/A')}\n"
        f"Code Execution Output: {state.get('code_output', 'N/A')}\n"
        f"Current Iteration: {current_iterations}\n\n"
        "Evaluate whether the collected results satisfy the user objective. "
        "If satisfactory or if iteration count >= 3, set is_satisfactory to True and write the final response."
    )

    eval_result: Evaluation = llm.invoke([HumanMessage(content=prompt)])

    if eval_result.is_satisfactory or current_iterations >= 3:
        return {
            "iteration_count": current_iterations,
            "final_output": eval_result.final_response,
            "review_feedback": "Approved",
            "next_step": "FINISH"
        }
    else:
        return {
            "iteration_count": current_iterations,
            "review_feedback": eval_result.feedback,
            "next_step": "supervisor"
        }