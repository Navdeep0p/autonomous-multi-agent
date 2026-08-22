from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import get_agent_llm
from app.core.state import AgentState
from app.tools.search import web_search

def researcher_node(state: AgentState) -> dict:
    llm = get_agent_llm("researcher", temperature=0.1)

    # 1. Format recent conversation history for context resolution
    messages = state.get("messages", [])
    history_context = ""
    if len(messages) > 1:
        history_lines = []
        for m in messages[-4:]:  # Look at last few exchanges
            role = "User" if m.type == "human" else "Assistant"
            history_lines.append(f"{role}: {m.content}")
        history_context = "Recent Conversation History:\n" + "\n".join(history_lines) + "\n\n"

    # 2. Contextual Query Rewriter
    query_prompt = (
        f"{history_context}"
        f"Current User Input: {state['user_goal']}\n\n"
        "Based on the conversation history and current input, generate a standalone 3-to-6 word search query. "
        "Resolve any missing context, pronouns, or follow-ups (e.g., if previous question was about 'age of X' and input is 'and Y?', search for 'age of Y').\n"
        "Return ONLY the search query keywords."
    )

    keyword_res = llm.invoke([
        SystemMessage(content="You are a search query optimizer that resolves follow-up questions into standalone web queries."),
        HumanMessage(content=query_prompt)
    ])
    search_keywords = keyword_res.content.strip().replace('"', '').replace("'", "")

    # 3. Execute search
    try:
        search_results = web_search.invoke(search_keywords)
    except Exception as e:
        search_results = f"Search error: {str(e)}"

    # 4. Synthesize findings
    summary_prompt = (
        f"Goal: {state['user_goal']}\n"
        f"Resolved Search Query: {search_keywords}\n"
        f"Raw Search Results:\n{search_results}\n\n"
        "Extract the core factual details, numbers, and dates answering the goal concisely."
    )
    summary = llm.invoke([
        SystemMessage(content="You are an expert research analyst. Extract key facts cleanly."),
        HumanMessage(content=summary_prompt)
    ])

    return {
        "research_data": summary.content.strip(),
        "next_step": "supervisor"
    }