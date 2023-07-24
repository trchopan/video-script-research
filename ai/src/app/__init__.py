import os
from dotenv import load_dotenv
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

from .base_model import get_db
from .app_state import AppStateService
from .assistant_writer import AssistantWriterService
from .speech import SpeechService
from .vector_store import VectorStore
from .general_knowledge import GeneralKnowledgeService
from .youtube_transcript import YoutubeTranscriptService
from .conversation import ConversationService

load_dotenv()

vector_store = VectorStore(get_db)

chat = ChatOpenAI(
    model="gpt-3.5-turbo-16k-0613",
    temperature=0.3,
    openai_api_key=os.environ["OPENAI_API_KEY"],
    max_tokens=1500,
)  # type: ignore


llm = OpenAI(
    model="gpt-3.5-turbo",
    temperature=0.3,
    openai_api_key=os.environ["OPENAI_API_KEY"],
    max_tokens=1500,
)  # type: ignore

embeddings = OpenAIEmbeddings(
    openai_api_key=os.environ["OPENAI_API_KEY"]
)  # type: ignore


app_state_svc = AppStateService()
youtube_transcript_svc = YoutubeTranscriptService(
    os.environ["YOUTUBE_API_KEY"], chat, embeddings, vector_store,
)
assistant_writer_svc = AssistantWriterService(chat)
general_knowledge_svc = GeneralKnowledgeService(chat)

speech_svc = SpeechService(
    openai_api_key=os.environ["OPENAI_API_KEY"],
)

conversation_svc = ConversationService(chat, llm, vector_store)

__all__ = [
    "app_state_svc",
    "assistant_writer_svc",
    "general_knowledge_svc",
    "speech_svc",
    "conversation_svc",
]
