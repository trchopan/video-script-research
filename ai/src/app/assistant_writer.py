from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage
from app.helpers import send_chat_prompt_with_print


class AssistantWriterService:
    def __init__(self, chat: ChatOpenAI):
        self.chat = chat

    def extend_content_with_context(self, content: str, context: list[str]):
        context_str = "\n---\n".join(context)
        messages = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    "You are a content writer assistant who helps continue writing "
                    "CONTENT below. Use the CONTEXT for more information to extend "
                    "the CONTENT.\n\n"
                    "CONTEXT:\n{context}\n\n"
                ),
                HumanMessagePromptTemplate.from_template("CONTENT:\n{content}"),
            ]
        )
        prompt = messages.format_prompt(context=context_str, content=content)
        result = send_chat_prompt_with_print(self.chat, prompt)
        return result.content

    def translate(self, text: str, language: str):
        messages = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    "You are a translator. Given a TEXT in English, help translate it "
                    "to {language}.\n"
                ),
                HumanMessagePromptTemplate.from_template("TEXT:\n{text}\n\nOUTPUT:"),
            ]
        )
        prompt = messages.format_prompt(text=text, language=language)
        result = send_chat_prompt_with_print(self.chat, prompt)
        return result.content

    def extract_information(self, documents: str):
        messages = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    "You are a content assistant who helps the user extract "
                    "the information from the DOCUMENTS given below. "
                    "Write the extracted information as a bullet point list into "
                    "the SCRATCH PAD. Only extract the information and "
                    "do not hallucinate.\n\n"
                    "DOCUMENTS:\n{documents}\n\n"
                ),
                HumanMessagePromptTemplate.from_template("SCRATCH PAD:"),
            ]
        )

        prompt = messages.format_prompt(documents=documents)
        result = send_chat_prompt_with_print(self.chat, prompt)
        return result.content

    def format_text(self, text: str):
        messages = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    "Improve the format output of the below TEXT.\n\nTEXT:\n{text}\n\n"
                ),
                HumanMessagePromptTemplate.from_template("FORMATED:"),
            ]
        )

        prompt = messages.format_prompt(text=text)
        result = send_chat_prompt_with_print(self.chat, prompt)
        return result.content

    def get_chat(self, chat: str):
        result = send_chat_prompt_with_print(
            self.chat,
            ChatPromptTemplate.from_messages([HumanMessage(content=chat)]).format_prompt(),
        )
        assert isinstance(result.content, str)
        return result.content
