from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

from app import learn_japanese_svc

learn_japanese_router = APIRouter()


class PostLearnJapaneseTranslate(BaseModel):
    sentences: List[str]


@learn_japanese_router.post("/learn_japanese_translate")
def post_learn_japanese_translate(body: PostLearnJapaneseTranslate):
    result = learn_japanese_svc.process_sentences(body.sentences)
    return {"translates": result}


class PostLearnJapaneseProcessVideo(BaseModel):
    chunks: List[int]


@learn_japanese_router.post("/learn_japanese_process_video/{video_id}")
def post_learn_japanese_process_video(video_id: str, body: PostLearnJapaneseProcessVideo):
    result = learn_japanese_svc.process_youtube_video_chunks(video_id, body.chunks)
    return {"learn_japanese": [r.to_dict() for r in result]}
