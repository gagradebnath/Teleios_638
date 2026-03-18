"""
Orchestrator — Multi-agent workflow orchestration.
Routes requests to appropriate agents, manages tool access, validates outputs.
Loads timeout and configuration from agents.json for each agent type.
"""
from __future__ import annotations
from typing import Any
import asyncio

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

    def __init__(self, 
                 tools_registry: dict[str, Any] | None = None, 
                 adapter=None,
                 config: dict | None = None):
        """
        Initialize the orchestrator.

        Args:
            tools_registry — dict of {tool_name: ToolInstance}
            adapter — ModelAdapter instance
            config — agents.json config dictionary
        """
        self.tools_registry = tools_registry or {}
        self.adapter = adapter
        self.config = config or {}

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

    def _get_agent_config(self, agent_name: str) -> dict:
        """Get configuration for a specific agent from agents.json."""
        if not self.config:
            return {}
        return self.config.get(agent_name, {})

    def _get_timeout(self, agent_name: str) -> int:
        """Get timeout for agent, fallback to orchestrator default."""
        agent_cfg = self._get_agent_config(agent_name)
        agent_timeout = agent_cfg.get("timeout_seconds")
        if agent_timeout:
            return agent_timeout
        
        # Fallback to orchestrator default
        orch_cfg = self.config.get("orchestrator", {})
        return orch_cfg.get("default_timeout_seconds", 60)

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
                "question": "prediction",  # Alias for predict
            }

            agent_name = intent_to_agent.get(intent)
            if not agent_name:
                return {"status": "error", "error": f"Unknown intent '{intent}'"}

            agent = self.agents.get(agent_name)
            if not agent:
                return {"status": "error", "error": f"Agent '{agent_name}' not found"}

            logger.info("orchestrator.dispatch", intent=intent, agent=agent_name)
            
            # Get timeout for this agent
            timeout = self._get_timeout(agent_name)
            
            try:
                # Run agent with timeout
                result = await asyncio.wait_for(
                    agent.run(**payload),
                    timeout=timeout
                )
                return result
            except asyncio.TimeoutError:
                logger.error("orchestrator.timeout", agent=agent_name, timeout=timeout)
                return {
                    "status": "error",
                    "error": f"Agent '{agent_name}' exceeded timeout of {timeout}s"
                }

        except Exception as exc:
            logger.error("orchestrator.error", error=str(exc))
            return {"status": "error", "error": str(exc)}
