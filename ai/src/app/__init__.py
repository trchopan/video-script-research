import os
from dotenv import load_dotenv
from google.cloud import speech
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from app.app_state import AppStateService
from app.assistant_writer import AssistantWriterService
from app.speech_to_text import SpeechToTextService

from app.vector_store import VectorStore
from app.general_knowledge import GeneralKnowledgeService
from app.youtube_transcript import YoutubeTranscriptService
from .base_model import get_db

load_dotenv()

vector_store = VectorStore(get_db)

chat = ChatOpenAI(
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
    os.environ["YOUTUBE_API_KEY"], chat, embeddings, vector_store
)
assistant_writer_svc = AssistantWriterService(chat)
general_knowledge_svc = GeneralKnowledgeService(chat)

speech_to_text_client = speech.SpeechClient()
speech_to_text_svc = SpeechToTextService(speech_to_text_client)
