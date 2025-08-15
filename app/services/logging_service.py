import logging
import json
from datetime import datetime
from typing import Dict, Any
from app.config.settings import settings
import os


class LoggingService:
    def __init__(self):
        self.interaction_logger = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Configure main logger
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/app.log'),
                logging.StreamHandler()
            ]
        )
        
        # Configure interaction logger for detailed tracking
        self.interaction_logger = logging.getLogger("interactions")
        interaction_handler = logging.FileHandler('logs/interactions.log')
        interaction_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        interaction_handler.setFormatter(interaction_formatter)
        
        self.interaction_logger.addHandler(interaction_handler)
        self.interaction_logger.setLevel(logging.INFO)
    
    def log_user_query(self, user_id: str, query: str, session_id: str = None):
        """Log user query."""
        log_data = {
            "event": "user_query",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "query": query
        }
        self.interaction_logger.info(json.dumps(log_data))
    
    def log_intent_analysis(self, user_id: str, query: str, intent_result: Dict[str, Any], session_id: str = None):
        """Log intent analysis result."""
        log_data = {
            "event": "intent_analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "intent": intent_result.get("intent"),
            "confidence": intent_result.get("confidence"),
            "reasoning": intent_result.get("reasoning")
        }
        self.interaction_logger.info(json.dumps(log_data))
    
    def log_node_routing(self, user_id: str, query: str, target_node: str, session_id: str = None):
        """Log node routing decision."""
        log_data = {
            "event": "node_routing",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "target_node": target_node
        }
        self.interaction_logger.info(json.dumps(log_data))
    
    def log_rag_retrieval(self, user_id: str, query: str, retrieved_docs: int, context_length: int, session_id: str = None):
        """Log RAG retrieval information."""
        log_data = {
            "event": "rag_retrieval",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "retrieved_documents": retrieved_docs,
            "context_length": context_length
        }
        self.interaction_logger.info(json.dumps(log_data))
    
    def log_gpt_response(self, user_id: str, query: str, response: str, node: str, session_id: str = None):
        """Log GPT response."""
        log_data = {
            "event": "gpt_response",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "response": response[:500] + "..." if len(response) > 500 else response,  # Truncate long responses
            "response_length": len(response),
            "processing_node": node
        }
        self.interaction_logger.info(json.dumps(log_data))
    
    def log_error(self, user_id: str, query: str, error: str, context: str = "", session_id: str = None):
        """Log error events."""
        log_data = {
            "event": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "error": error,
            "context": context
        }
        self.interaction_logger.error(json.dumps(log_data))
    
    def log_session_start(self, user_id: str, session_id: str):
        """Log session start."""
        log_data = {
            "event": "session_start",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id
        }
        self.interaction_logger.info(json.dumps(log_data))
    
    def log_session_end(self, user_id: str, session_id: str, duration: float = None):
        """Log session end."""
        log_data = {
            "event": "session_end",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "duration_seconds": duration
        }
        self.interaction_logger.info(json.dumps(log_data))


# Global service instance
logging_service = LoggingService()
