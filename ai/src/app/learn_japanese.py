import json
from multiprocessing.pool import ThreadPool
from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import OutputParserException
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
            self._translate_prompt = config

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
        results: List[LearnJapaneseService.Translation] = []

        total = len(sentences)

        def _process_fn(index: int, sentence: str):
            print(f">> Processing {index+1}/{total}")
            parser = PydanticOutputParser(pydantic_object=LearnJapaneseService.TranslationResponse)
            prompt = self._translate_prompt.format_prompt(
                format_instructions=LearnJapaneseService._translation_parser.get_format_instructions(),
                input=sentence.strip(),
            )
            example_prompt = ChatPromptTemplate.from_messages(
                [
                    ("human", "{input}"),
                    ("ai", "{output}"),
                ]
            )
            examples_args = list(
                map(lambda s: {"input": s[0], "output": s[1]}, self._translate_prompt["few_shots"])
            )

            few_shot_prompt = FewShotChatMessagePromptTemplate(
                example_prompt=example_prompt,
                examples=examples_args,
            )

            system_prompt = PromptTemplate(
                template=self._translate_prompt["prompt"],
                input_variables=["examples"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate(prompt=system_prompt),
                    few_shot_prompt,
                    ("human", "{input}"),
                ]
            )
            chain = prompt | self.chat_4
            result = chain.invoke({"input": sentence})
            resp: LearnJapaneseService.TranslationResponse = parser.invoke(result)

            return LearnJapaneseService.Translation(
                japanese=sentence,
                english=resp.english,
                romaji=resp.romaji,
                explainations=resp.explainations,
            )

        with ThreadPool(processes=5) as pool:
            workers = [pool.apply_async(_process_fn, (i, s)) for i, s in enumerate(sentences)]
            for worker in workers:
                result = worker.get()
                results.append(result)

        return results

    def break_text_to_chunks(self, text: str):
        dot_mark = "。"
        question_mark = "？"
        comma_mark = "、"

        def clean_japanese(s: str):
            return s.replace('"', "").replace("「", "").replace("」", "")

        chunks: List[str] = []
        count_comma = 0
        acc = ""

        for c in clean_japanese(str(text)):
            if c == comma_mark:
                count_comma = count_comma + 1

            if c in [dot_mark, question_mark] or count_comma >= 3:
                """Found break sentence marks or there are more than 3 commas"""

                # Filter out the comma mark because it can trigger completion in Japanese.
                # This is because the Japanese quality in the LLM is still weak in following
                # instructions.
                if c == comma_mark:
                    next_char = ""
                else:
                    next_char = c

                chunks.append(acc + next_char)
                acc = ""
                count_comma = 0
            else:
                acc = acc + c

        return chunks

    def process_text(self, text: str):
        chunks = self.break_text_to_chunks(text)
        return self.process_sentences(chunks)

    def process_youtube_video_chunks(self, video_id: str, chunks: List[int]):
        video_transcripts = self.youtube_transcript_svc.get_transcript(video_id)

        processed_video_chunks: List[YoutubeTranscript] = []

        for chunk in chunks:
            video_transcript = video_transcripts[chunk]

            translated_sentences = self.process_text(str(video_transcript.text))

            video_transcript_db = YoutubeTranscript.get(
                video_id=video_transcript.video_id, chunk=chunk
            )
            video_transcript_db.learn_japanese = json.dumps(
                [s.dict() for s in translated_sentences]
            )
            video_transcript_db.save()

            processed_video_chunks.append(video_transcript_db)

        return processed_video_chunks
