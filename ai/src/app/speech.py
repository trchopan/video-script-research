import tempfile

from openai import OpenAI
from fastapi import HTTPException


class SpeechService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_transcript_whisper(self, audio_file: bytes):
        """This function takes an audio file and returns the transcript text"""
        if len(audio_file) == 0:
            raise HTTPException(status_code=400, detail="no audio data")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpfile = f"{tmpdir}/sample.ogg"
            with open(tmpfile, "wb") as fb:
                fb.write(audio_file)

            with open(tmpfile, "rb") as fb:
                transcript = self.client.audio.transcriptions.create(model="whisper-1", file=fb)
                return transcript.text  # type: ignore
