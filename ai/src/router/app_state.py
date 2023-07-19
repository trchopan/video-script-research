from app import app_state_svc
from fastapi import APIRouter
from pydantic import BaseModel


app_state_router = APIRouter()


@app_state_router.get("/app_state_list")
def app_state_list():
    return {
        "app_states": [app_state.to_dict() for app_state in app_state_svc.list_all()],
    }


@app_state_router.get("/app_state/{app_id}")
def app_state_get(app_id: str):
    return {"app_state": app_state_svc.get(app_id)}


class AppStateCreate(BaseModel):
    name: str
    data: dict


@app_state_router.post("/app_state")
def app_state_create(body: AppStateCreate):
    app_id = app_state_svc.create(body.name, body.data)
    return {"app_id": app_id}


class AppStateUpdateData(BaseModel):
    data: dict


@app_state_router.post("/app_state/{app_id}/data")
def app_state_update_data(app_id: str, body: AppStateUpdateData):
    app_state_svc.update_data(app_id, data=body.data)
    return "saved"


class AppStateUpdateName(BaseModel):
    name: str


@app_state_router.post("/app_state/{app_id}/name")
def app_state_update_name(app_id: str, body: AppStateUpdateName):
    app_state_svc.update_name(app_id, name=body.name)
    return "saved"


@app_state_router.delete("/app_state/{app_id}")
def app_state_delete(app_id: str):
    app_state_svc.delete(app_id)
    return "deleted"
