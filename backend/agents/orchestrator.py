"""
Orchestrator — Multi-agent workflow orchestration.
Routes requests to appropriate agents, manages tool access, validates outputs.
"""
from __future__ import annotations
from typing import Any

import structlog
from agents.base_agent import BaseAgent
from agents.document_agent import DocumentAgent
from agents.retrieval_agent import RetrievalAgent
from agents.qa_agent import QAAgent
from agents.explanation_agent import ExplanationAgent
from agents.execution_agent import ExecutionAgent
from agents.prediction_agent import PredictionAgent

logger = structlog.get_logger()


class Orchestrator:
    """Orchestrates multi-agent workflows."""

    def __init__(self, tools_registry: dict[str, Any] | None = None, adapter=None):
        """
        Initialize the orchestrator.

        Args:
            tools_registry — dict of {tool_name: ToolInstance}
            adapter — ModelAdapter instance
        """
        self.tools_registry = tools_registry or {}
        self.adapter = adapter

        # Instantiate all agents
        self.agents: dict[str, BaseAgent] = {
            "document": DocumentAgent(tools_registry),
            "retrieval": RetrievalAgent(tools_registry),
            "qa": QAAgent(tools_registry),
            "explanation": ExplanationAgent(tools_registry),
            "execution": ExecutionAgent(tools_registry),
            "prediction": PredictionAgent(tools_registry),
        }

        # Inject adapter into all agents that need it
        if adapter:
            for agent in self.agents.values():
                agent.set_adapter(adapter)

    def set_adapter(self, adapter) -> None:
        """Inject or update ModelAdapter across all agents."""
        self.adapter = adapter
        for agent in self.agents.values():
            agent.set_adapter(adapter)

    def set_tools(self, tools_registry: dict[str, Any]) -> None:
        """Update tools registry for all agents."""
        self.tools_registry = tools_registry
        for agent in self.agents.values():
            agent.set_tools(tools_registry)

    async def run(
        self,
        intent: str,
        **payload,
    ) -> dict[str, Any]:
        """
        Route request to appropriate agent.

        Args:
            intent — 'ingest' | 'search' | 'ask' | 'explain' | 'execute' | 'predict'
            **payload — intent-specific parameters

        Returns:
            Structured result dict from agent
        """
        try:
            intent_to_agent = {
                "ingest": "document",
                "search": "retrieval",
                "ask": "qa",
                "explain": "explanation",
                "execute": "execution",
                "predict": "prediction",
            }

            agent_name = intent_to_agent.get(intent)
            if not agent_name:
                return {"status": "error", "error": f"Unknown intent '{intent}'"}

            agent = self.agents.get(agent_name)
            if not agent:
                return {"status": "error", "error": f"Agent '{agent_name}' not found"}

            logger.info("orchestrator.dispatch", intent=intent, agent=agent_name)
            result = await agent.run(**payload)
            return result

        except Exception as exc:
            logger.error("orchestrator.error", error=str(exc))
            return {"status": "error", "error": str(exc)}
