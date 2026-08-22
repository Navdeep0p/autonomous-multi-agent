from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import get_agent_llm
from app.core.state import AgentState
from app.tools.retriever import query_local_docs

class DocumentGrade(BaseModel):
    binary_score: Literal["yes", "no"] = Field(
        description="Whether the retrieved documents contain information relevant to the user objective ('yes' or 'no')."
    )
    reason: str = Field(description="Brief explanation of the grading decision.")

GRADER_SYSTEM_PROMPT = """You are a retrieval evaluator assessing the relevance of local documents to a user objective.

Grade 'yes' if the documents contain relevant facts or direct context that help address the user objective.
Grade 'no' if the documents are irrelevant, empty, or insufficient to answer the goal.
"""

def retriever_node(state: AgentState) -> dict:
    user_goal = state.get("user_goal", "")
    
    # 1. Retrieve candidate chunks from ChromaDB
    docs = query_local_docs(user_goal, k=3)
    
    if not docs:
        return {
            "documents": [],
            "retrieval_grade": "fallback_needed",
            "next_step": "researcher"  # Fallback to web search
        }
    
    # 2. Grade document relevance using fast local model
    llm = get_agent_llm("supervisor", temperature=0.0)
    structured_llm = llm.with_structured_output(DocumentGrade)

    doc_context = "\n\n---\n\n".join(docs)
    grading_prompt = f"User Goal: {user_goal}\n\nRetrieved Documents:\n{doc_context}"

    try:
        grade_result: DocumentGrade = structured_llm.invoke([
            SystemMessage(content=GRADER_SYSTEM_PROMPT),
            HumanMessage(content=grading_prompt)
        ])
        is_relevant = grade_result.binary_score == "yes"
    except Exception:
        is_relevant = len(docs) > 0

    if is_relevant:
        return {
            "documents": docs,
            "retrieval_grade": "relevant",
            "next_step": "reviewer"
        }
    else:
        return {
            "documents": docs,
            "retrieval_grade": "fallback_needed",
            "next_step": "researcher"  # Corrective Fallback to Web Search
        }