from fastapi import APIRouter
from pydantic import BaseModel
from app import system_prompt_svc


system_prompt_router = APIRouter()


@system_prompt_router.get("/system_prompts")
def system_prompt_list():
    result = system_prompt_svc.list_all()
    return {"system_prompts": [{"id": r.get_id(), "data": r.to_dict()} for r in result]}


@system_prompt_router.delete("/system_prompt/{id}")
def system_prompt_delete(id: int):
    system_prompt_svc.delete(id)
    return "deleted"


class SystemPromptUpdate(BaseModel):
    name: str
    template: str


@system_prompt_router.post("/system_prompt/{id}")
def systemprompt_update_name(id: int, body: SystemPromptUpdate):
    result = system_prompt_svc.update(id, body.name, body.template)
    return {"system_prompt": result.to_dict()}


class SystemPromptCreate(BaseModel):
    name: str
    template: str


@system_prompt_router.post("/system_prompt")
def systemprompt_update_template(body: SystemPromptCreate):
    result = system_prompt_svc.create(body.name, body.template)
    return {"system_prompt": result.to_dict()}
