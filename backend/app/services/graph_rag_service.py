import os
import asyncio
from typing import Dict, List, Any, Optional
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from app.services.factory import get_graph_service
from app.services.cognee_engine import search_graph as cognee_search
from app.utils.gemini_client import get_llm
from app.config import get_settings

settings = get_settings()

class GraphRAGService:
    def __init__(self):
        self.settings = settings
        self.web_search = DuckDuckGoSearchRun()
        self.service = get_graph_service()
        
        # Initialize LLMs using the rate-limited fallback client
        self.synthesizer_llm = get_llm(temperature=0)
        
        # Initialize Graph Executor
        self.graph_rag_executor = RunnableLambda(self.hybrid_rag_runner)
        
        # Session storage
        self._store = {}
        
        # Final Agent with History
        self.agent_with_history = RunnableWithMessageHistory(
            self.graph_rag_executor,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    async def hybrid_rag_runner(self, input_dict: Dict) -> Dict:
        question = input_dict.get("input", "").strip()

        if not question:
            return {"output": "Please enter a question."}

        graph_content = ""
        try:
            # Use cognee search from engine
            try:
                graph_content = await cognee_search(question)
            except Exception as e:
                graph_content = f"Cognee search error: {str(e)}"
        except Exception as e:
            graph_content = f"Database error: {str(e)}"

        web_content = ""
        try:
            web_content = await asyncio.to_thread(self.web_search.invoke, question)
        except Exception as e:
            web_content = "Web search currently unavailable."

        prompt = f"""
        You are an expert scientific assistant.
        User question: "{question}"

        Information sources:
        
        [SOURCE 1: INTERNAL KNOWLEDGE GRAPH]
        {graph_content}
        
        [SOURCE 2: WEB SEARCH]
        {web_content}

        INSTRUCTIONS:
        1. Prioritize SOURCE 1. If it contains the answer, use it as the primary base.
        2. Use SOURCE 2 to enrich the answer or if SOURCE 1 is empty.
        3. Clearly specify if information comes from the internal database or the web.
        4. Be concise and professional.
        5. Answer in English (unless the user asked in another language).

        Final Answer:
        """
        
        try:
            final_response = await self.synthesizer_llm.ainvoke(prompt)
            return {"output": final_response.content}
        except Exception as e:
            return {"output": f"Error synthesizing response: {str(e)}"}

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self._store:
            self._store[session_id] = ChatMessageHistory()
        return self._store[session_id]

    async def query(self, question: str, session_id: str = "default") -> str:
        response = await self.agent_with_history.ainvoke(
            {"input": question},
            config={"configurable": {"session_id": session_id}}
        )
        return response.get("output", "I couldn't generate an answer.")

# Singleton
_graph_rag_service = None

def get_graph_rag_service() -> GraphRAGService:
    global _graph_rag_service
    if _graph_rag_service is None:
        _graph_rag_service = GraphRAGService()
    return _graph_rag_service
