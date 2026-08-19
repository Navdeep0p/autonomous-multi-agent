```markdown
# Autonomous Multi-Agent Engineering System

An autonomous, state-driven multi-agent system implemented using **LangGraph**, **Google Gemini API**, an isolated **Python Subprocess Sandbox**, and **DuckDuckGo Web Search**[cite: 2].

---

## Core Capabilities

* **State Machine Orchestration:** Uses LangGraph for cyclical state transitions, shared memory, and deterministic graph routing[cite: 2].
* **Hierarchical Supervisor:** Decomposes complex objectives into subtasks and coordinates worker agents dynamically[cite: 2].
* **Live Web Intelligence:** Researcher agent queries live web sources to extract factual context and documentation[cite: 2].
* **Isolated Code Sandbox:** Coder agent executes dynamic Python scripts within an isolated subprocess runtime to compute and verify logic[cite: 2].
* **Self-Healing Review Loop:** Reviewer agent audits generated artifacts against defined constraints, triggering re-routing loops upon failure[cite: 2].
* **Unified Web Interface & SSE Streaming:** Real-time event streaming powered by FastAPI (Server-Sent Events) and a single-page dark workspace UI[cite: 1, 2].

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
│   │   │   ├── coder.py          # Sandbox code generation
│   │   │   ├── researcher.py     # Web search & query formulation
│   │   │   ├── reviewer.py       # Quality auditing & reflection
│   │   │   └── supervisor.py     # Task decomposition & routing
│   │   ├── core/
│   │   │   ├── config.py         # Environment & model configurations
│   │   │   └── state.py          # TypedDict shared graph schema
│   │   ├── tools/
│   │   │   ├── sandbox.py        # Subprocess execution runtime
│   │   │   └── search.py         # DuckDuckGo search tool wrapper
│   │   ├── graph.py              # LangGraph compilation & edge routing
│   │   └── main.py               # FastAPI server & static file host
│   ├── requirements.txt          # Python dependencies
│   ├── run_cli.py                # Command-line interface runner
│   └── test_connection.py        # Connectivity verification script
├── frontend/
│   └── index.html                # Single-page workspace UI
├── .gitignore
└── README.md
```[cite: 2]

---

## Getting Started

### 1. Prerequisites
* Python 3.10 or higher
* Google AI Studio API Key

### 2. Installation & Setup
```bash
# Clone the repository
git clone [https://github.com/Navdeep0p/autonomous-multi-agent.git](https://github.com/Navdeep0p/autonomous-multi-agent.git)
cd autonomous-multi-agent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```[cite: 2]

### 3. Environment Configuration
Create a `.env` file inside `backend/`[cite: 2]:
```ini
GEMINI_API_KEY=your_gemini_api_key_here

```

### 4. Running the System

**Option A: Web Workspace (Recommended)**

```bash
cd backend
uvicorn app.main:app --reload --port 8000

```

Open `http://127.0.0.1:8000` in your browser to access the interface.

**Option B: Command-Line Interface (CLI)**

```bash
cd backend
python run_cli.py
```[cite: 2]

---

## Technical Specifications

| Component | Implementation | Purpose |
| :--- | :--- | :--- |
| **Orchestration** | LangGraph (`StateGraph`) | Cyclic graph state execution & routing[cite: 2] |
| **Reasoning Engine** | Google Gemini Flash | Planning, summarization, and code synthesis[cite: 2] |
| **Web Retrieval** | DuckDuckGo (`ddgs`) | Real-time information extraction[cite: 2] |
| **Execution Sandbox** | Python `subprocess` | Isolated code computation & numerical verification[cite: 2] |
| **API & Streaming** | FastAPI + Server-Sent Events | Non-blocking telemetry and token streaming[cite: 2] |
| **User Interface** | HTML5 / CSS3 / JavaScript | Single-page workspace with reasoning logs & syntax highlighting[cite: 1, 2] |

---

## License

Distributed under the MIT License. See `LICENSE` for details.

```