import os
from dotenv import load_dotenv
from langchain_core.pydantic_v1 import SecretStr
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.base_service import BaseService

from app.learn_japanese import LearnJapaneseService

from .base_model import get_db
from .app_state import AppStateService
from .assistant_writer import AssistantWriterService
from .speech import SpeechService
from .vector_store import VectorStore
from .general_knowledge import GeneralKnowledgeService
from .youtube_transcript import YoutubeTranscriptService
from .conversation import ConversationService
from .system_prompt import SystemPromptService

load_dotenv()

vector_store = VectorStore(get_db)


def create_chat_open_ai(model: str):
    return ChatOpenAI(
        model=model,
        temperature=0.3,
        api_key=SecretStr(os.environ["OPENAI_API_KEY"]),
    )


chat_4 = create_chat_open_ai(model="gpt-4o")
chat_4_with_function = create_chat_open_ai(model="gpt-4o")

embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])  # type: ignore

app_state_svc = AppStateService()
youtube_transcript_svc = YoutubeTranscriptService(
    api_key=os.environ["YOUTUBE_API_KEY"],
    chat=chat_4,
    embeddings=embeddings,
    vector_store=vector_store,
)
assistant_writer_svc = AssistantWriterService(chat_4)
general_knowledge_svc = GeneralKnowledgeService(chat_4)

speech_svc = SpeechService(api_key=os.environ["OPENAI_API_KEY"])

conversation_svc = ConversationService(chat_4, vector_store)
system_prompt_svc = SystemPromptService()

BaseService.load(
    chat_4=chat_4,
    chat_4_with_function=chat_4_with_function,
)
learn_japanese_svc = LearnJapaneseService(youtube_transcript_svc=youtube_transcript_svc)

__all__ = [
    "app_state_svc",
    "assistant_writer_svc",
    "general_knowledge_svc",
    "speech_svc",
    "conversation_svc",
    "system_prompt_svc",
    "learn_japanese_svc",
]
