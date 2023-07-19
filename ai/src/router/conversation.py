from fastapi import APIRouter
from pydantic import BaseModel
from app import conversation_svc


conversation_router = APIRouter()


@conversation_router.get("/conversation_template")
def conversation_template():
    return {"templates": conversation_svc.get_templates()}


@conversation_router.get("/conversation_list")
def conversation_list():
    return {"conversations": [c.to_dict() for c in conversation_svc.list_all()]}


@conversation_router.get("/conversation/{conversation_id}")
def conversation_get(conversation_id: str):
    return {"conversation": conversation_svc.get(conversation_id)}


class ConversationCreate(BaseModel):
    name: str


@conversation_router.post("/conversation")
def conversation_create(body: ConversationCreate):
    new_conversation = conversation_svc.create(body.name)
    return {"conversation": new_conversation.to_dict()}


@conversation_router.delete("/conversation/{conversation_id}")
def conversation_delete(conversation_id: str):
    conversation_svc.delete(conversation_id)
    return "deleted"


class ConversationUpdateName(BaseModel):
    name: str


@conversation_router.post("/conversation/{conversation_id}/name")
def conversation_update_name(conversation_id: str, body: ConversationUpdateName):
    result = conversation_svc.update_name(conversation_id, body.name)
    return {"conversation": result.to_dict()}


class ConversationUpdateData(BaseModel):
    data: list[dict]


@conversation_router.post("/conversation/{conversation_id}/data")
def conversation_update_data(conversation_id: str, body: ConversationUpdateData):
    result = conversation_svc.update_data(conversation_id, body.data)
    return {"conversation": result.to_dict()}


class ConversationChat(BaseModel):
    chat: str


@conversation_router.post("/conversation/{conversation_id}/chat")
def conversation_chat(conversation_id: str, body: ConversationChat):
    result = conversation_svc.new_chat(conversation_id, body.chat)
    return {"result": result}
