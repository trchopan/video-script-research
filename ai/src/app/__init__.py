from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from pgvector.psycopg2 import register_vector
from app.assistant_writer import AssistantWriterService

from app.embedding_store import EmbeddingStore
from app.general_knowledge import GeneralKnowledgeService
from app.youtube_transcript import (
    YoutubeTranscript,
    YoutubeTranscriptService,
    YoutubeVideo,
)
from .secret import secret
from .base_model import db

register_vector(db)
db.create_tables([YoutubeVideo, YoutubeTranscript])

embedding_store = EmbeddingStore(db)
embedding_store.create_table()

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
    secret.get("YOUTUBE_API_KEY"), chat, embeddings, embedding_store
)
assistant_writer_svc = AssistantWriterService(chat)
general_knowledge_svc = GeneralKnowledgeService(chat)
