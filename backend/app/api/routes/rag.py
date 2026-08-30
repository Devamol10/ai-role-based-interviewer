from fastapi import APIRouter, HTTPException, status
from app.schemas.rag import RAGSearchRequest, RAGSearchResponse
from app.rag.retrieval import retrieve_relevant_chunks

router = APIRouter()

@router.post("/search", response_model=RAGSearchResponse)
def search_rag_knowledge(request: RAGSearchRequest):
    try:
        results = retrieve_relevant_chunks(
            query=request.query,
            role=request.role,
            top_k=request.top_k
        )
        return RAGSearchResponse(
            query=request.query,
            role=request.role,
            result_count=len(results),
            results=results
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during vector retrieval: {str(e)}"
        )
