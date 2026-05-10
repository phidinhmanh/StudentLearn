from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.graph_rag_service import get_graph_rag_service, GraphRAGService
from app.services.factory import get_graph_service
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/graph-rag",
    tags=["GraphRAG"],
)

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default-session"

class QueryResponse(BaseModel):
    answer: str

class GraphNode(BaseModel):
    id: str
    label: str
    skill_level: int = 1
    type: str = "concept"

class GraphLink(BaseModel):
    source: str
    target: str
    type: str = "relatedTo"

class GraphVisualizationResponse(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]

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

@router.get("/visualize/{document_id}", response_model=GraphVisualizationResponse)
async def visualize_document_graph(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Return nodes and edges for a document's knowledge graph for visualization.
    Nodes include skill_level for color coding (0=Gray, 1=Red, 2=Gold, 3=Green).
    """
    user_id = current_user["sub"]
    service = get_graph_service()

    doc = await service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if doc.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    topics = await service.get_topics_by_document(document_id)
    all_edges = service.metadata.get("edges", [])

    # Build node set from topics in this document
    topic_ids = {t["id"] for t in topics if t}
    nodes = []
    for t in topics:
        if not t:
            continue
        # Determine skill_level from progress metadata
        skill = 1  # default: Đỏ/Hổng
        for key, p in service.metadata.get("progress", {}).items():
            if p.get("topic_id") == t["id"]:
                skill = p.get("skill_level", 1)
                break
        nodes.append(GraphNode(
            id=t["id"],
            label=t.get("name", t["id"]),
            skill_level=skill,
            type=t.get("type", "concept"),
        ))

    # Filter edges where both source and target are in this document's topic set
    links = []
    for edge in all_edges:
        src = edge.get("source") or edge.get("source_id") or edge.get("from")
        tgt = edge.get("target") or edge.get("target_id") or edge.get("to")
        if src in topic_ids and tgt in topic_ids:
            links.append(GraphLink(
                source=src,
                target=tgt,
                type=edge.get("type", edge.get("relation", "relatedTo")),
            ))

    return GraphVisualizationResponse(nodes=nodes, links=links)
