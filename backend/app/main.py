import json
import uuid
import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph import multi_agent_app
from app.core.config import USE_LOCAL_FOR_INTERNAL, OLLAMA_MODEL, DEFAULT_MODEL
from app.tools.retriever import add_document_to_db

app = FastAPI(title="Autonomous Multi-Agent System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    user_goal: str
    thread_id: Optional[str] = None

class DocumentIngestRequest(BaseModel):
    text: str
    source_name: Optional[str] = "custom_note"

@app.get("/")
async def read_index():
    frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/index.html")
    return FileResponse(frontend_path)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/config")
def get_runtime_config():
    return {
        "use_local": USE_LOCAL_FOR_INTERNAL,
        "ollama_model": OLLAMA_MODEL,
        "gemini_model": DEFAULT_MODEL,
        "nodes": {
            "supervisor": {
                "engine": "Ollama" if USE_LOCAL_FOR_INTERNAL else "Gemini",
                "model": OLLAMA_MODEL if USE_LOCAL_FOR_INTERNAL else DEFAULT_MODEL
            },
            "retriever": {
                "engine": "ChromaDB",
                "model": "text-embedding-004"
            },
            "researcher": {
                "engine": "Gemini",
                "model": DEFAULT_MODEL
            },
            "coder": {
                "engine": "Ollama" if USE_LOCAL_FOR_INTERNAL else "Gemini",
                "model": OLLAMA_MODEL if USE_LOCAL_FOR_INTERNAL else DEFAULT_MODEL
            },
            "reviewer": {
                "engine": "Gemini",
                "model": DEFAULT_MODEL
            }
        }
    }

@app.post("/api/documents/ingest")
def ingest_document(req: DocumentIngestRequest):
    """Ingests custom knowledge or documents into the local ChromaDB vector store."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    add_document_to_db(req.text, metadata={"source": req.source_name})
    return {"status": "success", "message": "Document indexed successfully into Vector DB."}

async def event_generator(goal: str, thread_id: str):
    yield f"data: {json.dumps({'node': 'INIT', 'thread_id': thread_id})}\n\n"

    initial_state = {
        "messages": [HumanMessage(content=goal)],
        "user_goal": goal,
        "next_step": "supervisor",
        "route_decision": None,
        "documents": [],
        "retrieval_grade": None,
        "plan": [],
        "research_data": None,
        "code_output": None,
        "review_feedback": None,
        "iteration_count": 0,
        "final_output": None
    }

    final_output_text = ""
    config = {"configurable": {"thread_id": thread_id}}

    async for event in multi_agent_app.astream(initial_state, config=config):
        for node_name, state_update in event.items():
            if node_name == "retriever":
                engine_used = "ChromaDB"
                model_used = "text-embedding-004"
            elif USE_LOCAL_FOR_INTERNAL and node_name in ["supervisor", "coder"]:
                engine_used = "Ollama"
                model_used = OLLAMA_MODEL
            else:
                engine_used = "Gemini"
                model_used = DEFAULT_MODEL

            payload = {
                "node": node_name,
                "engine": engine_used,
                "model": model_used,
                "thread_id": thread_id,
                "plan": state_update.get("plan"),
                "next_step": state_update.get("next_step"),
                "documents": state_update.get("documents"),
                "retrieval_grade": state_update.get("retrieval_grade"),
                "research_snippet": state_update.get("research_data"),
                "code_output": state_update.get("code_output"),
                "review_feedback": state_update.get("review_feedback"),
                "final_output": state_update.get("final_output")
            }
            if state_update.get("final_output"):
                final_output_text = state_update.get("final_output")

            yield f"data: {json.dumps(payload)}\n\n"

    yield f"data: {json.dumps({'node': 'COMPLETE', 'thread_id': thread_id, 'final_output': final_output_text})}\n\n"

@app.post("/run-stream")
async def run_stream(req: AgentRequest):
    thread_id = req.thread_id or f"session-{uuid.uuid4().hex[:8]}"
    return StreamingResponse(
        event_generator(req.user_goal, thread_id), 
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )