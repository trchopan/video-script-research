from typing import List
from app import youtube_transcript_svc
from fastapi import APIRouter
from pydantic import BaseModel


youtube_transcript_router = APIRouter()


@youtube_transcript_router.get("/list_youtube_videos")
def list_youtube_videos():
    return {"videos": [v.to_dict() for v in youtube_transcript_svc.get_videos()]}


class YoutubeVideo(BaseModel):
    link: str


@youtube_transcript_router.post("/youtube_video")
def youtube_video(body: YoutubeVideo, clear_cache: bool = False):
    youtube_video = youtube_transcript_svc.get_video_details(
        body.link, clear_cache=clear_cache
    )
    return {"youtube_video": youtube_video.to_dict()}


class GetYoutubeTranscript(BaseModel):
    link: str


@youtube_transcript_router.post("/get_youtube_transcript")
def get_youtube_transcript(body: GetYoutubeTranscript, clear_cache: bool = False):
    transcripts = youtube_transcript_svc.get_parsed_transcript(
        body.link, clear_cache=clear_cache
    )
    return {
        "transcripts": [transcript.to_dict() for transcript in transcripts],
    }


class GetYoutubeTranscriptEmbedding(BaseModel):
    link: str


@youtube_transcript_router.post("/get_youtube_transcript_embedding")
def get_youtube_transcript_embedding(body: GetYoutubeTranscriptEmbedding):
    embeddings = youtube_transcript_svc.get_embeddings(body.link)
    return {"embeddings": embeddings}


class YoutubeTranscriptSimilarity(BaseModel):
    links: List[str]
    query: str
    k: int = 10


@youtube_transcript_router.post("/youtube_transcript_similarity")
def youtube_transcript_similarity(body: YoutubeTranscriptSimilarity):
    similarity = youtube_transcript_svc.get_similarity(body.query, body.links, k=body.k)
    return {"similarity": [s.to_dict() for s in similarity]}
