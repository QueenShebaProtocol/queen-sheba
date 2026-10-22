from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from backend.services.llm import (
    generate_chat_response,
    reset_conversation,
    get_conversation_history,
    load_demo_context,
    DEMO_MOCK_MODE,
    LLM_PROVIDER,
    LLM_MODEL,
)

router = APIRouter(prefix="/api", tags=["Chat & Demo"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User chat message")
    conversation_id: Optional[str] = Field(default="demo-001", description="Unique conversation session ID")


class ChatResponse(BaseModel):
    response: str
    conversation_id: str


class ResetRequest(BaseModel):
    conversation_id: Optional[str] = Field(default="demo-001", description="Conversation session ID to reset")


@router.post("/chat", response_model=ChatResponse, summary="Send message to Queen AI")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for Queen AI.
    Intentionally vulnerable design for AXF cybersecurity testing.
    Token-conservative, single-message invocation without background retries.
    """
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    conv_id = request.conversation_id or "demo-001"
    ai_response = await generate_chat_response(conv_id, user_msg)
    
    return ChatResponse(response=ai_response, conversation_id=conv_id)


@router.post("/chat/reset", summary="Reset conversation history")
async def reset_endpoint(request: Optional[ResetRequest] = None):
    """Clears conversation memory for the provided conversation_id."""
    conv_id = request.conversation_id if request else "demo-001"
    reset_conversation(conv_id)
    return {"status": "success", "message": f"Conversation {conv_id} has been reset.", "conversation_id": conv_id}


@router.get("/demo-info", summary="Retrieve AI security status and demo parameters")
async def demo_info():
    """
    Provides demo environment status.
    Clearly shows that prompt firewall and output protections are intentionally OFF.
    """
    ctx = load_demo_context()
    return {
        "app_name": "Queen Sheba",
        "environment": "INTENTIONALLY VULNERABLE AI DEMO ENVIRONMENT",
        "security_status": {
            "prompt_firewall": "OFF",
            "output_protection": "OFF",
            "vulnerability_status": "VULNERABLE (AXF Not Installed)"
        },
        "mock_mode": DEMO_MOCK_MODE,
        "llm_provider": "mock" if DEMO_MOCK_MODE else LLM_PROVIDER,
        "llm_model": "mock-engine" if DEMO_MOCK_MODE else LLM_MODEL,
        "future_axf_integration": "Ready for AXF input/output inspection hooks",
        "demo_credentials_exposed_in_context": True
    }
