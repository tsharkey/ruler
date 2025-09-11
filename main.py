from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.rag_service import rag_service

app = FastAPI(title="Board Game RAG API")

class QueryRequest(BaseModel):
    question: str
    limit: int = 5

class RuleResult(BaseModel):
    id: int
    rule: str
    game_name: str
    similarity: float

class QueryResponse(BaseModel):
    query: str
    results: List[RuleResult]
    total_results: int

@app.get("/")
def read_root():
    return {"message": "Board Game RAG API"}

@app.post("/query", response_model=QueryResponse)
def query_rules(request: QueryRequest):
    try:
        # Search using your RAG service
        results = rag_service.search_rules(request.question, request.limit)
        
        # Convert to Pydantic models
        rule_results = [RuleResult(**result) for result in results]
        
        return QueryResponse(
            query=request.question,
            results=rule_results,
            total_results=len(rule_results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Add CORS if needed
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
