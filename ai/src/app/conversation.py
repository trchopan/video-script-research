from enum import Enum
import json
from typing import List, Optional
from uuid import uuid4
from langchain import OpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage, messages_from_dict, messages_to_dict
from peewee import CharField, DateTimeField, TextField
from langchain.tools import (
    BaseTool,
    DuckDuckGoSearchRun,
    WikipediaQueryRun,
    YouTubeSearchTool,
)
from langchain.utilities import WikipediaAPIWrapper
from pydantic import BaseModel
import wikipedia

from app.tools.math_tool import MathTool
from app.vector_store import VectorStore
from app.base_model import BaseDBModel, get_db
from app.helpers import get_timestamp


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

    def to_dict(self):
        return {
            "conversation_id": self.conversation_id,
            "name": self.name,
            "timestamp": self.timestamp,
            "system_prompt": self.system_prompt,
            "memory": json.loads(str(self.memory)),
        }


class ConversationService:
    def __init__(self, chat: ChatOpenAI, llm: OpenAI, vector_store: VectorStore):
        self.chat = chat
        self.llm = llm
        self.vector_store = vector_store
        pass

    def list_all(self):
        conversations: List[Conversation] = Conversation.select().order_by(
            Conversation.timestamp
        )
        return conversations

    def get(self, conversation_id: str) -> dict:
        conversation: Conversation = Conversation.get(
            Conversation.conversation_id == conversation_id
        )
        return conversation.to_dict()

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
        Conversation.get(
            Conversation.conversation_id == conversation_id
        ).delete_instance()

    _code_helper = """I want you to act as a software developer. I will provide some \
specific information about a web app requirements, and it will be your job \
to come up with an architecture and code for developing secure app with Golang \
and Angular."""

    _helpful_ai = """You are an helpful AI. Try to answer the question in clear and \
informative way. Do not try to make up answer or hallucinate."""

    def get_templates(self) -> list[dict]:
        return [
            {"name": "Software Developer", "template": self._code_helper},
            {"name": "Helpful Assistant", "template": self._helpful_ai},
        ]


# Create table if not exists
get_db().create_tables([Conversation])
