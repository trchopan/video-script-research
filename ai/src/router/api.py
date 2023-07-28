from fastapi import APIRouter

from .app_state import app_state_router
from .assistant_writer import assistant_writer_router
from .youtube_transcript import youtube_transcript_router
from .general_knowledge import general_knowledge_router
from .conversation import conversation_router
from .speech import speech_router
from .system_prompt import system_prompt_router

router = APIRouter(prefix="/api")
router.include_router(app_state_router)
router.include_router(youtube_transcript_router)
router.include_router(general_knowledge_router)
router.include_router(assistant_writer_router)
router.include_router(conversation_router)
router.include_router(speech_router)
router.include_router(system_prompt_router)

