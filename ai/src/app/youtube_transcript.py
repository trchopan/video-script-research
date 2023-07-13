from datetime import datetime
import requests
from typing import List, Tuple
from urllib.parse import parse_qs, urlparse
from peewee import CharField, DateTimeField, FloatField, IntegerField, TextField
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from app.vector_store import VectorStore
from app.helpers import find_element


from .base_model import BaseModel, from_int, from_str, get_db, to_float

class YoutubeVideo(BaseModel):
    video_id = CharField()
    thumbnail = CharField(max_length=1024)
    title = CharField()
    description = TextField()
    channel = CharField()
    channel_id = CharField()
    publish_at = DateTimeField()

    def to_dict(self):
        return {
            "video_id": self.video_id,
            "thumbnail": self.thumbnail,
            "title": self.title,
            "description": self.description,
            "channel": self.channel,
            "channel_id": self.channel_id,
            "publish_at": str(self.publish_at),
        }


class YoutubeTranscript(BaseModel):
    video_id = CharField()
    chunk = IntegerField()
    start = FloatField()
    text = TextField()

    def to_dict(self):
        return {
            # "video_id": self.video_id,
            "chunk": self.chunk,
            "start": self.start,
            "text": self.text,
        }


class YoutubeTranscriptSimilarity:
    namespace: str
    document: str
    chunk: int
    content: str
    start: float
    similarity: float

    def __init__(
        self,
        namespace: str,
        document: str,
        chunk: int,
        content: str,
        start: float,
        similarity: float,
    ) -> None:
        self.namespace = namespace
        self.document = document
        self.chunk = chunk
        self.content = content
        self.start = start
        self.similarity = similarity

    def to_dict(self) -> dict:
        result: dict = {}
        result["namespace"] = from_str(self.namespace)
        result["document"] = from_str(self.document)
        result["chunk"] = from_int(self.chunk)
        result["content"] = from_str(self.content)
        result["start"] = to_float(self.start)
        result["similarity"] = to_float(self.similarity)
        return result


class YoutubeTranscriptService:
    _EMBEDDING_NAMESPACE = "youtube-transcript"
    _CHUNK_SIZE = 1000
    _CHUNK_OVERLAP = 200

    def __init__(
        self,
        api_key: str,
        chat: ChatOpenAI,
        embeddings: OpenAIEmbeddings,
        vector_store: VectorStore,
    ):
        self.api_key = api_key
        self.chat = chat
        self.embeddings = embeddings
        self.vector_store = vector_store

    _puncturation_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "Below is a Script that missing punctuation. Help add in the approriate punctuations in the Output\n\n"
                "Script:\n{script}\n\n"
            ),
            HumanMessagePromptTemplate.from_template("Text:"),
        ]
    )

    def get_videos(self):
        videos: list[YoutubeVideo] = list(YoutubeVideo.select())
        return videos

    def get_video_details(self, link: str, clear_cache: bool = False) -> YoutubeVideo:
        video_id = self.get_youtube_video_id(link) or ""

        if clear_cache:
            YoutubeVideo.delete().where(YoutubeVideo.video_id == video_id).execute()

        else:
            try:
                yt_video: YoutubeVideo = YoutubeVideo.get(
                    YoutubeVideo.video_id == video_id
                )
                return yt_video
            except:
                pass

        payload = {
            "id": video_id,
            "part": "contentDetails,snippet",
            "key": self.api_key,
        }
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/videos", params=payload
        )
        if response.status_code != 200:
            print(response.text)
            raise Exception("error getting youtube details")

        resp_dict = response.json()
        snippet = resp_dict["items"][0]["snippet"]
        publish_at = datetime.strptime(snippet["publishedAt"], "%Y-%m-%dT%H:%M:%S%z")
        yt_video = YoutubeVideo(
            video_id=video_id,
            thumbnail=snippet["thumbnails"]["standard"]["url"],
            title=snippet["title"],
            description=snippet["description"],
            channel=snippet["channelTitle"],
            channel_id=snippet["channelId"],
            publish_at=publish_at,
        )
        yt_video.save()
        return yt_video

    def get_parsed_transcript(
        self, link: str, clear_cache: bool = False
    ) -> list[YoutubeTranscript]:
        self.get_video_details(link, clear_cache=clear_cache)

        video_id = self.get_youtube_video_id(link) or ""

        if clear_cache:
            YoutubeTranscript.delete().where(
                YoutubeTranscript.video_id == video_id
            ).execute()

            self.vector_store.delete_embeddings(
                namespace=self._EMBEDDING_NAMESPACE,
                document=video_id,
            )

        else:
            transcripts: List[YoutubeTranscript] = list(
                YoutubeTranscript.select().where(YoutubeTranscript.video_id == video_id)
            )

            if transcripts is not None and len(transcripts) > 0:
                return transcripts

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._CHUNK_SIZE,
            chunk_overlap=self._CHUNK_OVERLAP,
        )
        youtube_transcripts_: list[dict] = YouTubeTranscriptApi.get_transcript(video_id)
        youtube_transcripts: list[dict] = []
        for i, t in enumerate(youtube_transcripts_):
            if i % 3 == 0:
                youtube_transcripts.append(
                    {
                        "text": t.get("text", ""),
                        "start": t.get("start"),
                    }
                )
                if len(youtube_transcripts) > 2:
                    # Add a little bit of overlap
                    youtube_transcripts[-1]["text"] = (
                        youtube_transcripts[-2]["text"][-20:]
                        + youtube_transcripts[-1]["text"]
                    )
            else:
                youtube_transcripts[-1]["text"] += "\n" + t.get("text", "")

        transcripts_fulltext = "\n".join(
            [t.get("text", "").strip() for t in youtube_transcripts_]
        )
        splitted_texts = text_splitter.split_text(transcripts_fulltext)
        transcript_starts = []

        def transcript_has_text(yt_transcript: dict, splited_text: str) -> bool:
            _text_to_check = (
                yt_transcript.get("text", "").replace(" ", "").replace("\n", "").strip()
            )
            _splitted_text = splited_text.replace(" ", "").replace("\n", "").strip()

            return _splitted_text[0:20] in _text_to_check

        for text in splitted_texts:
            found = find_element(
                youtube_transcripts,
                lambda transcript: transcript_has_text(transcript, text),
            )
            transcript_starts.append(
                found.get("start", 0.0) if found is not None else 0.0
            )

        results: list[Tuple[str, list[float]]] = []
        for i, text in enumerate(splitted_texts):
            print(
                f">>> processing {self._EMBEDDING_NAMESPACE} {video_id}: "
                f"{i + 1}/{len(splitted_texts)}"
            )
            prompt = self._puncturation_prompt.format_prompt(script=text)
            result = self.chat(prompt.to_messages())
            embeddings = self.embeddings.embed_query(result.content)
            results.append((result.content, embeddings))

        transcripts = []
        for i, [(content, embeddings), start] in enumerate(
            zip(results, transcript_starts)
        ):
            transcript = YoutubeTranscript(
                video_id=video_id,
                chunk=i,
                start=start,
                text=content,
            )
            transcript.save()

            self.vector_store.insert_embeddings(
                namespace=self._EMBEDDING_NAMESPACE,
                document=video_id,
                chunk=i,
                embeddings=embeddings,
            )

            transcripts.append(transcript)

        return transcripts

    def get_embeddings(self, link: str):
        video_id = self.get_youtube_video_id(link) or ""
        embeddings = self.vector_store.get_embeddings(
            namespace=self._EMBEDDING_NAMESPACE, document=video_id
        )
        return embeddings

    def get_similarity(self, query: str, links: List[str], k: int = 5):
        video_ids = [self.get_youtube_video_id(link) or "" for link in links]
        query_embedding = self.embeddings.embed_query(query)

        similarity_results: List[YoutubeTranscriptSimilarity] = []
        single_limit = round(k / len(links))
        for video_id in video_ids:
            similarities = self.vector_store.similarity_search(
                query_embedding,
                namespace=self._EMBEDDING_NAMESPACE,
                document=video_id,
                limit=single_limit,
            )
            transcripts: List[YoutubeTranscript] = list(
                YoutubeTranscript.select().where(YoutubeTranscript.video_id == video_id)
            )
            results = []
            for sim in similarities:
                transcript = find_element(transcripts, lambda t: t.chunk == sim.chunk)
                start = transcript.start if transcript is not None else 0.0
                content = str(transcript.text) if transcript is not None else ""
                results.append(
                    YoutubeTranscriptSimilarity(
                        namespace=self._EMBEDDING_NAMESPACE,
                        document=sim.document,
                        chunk=sim.chunk,
                        start=start + 0.0,
                        content=content,
                        similarity=sim.similarity,
                    )
                )

            similarity_results.extend(results)

        similarity_results.sort(key=lambda r: r.similarity, reverse=True)
        return similarity_results[0:k]

    def get_youtube_video_id(self, link: str) -> str | None:
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        query = urlparse(link)
        if query.hostname == "youtu.be":
            return query.path[1:]
        if query.hostname in ("www.youtube.com", "youtube.com"):
            if query.path == "/watch":
                p = parse_qs(query.query)
                return p["v"][0]
            if query.path[:7] == "/embed/":
                return query.path.split("/")[2]
            if query.path[:3] == "/v/":
                return query.path.split("/")[2]
        # fail?
        return None


# Create table if not exists
get_db().create_tables([YoutubeVideo, YoutubeTranscript])
