from typing import List, Optional, Sequence, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Annotated with add_messages so LangGraph appends instead of overwriting
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_goal: str
    next_step: str
    route_decision: Optional[str]
    documents: Optional[List[str]]
    retrieval_grade: Optional[str]
    plan: Optional[List[str]]
    research_data: Optional[str]
    code_output: Optional[str]
    review_feedback: Optional[str]
    iteration_count: int
    final_output: Optional[str]