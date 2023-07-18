from fastapi import HTTPException
import openai
import tempfile


class SpeechToTextService:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key

    def get_transcript_whisper(self, audio_file: bytes):
        """This function takes an audio file and returns the transcript text"""
        if len(audio_file) == 0:
            raise HTTPException(status_code=400, detail="no audio data")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpfile = f"{tmpdir}/sample.ogg"
            with open(tmpfile, "wb") as fb:
                fb.write(audio_file)

            with open(tmpfile, "rb") as fb:
                transcript = openai.Audio.transcribe(
                    "whisper-1", fb, api_key=self.openai_api_key
                )
                return transcript.text  # type: ignore
