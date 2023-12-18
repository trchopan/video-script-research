import os
from dotenv import load_dotenv
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
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
        model_name=model,
        temperature=0.3,
        openai_api_key=os.environ["OPENAI_API_KEY"],
        # max_tokens=5000,
    )  # type: ignore


chat_3 = create_chat_open_ai(model="gpt-3.5-turbo")
chat_3_with_function = create_chat_open_ai(model="gpt-3.5-turbo-0613")
chat_4 = create_chat_open_ai(model="gpt-4-1106-preview")
chat_4_with_function = create_chat_open_ai(model="gpt-4-0613")

llm = OpenAI(
    model_name="text-davinci-003",
    temperature=0.3,
    openai_api_key=os.environ["OPENAI_API_KEY"],
    # max_tokens=4000,
)  # type: ignore

embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])  # type: ignore

app_state_svc = AppStateService()
youtube_transcript_svc = YoutubeTranscriptService(
    api_key=os.environ["YOUTUBE_API_KEY"],
    chat35=chat_3,
    embeddings=embeddings,
    vector_store=vector_store,
)
assistant_writer_svc = AssistantWriterService(chat_4)
general_knowledge_svc = GeneralKnowledgeService(chat_4)

speech_svc = SpeechService(
    openai_api_key=os.environ["OPENAI_API_KEY"],
)

conversation_svc = ConversationService(chat_4, vector_store)
system_prompt_svc = SystemPromptService()

BaseService.load(
    llm=llm,
    chat_3=chat_3,
    chat_3_with_function=chat_3_with_function,
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
