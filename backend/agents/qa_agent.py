"""
QAAgent — Generate answers to questions using retrieval context.
Combines vector search with LLM generation.
"""
from __future__ import annotations
from typing import Any

import structlog
from agents.base_agent import BaseAgent

logger = structlog.get_logger()


class QAAgent(BaseAgent):
    """Generates answers to user questions."""

    def __init__(self, tools_registry: dict[str, Any] | None = None):
        super().__init__("qa_agent", tools_registry)

    async def run(
        self,
        question: str,
        doc_ids: list[str] | None = None,
        top_k: int = 6,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Answer a question using retrieval context.

        Args:
            question — user question
            doc_ids — optional list of document IDs to search
            top_k — results to retrieve

        Returns:
            {"status": "ok", "answer": "...", "citations": [...]}
            or {"status": "error", ...}
        """
        try:
            if self.adapter is None:
                return {"status": "error", "error": "QAAgent: adapter not set"}

            # Retrieve context
            vector_search_tool = await self.get_tool("vector_search")
            search_result = await vector_search_tool.execute(
                query=question,
                top_k=top_k,
                doc_id=doc_ids[0] if doc_ids else None,
            )

            results = search_result.get("results", [])
            if not results:
                return {"status": "ok", "answer": "No relevant context found.", "citations": []}

            # Build context
            context = "\n\n".join(
                [f"Block {i+1}: {r.get('text', '')}" for i, r in enumerate(results[:3])]
            )

            # Generate answer
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful tutor. Answer questions accurately and cite sources.",
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                },
            ]

            answer = await self.adapter.chat(messages)
            citations = [{"source": r.get("title"), "text": r.get("text", "")[:100]} for r in results[:3]]

            logger.info("qa_agent.answered", question_len=len(question))
            return {"status": "ok", "answer": answer, "citations": citations}

        except Exception as exc:
            logger.error("qa_agent.error", error=str(exc))
            return {"status": "error", "error": str(exc), "answer": "", "citations": []}
