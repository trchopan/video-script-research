from enum import Enum
from typing import List
from app import youtube_transcript_svc
from fastapi import APIRouter
from pydantic import BaseModel


youtube_transcript_router = APIRouter()


@youtube_transcript_router.get("/list_youtube_videos")
def list_youtube_videos():
    return {"videos": [v.to_dict() for v in youtube_transcript_svc.get_videos()]}


@youtube_transcript_router.get("/youtube_video/{video_id}")
def youtube_video(video_id: str):
    youtube_video = youtube_transcript_svc.get_video(video_id)
    return {"youtube_video": youtube_video.to_dict()}


@youtube_transcript_router.get("/youtube_transcript/{video_id}")
def get_youtube_transcript(video_id: str):
    transcripts = youtube_transcript_svc.get_transcript(video_id)
    return {
        "transcripts": [transcript.to_dict() for transcript in transcripts],
    }


@youtube_transcript_router.delete("/youtube_video/{video_id}")
def delete_youtube_video(video_id: str):
    return youtube_transcript_svc.delete_youtube_video_id(video_id)


class LanguageEnum(str, Enum):
    En = "en"
    Ja = "ja"


class PostYoutubeTranscript(BaseModel):
    video_id: str
    language: LanguageEnum


@youtube_transcript_router.post("/youtube_transcript")
def post_youtube_transcript(body: PostYoutubeTranscript):
    youtube_transcript_svc.pull_video_details(body.video_id)
    transcripts = youtube_transcript_svc.parse_transcript(body.video_id, language=body.language)
    return {
        "transcripts": [transcript.to_dict() for transcript in transcripts],
    }


@youtube_transcript_router.post("/youtube_transcript_embedding/{video_id}")
def get_youtube_transcript_embedding(video_id: str):
    embeddings = youtube_transcript_svc.get_embeddings(video_id)
    return {"embeddings": embeddings}


class YoutubeTranscriptSimilarity(BaseModel):
    links: List[str]
    query: str
    k: int = 10


@youtube_transcript_router.post("/youtube_transcript_similarity")
def youtube_transcript_similarity(body: YoutubeTranscriptSimilarity):
    similarity = youtube_transcript_svc.get_similarity(body.query, body.links, k=body.k)
    return {"similarity": [s.to_dict() for s in similarity]}
