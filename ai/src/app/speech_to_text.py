from google.cloud import speech


class SpeechToTextService:
    def __init__(self, client: speech.SpeechClient):
        self.client = client
        self.config = speech.RecognitionConfig(language_code="en")
        pass

    def get_transcript(self, audio_file: bytes):
        """This function takes an audio file and returns the transcript text"""
        audio = speech.RecognitionAudio(content=audio_file)
        response = self.client.recognize(config=self.config, audio=audio)
        result = response.results[0]
        return result.alternatives[0].transcript
