"""API router for MCP-powered chatbot."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

from .bedrock_chatbot import BedrockMCPChatbot
from db.session import get_database_manager, DatabaseManager

router = APIRouter(prefix="/chatbot", tags=["MCP Chatbot"])


class ChatRequest(BaseModel):
    """Chat request model."""
    query: str
    connection_id: str
    patient_id: Optional[str] = None
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    """Chat response model."""
    status: str
    answer: str
    tools_used: List[str] = []
    iterations: int
    session_id: str
    timestamp: str


# Store chatbot sessions
chatbot_sessions: Dict[str, BedrockMCPChatbot] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """
    Chat with the MCP-powered healthcare assistant.
    
    The chatbot uses AWS Bedrock Claude and MCP tools to access real patient data.
    
    Example queries:
    - "Show me demographics for patient 12345"
    - "What medications is this patient taking?"
    - "Get all vital signs for patient 67890"
    - "Show me the patient's lab results and conditions"
    """
    try:
        session_id = request.session_id
        
        # Get or create chatbot session
        if session_id not in chatbot_sessions:
            chatbot = BedrockMCPChatbot()
            await chatbot.initialize_mcp()
            chatbot_sessions[session_id] = chatbot
        else:
            chatbot = chatbot_sessions[session_id]
        
        # Process chat
        response = await chatbot.chat(
            user_message=request.query,
            connection_id=request.connection_id,
            patient_id=request.patient_id
        )
        
        # Log errors for debugging
        if response["status"] == "error":
            print(f"Chat error for session {session_id}: {response.get('error', 'Unknown error')}")
        
        return ChatResponse(
            status=response["status"],
            answer=response.get("answer", response.get("error", "")),
            tools_used=response.get("tools_used", []),
            iterations=response.get("iterations", 0),
            session_id=session_id,
            timestamp=response["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chatbot error: {str(e)}"
        )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session."""
    if session_id not in chatbot_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chatbot = chatbot_sessions[session_id]
    return {
        "session_id": session_id,
        "history": chatbot.get_history(),
        "total_messages": len(chatbot.get_history())
    }


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear conversation history for a session."""
    if session_id not in chatbot_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chatbot = chatbot_sessions[session_id]
    chatbot.clear_history()
    
    # Clean up MCP session and remove from cache
    await chatbot.cleanup()
    del chatbot_sessions[session_id]
    
    return {
        "status": "success",
        "message": f"Chat history cleared and session closed for {session_id}"
    }


@router.get("/tools")
async def list_available_tools():
    """List all available MCP tools."""
    # Create temp chatbot to get tools
    chatbot = BedrockMCPChatbot()
    try:
        await chatbot.initialize_mcp()
        return {
            "tools": chatbot.available_tools,
            "total_tools": len(chatbot.available_tools)
        }
    finally:
        # Always cleanup temp session
        await chatbot.cleanup()


@router.get("/sessions")
async def list_active_sessions():
    """List all active chatbot sessions."""
    return {
        "active_sessions": list(chatbot_sessions.keys()),
        "total_sessions": len(chatbot_sessions)
    }