"""
PredictionAgent — Score exam questions by difficulty/relevance.
Combines topic frequency, recency, and similarity scoring.
"""
from __future__ import annotations
from typing import Any

import structlog
from agents.base_agent import BaseAgent

logger = structlog.get_logger()


class PredictionAgent(BaseAgent):
    """Scores and predicts question difficulty/relevance."""

    def __init__(self, tools_registry: dict[str, Any] | None = None):
        super().__init__("prediction_agent", tools_registry)

    async def run(
        self,
        doc_ids: list[str],
        weights: dict[str, float] | None = None,
        top_n: int = 20,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Score questions from documents.

        Args:
            doc_ids — list of document IDs to score questions from
            weights — scoring weights {frequency, recency, similarity, importance}
            top_n — return top N questions

        Returns:
            {"status": "ok", "questions": [...], "weights": {...}, "total_scored": N}
            or {"status": "error", ...}
        """
        try:
            # Default weights
            if weights is None:
                weights = {
                    "frequency": 0.25,
                    "recency": 0.25,
                    "similarity": 0.25,
                    "importance": 0.25,
                }

            sql_query_tool = await self.get_tool("sql_query")
            stats_analysis_tool = await self.get_tool("stats_analysis")

            # Fetch all questions
            placeholders = ", ".join("?" * len(doc_ids))
            query = f"SELECT id, doc_id, text, topic, year FROM questions WHERE doc_id IN ({placeholders})"
            questions_result = await sql_query_tool.execute(query=query, params=doc_ids)
            questions = questions_result.get("rows", [])

            if not questions:
                return {"status": "ok", "questions": [], "weights": weights, "total_scored": 0}

            # Compute scores
            scored_questions = []
            for q in questions:
                topic_data = [{"topic": q.get("topic", "unknown")}]
                year_data = [{"year": q.get("year", 2024)}]

                freq_result = await stats_analysis_tool.execute(operation="frequency", data=topic_data)
                recency_result = await stats_analysis_tool.execute(operation="recency", data=year_data)

                frequency_score = list(freq_result.get("frequency", {}).values())[0] if freq_result.get("frequency") else 0
                recency_scores = recency_result.get("recency", {})
                recency_score = list(recency_scores.values())[0] if recency_scores else 0.5

                # Normalize and combine scores
                final_score = (
                    weights.get("frequency", 0.25) * min(frequency_score / 10, 1.0)
                    + weights.get("recency", 0.25) * recency_score
                    + weights.get("similarity", 0.25) * 0.5  # placeholder
                    + weights.get("importance", 0.25) * 0.5
                ) / 4.0

                scored_questions.append({
                    "id": q.get("id"),
                    "text": q.get("text"),
                    "topic": q.get("topic"),
                    "year": q.get("year"),
                    "score": round(final_score, 4),
                })

            # Sort and return top N
            scored_questions.sort(key=lambda x: x["score"], reverse=True)
            top_questions = scored_questions[:top_n]

            logger.info("prediction_agent.scored", total=len(questions), top_n=len(top_questions))
            return {
                "status": "ok",
                "questions": top_questions,
                "weights": weights,
                "total_scored": len(questions),
            }

        except Exception as exc:
            logger.error("prediction_agent.error", error=str(exc))
            return {"status": "error", "error": str(exc), "questions": [], "weights": weights, "total_scored": 0}
