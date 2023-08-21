import json
from enum import Enum
from typing import List, Optional
from uuid import uuid4

import wikipedia
from langchain import OpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage, messages_from_dict, messages_to_dict
from langchain.tools import (
    BaseTool,
    DuckDuckGoSearchRun,
    WikipediaQueryRun,
    YouTubeSearchTool,
)
from langchain.utilities import WikipediaAPIWrapper
from peewee import CharField, DateTimeField, IntegerField, TextField
from pydantic import BaseModel

from app.base_model import BaseDBModel, get_db
from app.helpers import get_timestamp
from app.tools.math_tool import MathTool
from app.vector_store import VectorStore


class ConversationUpdateOrder(BaseModel):
    conversation_id: str
    order: int


class ConversationChatToolData(BaseModel):
    data: Optional[dict]


class ConversationChatToolEnum(str, Enum):
    llm_math = "llm-math"
    wikipedia = "wikipedia"
    duckduckgo = "duckduckgo"
    youtube = "youtube"


class Conversation(BaseDBModel):
    conversation_id = CharField()
    name = CharField()
    timestamp = DateTimeField()
    system_prompt = TextField()
    memory = TextField()
    order = IntegerField()

    def to_dict(self):
        return {
            "conversation_id": self.conversation_id,
            "name": self.name,
            "timestamp": self.timestamp,
            "system_prompt": self.system_prompt,
            "memory": json.loads(str(self.memory)),
            "order": self.order,
        }


class ConversationService:
    def __init__(self, chat: ChatOpenAI, vector_store: VectorStore):
        self.chat = chat
        self.vector_store = vector_store
        pass

    def list_all(self):
        conversations: List[Conversation] = Conversation.select().order_by(
            Conversation.order.desc()
        )
        return conversations

    def get(self, conversation_id: str) -> dict:
        conversation: Conversation = Conversation.get(
            Conversation.conversation_id == conversation_id
        )
        return conversation.to_dict()

    _helpful_ai = """You are an helpful AI. Try to answer the question in clear and \
informative way. Do not try to make up or hallucinate new answer."""

    def create(self, name: str):
        conversation_id = str(uuid4())
        conversation = Conversation(
            conversation_id=conversation_id,
            name=name,
            timestamp=get_timestamp(),
            system_prompt=self._helpful_ai,
            memory="[]",
        )
        conversation.save()
        return conversation

    def update_name(self, conversation_id: str, name: str):
        conversation = Conversation.get(Conversation.conversation_id == conversation_id)
        conversation.name = name
        conversation.save()
        return conversation

    def update_system_prompt(self, conversation_id: str, system_prompt: str):
        conversation = Conversation.get(Conversation.conversation_id == conversation_id)
        conversation.system_prompt = system_prompt
        conversation.save()
        return conversation

    def update_memory(self, conversation_id: str, memory: list[dict]):
        conversation = Conversation.get(Conversation.conversation_id == conversation_id)
        memory_messages = messages_from_dict(memory)
        conversation.memory = json.dumps(messages_to_dict(memory_messages))
        conversation.save()
        return conversation

    def _make_tools(
        self,
        tools: dict[ConversationChatToolEnum, ConversationChatToolData],
    ):
        math_tool = MathTool(chat=self.chat)
        agent_tools: List[BaseTool] = [math_tool]

        for tool, data in tools.items():
            if tool == ConversationChatToolEnum.wikipedia:
                wikipedia_tool = WikipediaQueryRun(
                    api_wrapper=WikipediaAPIWrapper(wiki_client=wikipedia)
                )
                agent_tools.append(wikipedia_tool)

            if tool == ConversationChatToolEnum.duckduckgo:
                duckduckgo_tool = DuckDuckGoSearchRun()
                agent_tools.append(duckduckgo_tool)

            if tool == ConversationChatToolEnum.youtube:
                youtube_tool = YouTubeSearchTool()
                agent_tools.append(youtube_tool)

        print("===", [t.name for t in agent_tools])
        return agent_tools

    def new_chat(
        self,
        conversation_id: str,
        message: str,
        tools: dict[ConversationChatToolEnum, ConversationChatToolData],
    ):
        conversation = Conversation.get(Conversation.conversation_id == conversation_id)
        memory_messages = messages_from_dict(json.loads(conversation.memory))
        memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
        memory.chat_memory.messages = memory_messages
        agent_tools = self._make_tools(tools)
        agent_kwargs = {
            "system_message": SystemMessage(content=conversation.system_prompt),
            "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
        }

        agent = initialize_agent(
            llm=self.chat,
            tools=agent_tools,
            agent=AgentType.OPENAI_FUNCTIONS,
            agent_kwargs=agent_kwargs,
            memory=memory,
            verbose=True,
        )
        result = agent.run(message)
        print(">>", result)

        conversation.memory = json.dumps(messages_to_dict(memory.chat_memory.messages))
        conversation.save()
        return conversation

    def delete(self, conversation_id: str):
        Conversation.get(Conversation.conversation_id == conversation_id).delete_instance()

    @staticmethod
    def update_orders(data: List[ConversationUpdateOrder]):
        for d in data:
            conversation = Conversation.get(Conversation.conversation_id == d.conversation_id)
            conversation.order = d.order
            conversation.save()


# Create table if not exists
get_db().create_tables([Conversation])
