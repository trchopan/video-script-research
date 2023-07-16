import json
from uuid import uuid4
from peewee import CharField, DateTimeField, TextField

from app.base_model import BaseModel, get_db
from app.helpers import get_timestamp


class AppState(BaseModel):
    app_id = CharField()
    name = CharField()
    timestamp = DateTimeField()
    data = TextField()

    def to_dict(self):
        return {
            "app_id": self.app_id,
            "name": self.name,
            "timestamp": self.timestamp,
            "data": json.loads(str(self.data)),
        }


class AppStateService:
    def __init__(self):
        pass

    def get(self, app_id: str) -> dict:
        state: AppState = AppState.get(AppState.app_id == app_id)
        return state.to_dict()

    def create(self, name: str, data: dict):
        app_id = str(uuid4())
        app_state = AppState(
            app_id=app_id,
            name=name,
            data=data,
            timestamp=get_timestamp(),
        )
        app_state.save()
        return app_id

    def save(self, app_id: str, data: dict):
        app_state = AppState.get(AppState.app_id == app_id)
        app_state.data = json.dumps(data)
        app_state.save()

    def delete(self, app_id: str):
        AppState.get(AppState.app_id == app_id).delete_instance()

    def list_all(self):
        app_states: list[AppState] = list(AppState.select())
        return app_states


# Create table if not exists
get_db().create_tables([AppState])