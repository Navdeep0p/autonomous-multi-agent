import streamlit as st
import requests
import json

st.set_page_config(page_title="Autonomous Multi-Agent System", page_icon="🤖", layout="wide")

st.title("🤖 Autonomous Multi-Agent Engineering System")
st.caption("Powered by LangGraph, Google Gemini API, Isolated Sandboxes, and Live Web Retrieval")

user_input = st.text_area(
    "Enter your high-level objective:",
    value="Find the latest stock price and quarterly revenue of Tesla, and calculate its forward P/E ratio using code.",
    height=90
)

run_button = st.button("🚀 Run Multi-Agent System", type="primary")

if run_button and user_input:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("⚡ Agent Thought Stream")
        status_container = st.container()

    with col2:
        st.subheader("📋 Final Synthesis & Artifacts")
        result_container = st.empty()

    backend_url = "http://127.0.0.1:8000/run-stream"
    
    try:
        response = requests.post(backend_url, json={"user_goal": user_input}, stream=True)
        
        final_result = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    event_data = json.loads(decoded_line[6:])
                    node = event_data.get("node")

                    if node == "COMPLETE":
                        final_result = event_data.get("final_output")
                        break

                    with status_container:
                        with st.expander(f"📍 Node Active: **{node.upper()}**", expanded=True):
                            if event_data.get("plan"):
                                st.markdown(f"**Current Plan:** {event_data['plan']}")
                            if event_data.get("next_step"):
                                st.markdown(f"**Routing Next:** `{event_data['next_step']}`")
                            if event_data.get("research_snippet"):
                                st.info(f"**Research Summary:**\n{event_data['research_snippet']}")
                            if event_data.get("code_output"):
                                st.code(event_data['code_output'], language="text")
                            if event_data.get("review_feedback"):
                                st.success(f"**Audit Status:** {event_data['review_feedback']}")

        if final_result:
            result_container.markdown(final_result)
        else:
            result_container.info("Workflow completed.")

    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")