from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import GEMINI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from app.core.state import AgentState
from app.tools.sandbox import python_executor

def coder_node(state: AgentState) -> dict:
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        max_output_tokens=350
    )

    code_prompt = (
        f"Goal: {state['user_goal']}\n"
        f"Data: {state.get('research_data', 'None')}\n\n"
        "Write pure executable Python code to compute or verify the goal. "
        "Print the results clearly. Output ONLY executable code in a markdown block."
    )
    code_response = llm.invoke([HumanMessage(content=code_prompt)])
    execution_result = python_executor.invoke(code_response.content)

    return {
        "code_output": execution_result,
        "next_step": "supervisor"
    }