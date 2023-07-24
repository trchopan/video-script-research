from typing import Optional
from langchain import OpenAI, LLMMathChain

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.chat_models import ChatOpenAI
from langchain.tools.base import BaseTool
from pydantic import Field


class MathTool(BaseTool):
    """Tool that can solve math problems from natural language question."""

    name = "MathTool"
    description = (
        "A tool for solving math questions. "
        "Useful for when you need to make calculations."
    )
    chat: ChatOpenAI = Field(exclude=True)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the MathTool tool."""
        llm_math = LLMMathChain.from_llm(self.chat)
        return llm_math.run(query)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Wikipedia tool asynchronously."""
        raise NotImplementedError("WikipediaQueryRun does not support async")
