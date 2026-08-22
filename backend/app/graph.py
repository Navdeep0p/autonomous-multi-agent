import time
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.core.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.retriever import retriever_node
from app.agents.researcher import researcher_node
from app.agents.coder import coder_node
from app.agents.reviewer import reviewer_node

checkpointer = MemorySaver()

def route_supervisor(state: AgentState) -> str:
    time.sleep(1)
    next_step = state.get("next_step")
    if next_step in ["retriever", "researcher", "coder", "reviewer"]:
        return next_step
    return "reviewer"

def route_retriever(state: AgentState) -> str:
    time.sleep(1)
    next_step = state.get("next_step")
    if next_step == "researcher":
        return "researcher"
    return "reviewer"

def route_reviewer(state: AgentState) -> str:
    time.sleep(1)
    if state.get("next_step") == "FINISH":
        return END
    return "supervisor"

def create_multi_agent_graph():
    workflow = StateGraph(AgentState)

    # 1. Register Nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("reviewer", reviewer_node)

    # 2. Entry Point
    workflow.add_edge(START, "supervisor")

    # 3. Supervisor Dynamic Routing
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "retriever": "retriever",
            "researcher": "researcher",
            "coder": "coder",
            "reviewer": "reviewer"
        }
    )

    # 4. Corrective RAG Direct Transitions
    workflow.add_conditional_edges(
        "retriever",
        route_retriever,
        {
            "researcher": "researcher",
            "reviewer": "reviewer"
        }
    )

    # 5. Pipeline Completion Transitions
    workflow.add_edge("researcher", "reviewer")
    workflow.add_edge("coder", "reviewer")

    # 6. Quality Gate / Finish
    workflow.add_conditional_edges(
        "reviewer",
        route_reviewer,
        {
            "supervisor": "supervisor",
            END: END
        }
    )

    return workflow.compile(checkpointer=checkpointer)

multi_agent_app = create_multi_agent_graph()