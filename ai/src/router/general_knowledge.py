from fastapi import APIRouter
from pydantic import BaseModel
from app import general_knowledge_svc

general_knowledge_router = APIRouter()


class GeneralKnowledgeWikipediaSearch(BaseModel):
    search: str


@general_knowledge_router.post("/general_knowledge_wikipedia_search")
def general_knowledge_wikipedia_search(body: GeneralKnowledgeWikipediaSearch):
    return {"search_results": general_knowledge_svc.search_page(body.search)}


class GeneralKnowledgeWikipediaPage(BaseModel):
    search: str


@general_knowledge_router.post("/general_knowledge_wikipedia_page")
def general_knowledge_wikipedia_page(body: GeneralKnowledgeWikipediaPage):
    return {"page": general_knowledge_svc.get_wikipedia_page(body.search)}


class GeneralKnowledgeWikipediaSummary(BaseModel):
    search: str


@general_knowledge_router.post("/general_knowledge_wikipedia_summary")
def general_knowledge_wikipedia_summary(body: GeneralKnowledgeWikipediaSummary):
    return {"summary": general_knowledge_svc.get_wikipedia_summary(body.search)}
