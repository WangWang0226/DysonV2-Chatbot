from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter()

# Initialize RAG service
try:
    rag_service = RAGService()
except Exception as e:
    print(f"Failed to initialize RAG service: {e}")
    rag_service = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat message and return AI response
    """
    if not rag_service:
        raise HTTPException(
            status_code=500, 
            detail="RAG service is not available. Please check your environment variables."
        )
    
    try:
        # Get response from RAG service
        result = await rag_service.get_response(request.message)
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"處理聊天訊息時發生錯誤：{str(e)}"
        )

@router.get("/health")
async def health():
    """
    Health check endpoint
    """
    status = "healthy" if rag_service else "unhealthy"
    return {"status": status}