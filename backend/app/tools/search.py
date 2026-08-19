from langchain_core.tools import tool
from ddgs import DDGS

@tool
def web_search(query: str) -> str:
    """
    Search the web for up-to-date information, documentation, news, and financial data.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        
        if not results:
            return "No search results found."

        formatted_results = []
        for r in results:
            formatted_results.append(
                f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nURL: {r.get('href')}\n"
            )
        
        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Error executing search for query '{query}': {str(e)}"