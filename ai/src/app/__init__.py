from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from app.assistant_writer import AssistantWriterService

from app.vector_store import VectorStore
from app.general_knowledge import GeneralKnowledgeService
from app.youtube_transcript import YoutubeTranscriptService
from .secret import secret
from .base_model import get_db

vector_store = VectorStore(get_db)

chat = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,
    openai_api_key=secret.get("OPENAI_API_KEY"),
    max_tokens=1500,
)  # type: ignore

embeddings = OpenAIEmbeddings(
    openai_api_key=secret.get("OPENAI_API_KEY")
)  # type: ignore


youtube_transcript_svc = YoutubeTranscriptService(
    secret.get("YOUTUBE_API_KEY"), chat, embeddings, vector_store
)
assistant_writer_svc = AssistantWriterService(chat)
general_knowledge_svc = GeneralKnowledgeService(chat)
