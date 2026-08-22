from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import get_agent_llm
from app.core.state import AgentState
from app.tools.sandbox import python_executor

def coder_node(state: AgentState) -> dict:
    # Uses Ollama locally if USE_LOCAL_FOR_INTERNAL=true, else rotates Gemini keys
    llm = get_agent_llm("coder", temperature=0.1)

    system_prompt = (
        "You are an expert Python Developer agent.\n"
        "Write executable Python code to compute, verify, or solve the objective.\n"
        "Always output executable code enclosed in a ```python ... ``` block.\n"
        "Always print results clearly to stdout."
    )

    context_prompt = (
        f"Goal: {state['user_goal']}\n"
        f"Data: {state.get('research_data', 'None')}\n\n"
        "Write the Python script to calculate or verify this."
    )

    code_response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=context_prompt)
    ])

    execution_result = python_executor.invoke(code_response.content)

    return {
        "code_output": str(execution_result),
        "next_step": "supervisor"
    }