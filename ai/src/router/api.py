from typing import Annotated
from fastapi import APIRouter, File

from app import speech_to_text_svc

from .app_state import app_state_router
from .assistant_writer import assistant_writer_router
from .youtube_transcript import youtube_transcript_router
from .general_knowledge import general_knowledge_router
from .conversation import conversation_router

router = APIRouter(prefix="/api")
router.include_router(app_state_router)
router.include_router(youtube_transcript_router)
router.include_router(general_knowledge_router)
router.include_router(assistant_writer_router)
router.include_router(conversation_router)


@router.post("/speech_to_text")
def speech_to_text(
    file: Annotated[
        bytes,
        File(
            title="SpeedAudioFile",
            description="Should be in bytes blob",
        ),
    ]
):
    transcript = speech_to_text_svc.get_transcript_whisper(file)
    return {"transcript": transcript}
