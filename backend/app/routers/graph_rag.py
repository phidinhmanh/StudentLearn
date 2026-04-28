from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.graph_rag_service import get_graph_rag_service, GraphRAGService

router = APIRouter(
    prefix="/graph-rag",
    tags=["GraphRAG"],
)

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default-session"

class QueryResponse(BaseModel):
    answer: str

@router.post("/query", response_model=QueryResponse)
async def query_graph_rag(
    request: QueryRequest,
    service: GraphRAGService = Depends(get_graph_rag_service)
):
    """
    Query the knowledge graph using GraphRAG (Neo4j + Gemini) with Web Search fallback.
    """
    try:
        answer = await service.query(request.query, request.session_id)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GraphRAG error: {str(e)}")
