import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.graph import multi_agent_app

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

@app.get("/health")
def health_check():
    return {"status": "healthy"}

async def event_generator(goal: str):
    initial_state = {
        "messages": [],
        "user_goal": goal,
        "next_step": "supervisor",
        "plan": [],
        "research_data": None,
        "code_output": None,
        "review_feedback": None,
        "iteration_count": 0,
        "final_output": None
    }

    final_output_text = ""

    # Asynchronous non-blocking streaming
    async for event in multi_agent_app.astream(initial_state):
        for node_name, state_update in event.items():
            payload = {
                "node": node_name,
                "plan": state_update.get("plan"),
                "next_step": state_update.get("next_step"),
                "research_snippet": state_update.get("research_data"),
                "code_output": state_update.get("code_output"),
                "review_feedback": state_update.get("review_feedback"),
                "final_output": state_update.get("final_output")
            }
            if state_update.get("final_output"):
                final_output_text = state_update.get("final_output")

            yield f"data: {json.dumps(payload)}\n\n"

    yield f"data: {json.dumps({'node': 'COMPLETE', 'final_output': final_output_text})}\n\n"

@app.post("/run-stream")
async def run_stream(req: AgentRequest):
    return StreamingResponse(
        event_generator(req.user_goal), 
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )