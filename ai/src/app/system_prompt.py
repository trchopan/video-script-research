from typing import List
from peewee import CharField, DateTimeField, TextField
from app.base_model import BaseDBModel, get_db
from app.helpers import get_timestamp


class SystemPrompt(BaseDBModel):
    name = CharField()
    template = TextField()
    timestamp = DateTimeField()

    def to_dict(self):
        return {
            "name": self.name,
            "template": self.template,
            "timestamp": self.timestamp,
        }


class SystemPromptService:
    def create(self, name: str, template: str):
        p = SystemPrompt(
            name=name,
            template=template,
            timestamp=get_timestamp(),
        )
        p.save()
        return p

    def update(self, id: int, name: str, template: str):
        p = SystemPrompt.get(id)
        p.name = name
        p.template = template
        p.save()
        return p

    def delete(self, id: int):
        SystemPrompt.get(id).delete_instance()

    def list_all(self):
        prompts: List[SystemPrompt] = SystemPrompt.select().order_by(SystemPrompt.timestamp)
        return prompts


# Create table if not exists
get_db().create_tables([SystemPrompt])
