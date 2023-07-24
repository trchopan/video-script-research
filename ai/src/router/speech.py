from typing import Annotated
from fastapi import APIRouter, File

from app import speech_svc

speech_router = APIRouter()


@speech_router.post("/speech_to_text")
def speech_to_text(
    file: Annotated[
        bytes,
        File(
            title="SpeedAudioFile",
            description="Should be in bytes blob",
        ),
    ]
):
    transcript = speech_svc.get_transcript_whisper(file)
    return {"transcript": transcript}
