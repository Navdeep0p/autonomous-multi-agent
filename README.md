```markdown
# Autonomous Multi-Agent Engineering System

An autonomous, state-driven multi-agent system implemented using **LangGraph**, **Google Gemini API**, an isolated **Python Subprocess Sandbox**, and **DuckDuckGo Web Search**.

---

## Core Capabilities

* **State Machine Orchestration:** Employs LangGraph for cycle management, shared memory state transitions, and deterministic graph routing.
* **Hierarchical Supervisor:** Decomposes user objectives and coordinates sub-tasks dynamically between worker agents.
* **Live Web Intelligence:** Researcher agent queries live web sources to extract factual context and documentation.
* **Isolated Code Sandbox:** Coder agent executes dynamic Python scripts within an isolated runtime environment to compute and verify logic.
* **Self-Healing Review Loop:** Reviewer agent audits generated artifacts against defined constraints, triggering re-routing loops upon failure.
* **Real-Time Streaming:** Exposes intermediate graph execution states over Server-Sent Events (FastAPI) and an interactive Streamlit UI.

---

## System Architecture

```text
               +-----------------------+
               |     User Objective    |
               +-----------+-----------+
                           |
                           v
               +-----------------------+
        +----> |   Supervisor Agent    | <----+
        |      |  (Planner / Router)   |      |
        |      +-----------+-----------+      |
        |                  |                  | (Feedback Loop
        |       +----------+----------+       |  on Audit Failure)
        |       |                     |       |
        |       v                     v       |
  +-----+---------------+   +---------+-------+---+
  |   Research Agent    |   |     Coder Agent     |
  | (DuckDuckGo Search) |   |  (Python Sandbox)   |
  +---------------------+   +---------------------+
        |                             |
        +--------------+--------------+
                       |
                       v
            +---------------------+
            | Reviewer / Evaluator| -----> [Final Synthesized Output]
            +---------------------+

```

---

## Project Structure

```text
autonomous-multi-agent/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── supervisor.py     # Task decomposition & routing
│   │   │   ├── researcher.py     # Web search & summarization
│   │   │   ├── coder.py          # Sandbox code execution
│   │   │   └── reviewer.py       # Quality auditing & reflection
│   │   ├── core/
│   │   │   ├── config.py         # Environment & model configurations
│   │   │   └── state.py          # TypedDict shared graph schema
│   │   ├── tools/
│   │   │   ├── search.py         # Search integration wrapper
│   │   │   └── sandbox.py        # Isolated execution runtime
│   │   ├── graph.py              # LangGraph compilation & edge routing
│   │   └── main.py               # FastAPI SSE streaming server
│   ├── requirements.txt
│   └── run_cli.py                # Command-line interface runner
├── frontend/
│   └── app.py                    # Streamlit real-time dashboard
└── README.md

```

---

## Getting Started

### 1. Prerequisites

* Python 3.10 or higher
* Google AI Studio API Key

### 2. Installation & Environment Setup

```bash
# Clone the repository
git clone [https://github.com/Navdeep0p/autonomous-multi-agent.git](https://github.com/Navdeep0p/autonomous-multi-agent.git)
cd autonomous-multi-agent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

```

### 3. Environment Configuration

Create a `.env` file inside `backend/`:

```ini
GEMINI_API_KEY=your_gemini_api_key_here

```

### 4. Running the System

**Option A: Command-Line Interface (CLI)**

```bash
python backend/run_cli.py

```

**Option B: Web Dashboard (FastAPI + Streamlit)**

```bash
# Terminal 1: Start API server
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Launch frontend
streamlit run frontend/app.py

```

---

## Technical Specifications

| Component | Implementation | Purpose |
| --- | --- | --- |
| **Orchestration** | LangGraph (StateGraph) | Cyclic graph state execution & routing |
| **Reasoning Engine** | Google Gemini Flash | Structured JSON output & planning |
| **Web Retrieval** | DuckDuckGo (`ddgs`) | Real-time information gathering |
| **Execution Sandbox** | Python Subprocess API | Isolated code computation & verification |
| **API & Streaming** | FastAPI (SSE) | Non-blocking real-time event streaming |
| **User Interface** | Streamlit | Step-by-step agent tracking interface |

---

