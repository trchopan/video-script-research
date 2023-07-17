from typing import Annotated, List
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, File
import os

from pydantic import BaseModel
from app import (
    app_state_svc,
    youtube_transcript_svc,
    assistant_writer_svc,
    general_knowledge_svc,
    speech_to_text_svc,
)

app = FastAPI()


@app.get("/healthz")
def healthz():
    return "healthy", 200


@app.get("/app_state_list")
def app_state_list():
    return {
        "app_states": [app_state.to_dict() for app_state in app_state_svc.list_all()],
    }, 200


@app.get("/app_state/<app_id>")
def app_state_get(app_id: str):
    return {"app_state": app_state_svc.get(app_id)}, 200


class AppStateCreate(BaseModel):
    name: str
    data: dict


@app.post("/app_state")
def app_state_create(body: AppStateCreate):
    app_id = app_state_svc.create(body.name, body.data)
    return {"app_id": app_id}, 200


class AppStateSave(BaseModel):
    data: dict


@app.post("/app_state/{app_id}")
def app_state_save(app_id: str, body: AppStateSave):
    app_state_svc.save(app_id, body.data)
    return "saved", 200


@app.delete("/app_state/{app_id}")
def app_state_delete(app_id: str):
    app_state_svc.delete(app_id)
    return "deleted", 200


@app.get("/list_youtube_videos")
def list_youtube_videos():
    return {"videos": [v.to_dict() for v in youtube_transcript_svc.get_videos()]}, 200


class YoutubeVideo(BaseModel):
    link: str


@app.post("/youtube_video")
def youtube_video(clear_cache: bool, body: YoutubeVideo):
    youtube_video = youtube_transcript_svc.get_video_details(
        body.link, clear_cache=clear_cache
    )
    return {"youtube_video": youtube_video.to_dict()}, 200


class GetYoutubeTranscript:
    link: str


@app.post("/get_youtube_transcript")
def get_youtube_transcript(clear_cache: bool, body: GetYoutubeTranscript):
    transcripts = youtube_transcript_svc.get_parsed_transcript(
        body.link, clear_cache=clear_cache
    )
    return {
        "transcripts": [transcript.to_dict() for transcript in transcripts],
    }, 200


class GetYoutubeTranscriptEmbedding(BaseModel):
    link: str


@app.post("/get_youtube_transcript_embedding")
def get_youtube_transcript_embedding(body: GetYoutubeTranscriptEmbedding):
    embeddings = youtube_transcript_svc.get_embeddings(body.link)
    return {"embeddings": embeddings}, 200


class YoutubeTranscriptSimilarity(BaseModel):
    links: List[str]
    query: str


@app.post("/youtube_transcript_similarity")
def youtube_transcript_similarity(k: bool, body: YoutubeTranscriptSimilarity):
    similarity = youtube_transcript_svc.get_similarity(body.query, body.links, k=k or 5)
    return {"similarity": [s.to_dict() for s in similarity]}, 200


class GeneralKnowledgeWikipediaSearch(BaseModel):
    search: str


@app.post("/general_knowledge_wikipedia_search")
def general_knowledge_wikipedia_search(body: GeneralKnowledgeWikipediaSearch):
    return {"search_results": general_knowledge_svc.search_page(body.search)}, 200


class GeneralKnowledgeWikipediaPage(BaseModel):
    search: str


@app.post("/general_knowledge_wikipedia_page")
def general_knowledge_wikipedia_page(body: GeneralKnowledgeWikipediaPage):
    return {"page": general_knowledge_svc.get_wikipedia_page(body.search)}, 200


class GeneralKnowledgeWikipediaSummary(BaseModel):
    search: str


@app.post("/general_knowledge_wikipedia_summary")
def general_knowledge_wikipedia_summary(body: GeneralKnowledgeWikipediaSummary):
    return {"summary": general_knowledge_svc.get_wikipedia_summary(body.search)}, 200


class AssistantWriterExtendWithContext(BaseModel):
    content: str
    context: List[str]


@app.post("/assistant_writer_extend_with_context")
def assistant_writer_extend_with_context(body: AssistantWriterExtendWithContext):
    res = assistant_writer_svc.extend_content_with_context(
        content=body.content, context=body.context
    )
    return {"extended_content": res}, 200


class AssistantExtractInformation(BaseModel):
    documents: str


@app.post("/assistant_extract_information")
def assistant_extract_information(body: AssistantExtractInformation):
    res = assistant_writer_svc.extract_information(documents=body.documents)
    return {"scratch_pad": res}, 200


class AssistantTranslate(BaseModel):
    text: str
    language: str


@app.post("/assistant_translate")
def assistant_translate(body: AssistantTranslate):
    res = assistant_writer_svc.translate(text=body.text, language=body.language)
    return {"translated": res}, 200


class AssistantFormat(BaseModel):
    text: str


@app.post("/assistant_format")
def assistant_format(body: AssistantFormat):
    res = assistant_writer_svc.format_text(text=body.text)
    return {"formated": res}, 200


class AssistantChat(BaseModel):
    chat: str


@app.post("/assistant_chat")
def assistant_chat(body: AssistantChat):
    res = assistant_writer_svc.get_chat(chat=body.chat)
    return {"response": res}, 200


@app.post("/speech")
def speech(file: Annotated[bytes, File()]):
    transcript = speech_to_text_svc.get_transcript(file)
    return {"transcript": transcript}, 200


app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
