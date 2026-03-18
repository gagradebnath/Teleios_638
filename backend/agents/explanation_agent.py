"""
ExplanationAgent — Clarify topics, provide tutorials, and explain concepts.
Uses LLM + retrieval to generate explanations.
"""
from __future__ import annotations
from typing import Any

import structlog
from agents.base_agent import BaseAgent

logger = structlog.get_logger()


class ExplanationAgent(BaseAgent):
    """Provides detailed explanations of topics."""

    def __init__(self, tools_registry: dict[str, Any] | None = None):
        super().__init__("explanation_agent", tools_registry)

    async def run(
        self,
        topic: str,
        depth: str = "medium",
        doc_ids: list[str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate an explanation for a topic.

        Args:
            topic — concept or topic to explain
            depth — 'basic' | 'medium' | 'advanced'
            doc_ids — optional document IDs to reference

        Returns:
            {"status": "ok", "explanation": "...", "references": [...]}
            or {"status": "error", ...}
        """
        try:
            if self.adapter is None:
                return {"status": "error", "error": "ExplanationAgent: adapter not set"}

            # Retrieve relevant context
            vector_search_tool = await self.get_tool("vector_search")
            search_result = await vector_search_tool.execute(
                query=topic,
                top_k=8,
                doc_id=doc_ids[0] if doc_ids else None,
            )

            results = search_result.get("results", [])
            context = "\n\n".join(
                [f"Source: {r.get('title', 'Unknown')}\n{r.get('text', '')[:200]}" for r in results[:5]]
            )

            # Generate explanation
            depth_prompt = {
                "basic": "Explain this topic in simple terms, suitable for beginners.",
                "medium": "Provide a balanced explanation with moderate detail.",
                "advanced": "Provide a comprehensive, technical explanation.",
            }.get(depth, "Provide a balanced explanation.")

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert tutor explaining complex topics clearly and accurately.",
                },
                {
                    "role": "user",
                    "content": f"{depth_prompt}\n\nTopic: {topic}\n\nRelevant material:\n{context}",
                },
            ]

            explanation = await self.adapter.chat(messages)
            references = [{"source": r.get("title"), "relevance": r.get("score", 0)} for r in results[:5]]

            logger.info("explanation_agent.generated", topic_len=len(topic), depth=depth)
            return {"status": "ok", "explanation": explanation, "references": references}

        except Exception as exc:
            logger.error("explanation_agent.error", error=str(exc))
            return {"status": "error", "error": str(exc), "explanation": "", "references": []}
