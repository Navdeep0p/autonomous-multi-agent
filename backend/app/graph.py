import time
from langgraph.graph import StateGraph, START, END
from app.core.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.researcher import researcher_node
from app.agents.coder import coder_node
from app.agents.reviewer import reviewer_node

def route_supervisor(state: AgentState) -> str:
    time.sleep(1)  # Safe buffer to prevent RPM spikes on free tier
    next_step = state.get("next_step")
    if next_step in ["researcher", "coder", "reviewer"]:
        return next_step
    return "reviewer"

def route_reviewer(state: AgentState) -> str:
    time.sleep(1)
    if state.get("next_step") == "FINISH":
        return END
    return "supervisor"

def create_multi_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("reviewer", reviewer_node)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "coder": "coder",
            "reviewer": "reviewer"
        }
    )

    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("coder", "supervisor")

    workflow.add_conditional_edges(
        "reviewer",
        route_reviewer,
        {
            "supervisor": "supervisor",
            END: END
        }
    )

    return workflow.compile()

multi_agent_app = create_multi_agent_graph()