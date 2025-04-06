
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.google_service import get_ai_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    ai_response = get_ai_response(request.message)
    return ChatResponse(response=ai_response)
