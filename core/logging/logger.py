"""
Structured logging for observability and tracing.
Layer 7 - Observability Layer
"""
from loguru import logger
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

logger.remove()

# Console logging with structured format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="INFO",
    serialize=False
)

# File logging with JSON format for parsing/analysis
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="10 days",
    level="DEBUG",
    serialize=True,  # JSON format for structured logging
    enqueue=True
)

# Separate file for errors
logger.add(
    "logs/error.log",
    rotation="10 MB",
    retention="30 days",
    level="ERROR",
    serialize=True
)


class ObservabilityLogger:
    """Structured logger for tracing LLM calls, tool calls, and scenario execution."""
    
    @staticmethod
    def log_llm_call(
        session_id: str,
        model: str,
        prompt: str,
        response: str,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[float] = None
    ):
        """Log LLM call for tracing and evaluation."""
        logger.bind(
            event_type="llm_call",
            session_id=session_id,
            model=model,
            prompt_length=len(prompt),
            response_length=len(response),
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow().isoformat()
        ).info("LLM call executed")
    
    @staticmethod
    def log_tool_call(
        session_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any],
        latency_ms: Optional[float] = None,
        cache_hit: bool = False
    ):
        """Log tool call for tracing and debugging."""
        logger.bind(
            event_type="tool_call",
            session_id=session_id,
            tool_name=tool_name,
            cache_hit=cache_hit,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow().isoformat()
        ).debug(f"Tool {tool_name} called with args: {arguments}")
    
    @staticmethod
    def log_scenario_start(
        session_id: str,
        query: str,
        perturbations: list
    ):
        """Log scenario simulation start."""
        logger.bind(
            event_type="scenario_start",
            session_id=session_id,
            query=query,
            perturbation_count=len(perturbations),
            timestamp=datetime.utcnow().isoformat()
        ).info(f"Scenario simulation started: {query}")
    
    @staticmethod
    def log_scenario_complete(
        session_id: str,
        processing_time_ms: float,
        tool_calls_count: int,
        recommendations_count: int
    ):
        """Log scenario simulation completion."""
        logger.bind(
            event_type="scenario_complete",
            session_id=session_id,
            processing_time_ms=processing_time_ms,
            tool_calls_count=tool_calls_count,
            recommendations_count=recommendations_count,
            timestamp=datetime.utcnow().isoformat()
        ).info("Scenario simulation completed")
    
    @staticmethod
    def log_error(
        session_id: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log error with context for debugging."""
        logger.bind(
            event_type="error",
            session_id=session_id,
            error_type=error_type,
            context=context or {},
            timestamp=datetime.utcnow().isoformat()
        ).error(f"Error: {error_message}")
    
    @staticmethod
    @contextmanager
    def trace_operation(operation_name: str, session_id: str, **context):
        """Context manager for tracing operations with timing."""
        start_time = datetime.utcnow()
        logger.bind(
            event_type="operation_start",
            operation=operation_name,
            session_id=session_id,
            context=context,
            timestamp=start_time.isoformat()
        ).debug(f"Starting operation: {operation_name}")
        
        try:
            yield
        finally:
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            logger.bind(
                event_type="operation_complete",
                operation=operation_name,
                session_id=session_id,
                duration_ms=duration_ms,
                timestamp=end_time.isoformat()
            ).debug(f"Completed operation: {operation_name} in {duration_ms:.2f}ms")


# Global observability logger instance
obs_logger = ObservabilityLogger()
