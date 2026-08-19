from app.graph import multi_agent_app

def run_agent_cli():
    print("=" * 60)
    print("AUTONOMOUS MULTI-AGENT SYSTEM (CLI RUNNER)")
    print("=" * 60)
    
    query = input("\nEnter objective: ").strip()
    if not query:
        query = "Find the latest stock price and market capitalization of Apple (AAPL), and write Python code to calculate how many shares someone could buy with $25,000 and the remaining cash balance."
        print(f"Using default prompt: {query}")

    state = {
        "messages": [],
        "user_goal": query,
        "next_step": "supervisor",
        "plan": [],
        "research_data": None,
        "code_output": None,
        "review_feedback": None,
        "iteration_count": 0,
        "final_output": None
    }

    print("\n--- Executing Graph Workflow ---")
    
    for event in multi_agent_app.stream(state):
        for node_name, state_update in event.items():
            print(f"\n[NODE]: {node_name.upper()}")
            if "plan" in state_update:
                print(f"  Plan: {state_update['plan']}")
            if "next_step" in state_update:
                print(f"  Target: {state_update['next_step']}")
            if "research_data" in state_update:
                print(f"  Research: {state_update['research_data'][:180]}...")
            if "code_output" in state_update:
                print(f"  Code Output:\n{state_update['code_output']}")
            if "review_feedback" in state_update:
                print(f"  Audit Status: {state_update['review_feedback']}")
            if "final_output" in state_update:
                state["final_output"] = state_update["final_output"]

    print("\n" + "=" * 60)
    print("FINAL SYNTHESIZED REPORT")
    print("=" * 60)
    print(state.get("final_output", "Workflow completed without final output."))

if __name__ == "__main__":
    run_agent_cli()