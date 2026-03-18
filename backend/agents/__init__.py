"""
Agent module — orchestration, document processing, retrieval, QA, and prediction.

Agents:
  - BaseAgent: abstract base class for all agents
  - DocumentAgent: ingests PDFs, extracts blocks & questions
  - RetrievalAgent: semantic search in vector store
  - QAAgent: generates answers from retrieval context
  - ExplanationAgent: clarifies topics or exam questions
  - ExecutionAgent: runs sandboxed Python code
  - PredictionAgent: scores exam questions by difficulty
  - Orchestrator: multi-agent workflow orchestration
"""
from agents.base_agent import BaseAgent
from agents.document_agent import DocumentAgent
from agents.retrieval_agent import RetrievalAgent
from agents.qa_agent import QAAgent
from agents.explanation_agent import ExplanationAgent
from agents.execution_agent import ExecutionAgent
from agents.prediction_agent import PredictionAgent
from agents.orchestrator import Orchestrator

__all__ = [
    "BaseAgent",
    "DocumentAgent",
    "RetrievalAgent",
    "QAAgent",
    "ExplanationAgent",
    "ExecutionAgent",
    "PredictionAgent",
    "Orchestrator",
]
