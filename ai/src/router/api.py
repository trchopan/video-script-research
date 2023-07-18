from typing import Annotated, List
from fastapi import APIRouter, File


from pydantic import BaseModel
from app import (
    app_state_svc,
    youtube_transcript_svc,
    assistant_writer_svc,
    general_knowledge_svc,
    speech_to_text_svc,
)

router = APIRouter(prefix="/api")


@router.get("/app_state_list")
def app_state_list():
    return {
        "app_states": [app_state.to_dict() for app_state in app_state_svc.list_all()],
    }


@router.get("/app_state/{app_id}")
def app_state_get(app_id: str):
    return {"app_state": app_state_svc.get(app_id)}


class AppStateCreate(BaseModel):
    name: str
    data: dict


@router.post("/app_state")
def app_state_create(body: AppStateCreate):
    app_id = app_state_svc.create(body.name, body.data)
    return {"app_id": app_id}


class AppStateUpdateData(BaseModel):
    data: dict


@router.post("/app_state/{app_id}")
def app_state_update_data(app_id: str, body: AppStateUpdateData):
    app_state_svc.update_data(app_id, data=body.data)
    return "saved"


class AppStateUpdateName(BaseModel):
    name: str


@router.post("/app_state/{app_id}")
def app_state_update_name(app_id: str, body: AppStateUpdateName):
    app_state_svc.update_name(app_id, name=body.name)
    return "saved"


@router.delete("/app_state/{app_id}")
def app_state_delete(app_id: str):
    app_state_svc.delete(app_id)
    return "deleted"


@router.get("/list_youtube_videos")
def list_youtube_videos():
    return {"videos": [v.to_dict() for v in youtube_transcript_svc.get_videos()]}


class YoutubeVideo(BaseModel):
    link: str


@router.post("/youtube_video")
def youtube_video(body: YoutubeVideo, clear_cache: bool = False):
    youtube_video = youtube_transcript_svc.get_video_details(
        body.link, clear_cache=clear_cache
    )
    return {"youtube_video": youtube_video.to_dict()}


class GetYoutubeTranscript(BaseModel):
    link: str


@router.post("/get_youtube_transcript")
def get_youtube_transcript(body: GetYoutubeTranscript, clear_cache: bool = False):
    transcripts = youtube_transcript_svc.get_parsed_transcript(
        body.link, clear_cache=clear_cache
    )
    return {
        "transcripts": [transcript.to_dict() for transcript in transcripts],
    }


class GetYoutubeTranscriptEmbedding(BaseModel):
    link: str


@router.post("/get_youtube_transcript_embedding")
def get_youtube_transcript_embedding(body: GetYoutubeTranscriptEmbedding):
    embeddings = youtube_transcript_svc.get_embeddings(body.link)
    return {"embeddings": embeddings}


class YoutubeTranscriptSimilarity(BaseModel):
    links: List[str]
    query: str
    k: int = 10


@router.post("/youtube_transcript_similarity")
def youtube_transcript_similarity(body: YoutubeTranscriptSimilarity):
    similarity = youtube_transcript_svc.get_similarity(body.query, body.links, k=body.k)
    return {"similarity": [s.to_dict() for s in similarity]}


class GeneralKnowledgeWikipediaSearch(BaseModel):
    search: str


@router.post("/general_knowledge_wikipedia_search")
def general_knowledge_wikipedia_search(body: GeneralKnowledgeWikipediaSearch):
    return {"search_results": general_knowledge_svc.search_page(body.search)}


class GeneralKnowledgeWikipediaPage(BaseModel):
    search: str


@router.post("/general_knowledge_wikipedia_page")
def general_knowledge_wikipedia_page(body: GeneralKnowledgeWikipediaPage):
    return {"page": general_knowledge_svc.get_wikipedia_page(body.search)}


class GeneralKnowledgeWikipediaSummary(BaseModel):
    search: str


@router.post("/general_knowledge_wikipedia_summary")
def general_knowledge_wikipedia_summary(body: GeneralKnowledgeWikipediaSummary):
    return {"summary": general_knowledge_svc.get_wikipedia_summary(body.search)}


class AssistantWriterExtendWithContext(BaseModel):
    content: str
    context: List[str]


@router.post("/assistant_writer_extend_with_context")
def assistant_writer_extend_with_context(body: AssistantWriterExtendWithContext):
    res = assistant_writer_svc.extend_content_with_context(
        content=body.content, context=body.context
    )
    return {"extended_content": res}


class AssistantExtractInformation(BaseModel):
    documents: str


@router.post("/assistant_extract_information")
def assistant_extract_information(body: AssistantExtractInformation):
    res = assistant_writer_svc.extract_information(documents=body.documents)
    return {"scratch_pad": res}


class AssistantTranslate(BaseModel):
    text: str
    language: str


@router.post("/assistant_translate")
def assistant_translate(body: AssistantTranslate):
    res = assistant_writer_svc.translate(text=body.text, language=body.language)
    return {"translated": res}


class AssistantFormat(BaseModel):
    text: str


@router.post("/assistant_format")
def assistant_format(body: AssistantFormat):
    res = assistant_writer_svc.format_text(text=body.text)
    return {"formated": res}


class AssistantChat(BaseModel):
    chat: str


@router.post("/assistant_chat")
def assistant_chat(body: AssistantChat):
    res = assistant_writer_svc.get_chat(chat=body.chat)
    return {"response": res}


@router.post("/speech_to_text")
def speech_to_text(
    file: Annotated[
        bytes,
        File(
            title="SpeedAudioFile",
            description="Should be in bytes blob",
        ),
    ]
):
    transcript = speech_to_text_svc.get_transcript_whisper(file)
    return {"transcript": transcript}
