import json
from pydantic import BaseModel, Field
import yaml
from typing import List
from langchain.output_parsers import PydanticOutputParser


from app.base_service import BaseService
from app.youtube_transcript import YoutubeTranscript, YoutubeTranscriptService


class LearnJapaneseService(BaseService):
    def __init__(self, youtube_transcript_svc: YoutubeTranscriptService):
        self.youtube_transcript_svc = youtube_transcript_svc
        with open("./prompts/learn_japanese.yaml") as f:
            config = yaml.safe_load(f)

        self._translate_prompt = BaseService.load_messages(config, "Translate")

    class TranslationResponse(BaseModel):
        english: str = Field(description="English translation")
        romaji: str = Field(description="Romaji form")
        explainations: List[str] = Field(description=("List of explainations."))

    class Translation(TranslationResponse):
        japanese: str

    _translation_parser = PydanticOutputParser(pydantic_object=TranslationResponse)

    def process_sentences(self, sentences: List[str]):
        """This function process sentences to it's romanji
        and breakdown the words inside with explaination
        """
        results: List[LearnJapaneseService.TranslationResponse] = []
        for sentence in sentences:
            prompt = self._translate_prompt.format_prompt(
                format_instructions=LearnJapaneseService._translation_parser.get_format_instructions(),
                input=sentence.strip(),
            )
            print(">>", prompt.to_string())
            response = self.chat_3(prompt.to_messages())
            response: LearnJapaneseService.TranslationResponse = (
                LearnJapaneseService._translation_parser.parse(response.content)
            )
            result = LearnJapaneseService.Translation(
                japanese=sentence,
                english=response.english,
                romaji=response.romaji,
                explainations=response.explainations,
            )
            results.append(result)

        return results

    def process_youtube_video_chunks(self, video_id: str, chunks: List[int]):
        video_transcripts = self.youtube_transcript_svc.get_transcript(video_id)

        dot_mark = "。"
        question_mark = "？"
        comma_mark = "、"

        processed_video_chunks: List[YoutubeTranscript] = []

        def clean_japanese(s: str):
            return s.replace('"', "").replace("「", "").replace("」", "")

        for chunk in chunks:
            video_transcript = video_transcripts[chunk]

            sentences: List[str] = []
            acc = ""
            count_comma = 0
            for c in clean_japanese(str(video_transcript.text)):
                if c == comma_mark:
                    count_comma = count_comma + 1

                if c in [dot_mark, question_mark] or count_comma >= 3:
                    """Found break sentence marks or there are more than 3 commas"""
                    sentences.append(acc + c)
                    acc = ""
                    count_comma = 0
                else:
                    acc = acc + c

            translated_sentences = self.process_sentences(sentences)
            video_transcript_db = YoutubeTranscript.get(
                video_id=video_transcript.video_id, chunk=chunk
            )
            video_transcript_db.learn_japanese = json.dumps(
                [s.dict() for s in translated_sentences]
            )
            video_transcript_db.save()

            processed_video_chunks.append(video_transcript_db)

        return processed_video_chunks
