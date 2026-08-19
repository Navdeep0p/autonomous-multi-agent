from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import GEMINI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from app.core.state import AgentState
from app.tools.search import web_search

def researcher_node(state: AgentState) -> dict:
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=DEFAULT_TEMPERATURE,
        max_output_tokens=300
    )

    # 1. Convert goal into a concise search keyword phrase
    query_prompt = (
        f"Goal: {state['user_goal']}\n"
        "Extract a concise 3 to 5 word web search keyword phrase to find this information. "
        "Return ONLY the search phrase without quotes or explanation."
    )
    keyword_res = llm.invoke([HumanMessage(content=query_prompt)])
    search_keywords = keyword_res.content.strip().replace('"', '')

    # 2. Execute search
    search_results = web_search.invoke(search_keywords)

    # 3. Summarize findings
    summary_prompt = (
        f"Goal: {state['user_goal']}\n"
        f"Search Keywords Used: {search_keywords}\n"
        f"Raw Search Results:\n{search_results}\n\n"
        "Extract the core facts and numerical figures. Keep it concise."
    )
    summary = llm.invoke([HumanMessage(content=summary_prompt)])

    return {
        "research_data": summary.content.strip(),
        "next_step": "supervisor"
    }