from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from app import assistant_writer_svc

assistant_writer_router = APIRouter()


class AssistantWriterExtendWithContext(BaseModel):
    content: str
    context: List[str]


@assistant_writer_router.post("/assistant_writer_extend_with_context")
def assistant_writer_extend_with_context(body: AssistantWriterExtendWithContext):
    res = assistant_writer_svc.extend_content_with_context(
        content=body.content, context=body.context
    )
    return {"extended_content": res}


class AssistantExtractInformation(BaseModel):
    documents: str


@assistant_writer_router.post("/assistant_extract_information")
def assistant_extract_information(body: AssistantExtractInformation):
    res = assistant_writer_svc.extract_information(documents=body.documents)
    return {"scratch_pad": res}


class AssistantTranslate(BaseModel):
    text: str
    language: str


@assistant_writer_router.post("/assistant_translate")
def assistant_translate(body: AssistantTranslate):
    res = assistant_writer_svc.translate(text=body.text, language=body.language)
    return {"translated": res}


class AssistantFormat(BaseModel):
    text: str


@assistant_writer_router.post("/assistant_format")
def assistant_format(body: AssistantFormat):
    res = assistant_writer_svc.format_text(text=body.text)
    return {"formated": res}


class AssistantChat(BaseModel):
    chat: str


@assistant_writer_router.post("/assistant_chat")
def assistant_chat(body: AssistantChat):
    res = assistant_writer_svc.get_chat(chat=body.chat)
    return {"response": res}
