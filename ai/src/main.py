from flask import Flask, request
import os
from app import (
    youtube_transcript_svc,
    assistant_writer_svc,
    general_knowledge_svc,
)

from app.helpers import (
    request_json_optional,
    request_json_require_validate,
    with_handle_require_validate,
)

app = Flask(__name__)


@app.get("/healthz")
def healthz():
    return "healthy", 200


@app.get("/list_youtube_videos")
def list_youtube_videos():
    return {"videos": [v.to_dict() for v in youtube_transcript_svc.get_videos()]}, 200


@app.post("/youtube_video")
@with_handle_require_validate
def youtube_video():
    [link] = request_json_require_validate(["link"])
    clear_cache = request.args.get("clear_cache", None) is not None
    youtube_video = youtube_transcript_svc.get_video_details(
        link, clear_cache=clear_cache
    )
    return {"youtube_video": youtube_video.to_dict()}, 200


@app.post("/get_youtube_transcript")
@with_handle_require_validate
def get_youtube_transcript():
    [link] = request_json_require_validate(["link"])
    clear_cache = request.args.get("clear_cache", None) is not None
    transcripts = youtube_transcript_svc.get_parsed_transcript(
        link, clear_cache=clear_cache
    )
    return {
        "transcripts": [transcript.to_dict() for transcript in transcripts],
    }, 200


@app.post("/get_youtube_transcript_embedding")
@with_handle_require_validate
def get_youtube_transcript_embedding():
    [link] = request_json_require_validate(["link"])
    embeddings = youtube_transcript_svc.get_embeddings(link)
    return {"embeddings": embeddings}, 200


@app.post("/youtube_transcript_similarity")
@with_handle_require_validate
def youtube_transcript_similarity():
    [links, query] = request_json_require_validate(["links", "query"])
    [k] = request_json_optional(["k"])
    similarity = youtube_transcript_svc.get_similarity(query, links, k=k or 5)
    return {"similarity": [s.to_dict() for s in similarity]}, 200

@app.post("/general_knowledge_wikipedia_search")
@with_handle_require_validate
def general_knowledge_wikipedia_search():
    [search] = request_json_require_validate(["search"])
    return {"search_results": general_knowledge_svc.search_page(search)}, 200

@app.post("/general_knowledge_wikipedia_page")
@with_handle_require_validate
def general_knowledge_wikipedia_page():
    [search] = request_json_require_validate(["search"])
    return {"page": general_knowledge_svc.get_wikipedia_page(search)}, 200


@app.post("/general_knowledge_wikipedia_summary")
@with_handle_require_validate
def general_knowledge_wikipedia_summary():
    [search] = request_json_require_validate(["search"])
    return {"summary": general_knowledge_svc.get_wikipedia_summary(search)}, 200


@app.post("/assistant_writer_extend_with_context")
@with_handle_require_validate
def assistant_writer_extend_with_context():
    [content, context] = request_json_require_validate(["content", "context"])

    res = assistant_writer_svc.extend_content_with_context(
        content=content, context=context
    )
    return {"extended_content": res}, 200


@app.post("/assistant_extract_information")
@with_handle_require_validate
def assistant_extract_information():
    [documents] = request_json_require_validate(["documents"])
    res = assistant_writer_svc.extract_information(documents=documents)
    return {"scratch_pad": res}, 200


@app.post("/assistant_translate")
@with_handle_require_validate
def assistant_translate():
    [text, language] = request_json_require_validate(["text", "language"])
    res = assistant_writer_svc.translate(text=text, language=language)
    return {"translated": res}, 200


@app.post("/assistant_format")
@with_handle_require_validate
def assistant_format():
    [text] = request_json_require_validate(["text"])
    res = assistant_writer_svc.format_text(text=text)
    return {"formated": res}, 200


@app.post("/assistant_chat")
@with_handle_require_validate
def assistant_chat():
    [chat] = request_json_require_validate(["chat"])
    res = assistant_writer_svc.get_chat(chat=chat)
    return {"response": res}, 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
