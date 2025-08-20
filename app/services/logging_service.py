import logging
import json
from datetime import datetime
from typing import Dict, Any, List
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

    def log_openai_request(self, user_id: str, operation: str, system_prompt: str, user_prompt: str, 
                          model: str = None, session_id: str = None, request_id: str = None):
        """Log OpenAI API request details including full prompts."""
        log_data = {
            "event": "openai_request",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "operation": operation,  # "intent_analysis", "response_generation", "embedding"
            "model": model,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "system_prompt_length": len(system_prompt) if system_prompt else 0,
            "user_prompt_length": len(user_prompt) if user_prompt else 0
        }
        self.interaction_logger.info(json.dumps(log_data, indent=2))

    def log_openai_response(self, user_id: str, operation: str, response: str, 
                           model: str = None, session_id: str = None, request_id: str = None,
                           tokens_used: int = None, response_time_ms: float = None):
        """Log OpenAI API response details."""
        log_data = {
            "event": "openai_response",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "operation": operation,
            "model": model,
            "response": response,
            "response_length": len(response) if response else 0,
            "tokens_used": tokens_used,
            "response_time_ms": response_time_ms
        }
        self.interaction_logger.info(json.dumps(log_data, indent=2))

    def log_openai_embedding_request(self, user_id: str, text: str, model: str = "text-embedding-3-large",
                                   session_id: str = None, request_id: str = None):
        """Log OpenAI embedding request."""
        log_data = {
            "event": "openai_embedding_request",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "model": model,
            "input_text": text,
            "input_text_length": len(text) if text else 0
        }
        self.interaction_logger.info(json.dumps(log_data, indent=2))

    def log_openai_embedding_response(self, user_id: str, embedding_dimension: int, 
                                    model: str = "text-embedding-3-large", session_id: str = None, 
                                    request_id: str = None, response_time_ms: float = None):
        """Log OpenAI embedding response."""
        log_data = {
            "event": "openai_embedding_response",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "model": model,
            "embedding_dimension": embedding_dimension,
            "response_time_ms": response_time_ms
        }
        self.interaction_logger.info(json.dumps(log_data, indent=2))

    def log_pinecone_query_request(self, user_id: str, query_vector_dimension: int, top_k: int,
                                  filter_dict: Dict = None, session_id: str = None, request_id: str = None):
        """Log Pinecone query request details."""
        log_data = {
            "event": "pinecone_query_request",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "query_vector_dimension": query_vector_dimension,
            "top_k": top_k,
            "filter": filter_dict,
            "has_filter": filter_dict is not None
        }
        self.interaction_logger.info(json.dumps(log_data, indent=2))

    def log_pinecone_query_response(self, user_id: str, results_count: int, results_data: List[Dict[str, Any]],
                                   session_id: str = None, request_id: str = None, response_time_ms: float = None):
        """Log Pinecone query response details including retrieved documents."""
        # Create a detailed log of results without exposing vectors
        formatted_results = []
        for i, result in enumerate(results_data):
            formatted_result = {
                "result_index": i,
                "document_id": result.get("id", "unknown"),
                "similarity_score": result.get("score", 0),
                "metadata": result.get("metadata", {})
            }
            formatted_results.append(formatted_result)

        log_data = {
            "event": "pinecone_query_response",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "results_count": results_count,
            "results": formatted_results,
            "response_time_ms": response_time_ms
        }
        self.interaction_logger.info(json.dumps(log_data, indent=2))

    def log_pinecone_context_generation(self, user_id: str, query_results_count: int, 
                                       generated_context: str, max_context_length: int,
                                       session_id: str = None, request_id: str = None):
        """Log Pinecone context generation for RAG."""
        log_data = {
            "event": "pinecone_context_generation",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "input_results_count": query_results_count,
            "max_context_length": max_context_length,
            "generated_context": generated_context,
            "generated_context_length": len(generated_context) if generated_context else 0,
            "context_truncated": len(generated_context) >= max_context_length if generated_context else False
        }
        self.interaction_logger.info(json.dumps(log_data, indent=2))

    def log_rag_pipeline_flow(self, user_id: str, original_query: str, embedding_dimension: int,
                             pinecone_results_count: int, context_length: int, final_response: str,
                             session_id: str = None, request_id: str = None):
        """Log complete RAG pipeline flow summary."""
        log_data = {
            "event": "rag_pipeline_flow",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "original_query": original_query,
            "pipeline_steps": {
                "1_embedding_dimension": embedding_dimension,
                "2_pinecone_results_found": pinecone_results_count,
                "3_context_generated_length": context_length,
                "4_final_response_length": len(final_response) if final_response else 0
            },
            "final_response": final_response
        }
        self.interaction_logger.info(json.dumps(log_data, indent=2))


# Global service instance
logging_service = LoggingService()
