from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from app import conversation_svc
from app.conversation import (
    ConversationChatToolData,
    ConversationChatToolEnum,
    ConversationUpdateOrder,
)


conversation_router = APIRouter()


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


class ConversationUpdateSystemPrompt(BaseModel):
    system_prompt: str


@conversation_router.post("/conversation/{conversation_id}/system_prompt")
def conversation_update_system_prompt(conversation_id: str, body: ConversationUpdateSystemPrompt):
    result = conversation_svc.update_system_prompt(conversation_id, body.system_prompt)
    return {"conversation": result.to_dict()}


class ConversationUpdateMemory(BaseModel):
    memory: list[dict]


@conversation_router.post("/conversation/{conversation_id}/memory")
def conversation_update_memory(conversation_id: str, body: ConversationUpdateMemory):
    result = conversation_svc.update_memory(conversation_id, body.memory)
    return {"conversation": result.to_dict()}


class ConversationUpdateOrderRequest(BaseModel):
    orders: List[ConversationUpdateOrder]


@conversation_router.post("/conversation/orders")
def conversation_update_orders(body: ConversationUpdateOrderRequest):
    conversation_svc.update_orders(body.orders)
    return {"conversations": [c.to_dict() for c in conversation_svc.list_all()]}


class ConversationChat(BaseModel):
    chat: str
    tools: dict[ConversationChatToolEnum, ConversationChatToolData]


@conversation_router.post("/conversation/{conversation_id}/chat")
def conversation_chat(conversation_id: str, body: ConversationChat):
    result = conversation_svc.new_chat(conversation_id, body.chat, body.tools)
    return {"conversation": result.to_dict()}
