from typing import Dict, Any, List
from app.services.openai_service import get_openai_service
from app.services.pinecone_service import get_pinecone_service
from app.services.logging_service import logging_service
import logging

logger = logging.getLogger(__name__)


class TNEANode:
    """
    TNEA Node - Handles Tamil Nadu Engineering Admissions queries.
    Uses RAG with Pinecone and GPT-4.0 for responses.
    """
    
    def __init__(self):
        self.name = "TNEANode"
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process TNEA-related queries using RAG.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with response
        """
        try:
            query = state.get("query", "")
            user_id = state.get("user_id", "anonymous")
            session_id = state.get("session_id", "")
            
            # Generate query embedding for RAG
            query_embedding = await self._get_query_embedding(query)
            
            # Retrieve relevant context from Pinecone
            pinecone_service = get_pinecone_service()
            context = await pinecone_service.get_context_for_query(query_embedding)
            
            # Log RAG retrieval
            logging_service.log_rag_retrieval(
                user_id, 
                query, 
                len(context.split('\n\n')) if context else 0,
                len(context) if context else 0,
                session_id
            )
            
            # Generate response using GPT-4.0 with RAG context
            system_prompt = """You are a TNEA (Tamil Nadu Engineering Admissions) expert. Use 2024 as default cutoff year.Show results as crisp, categorized bullet points only.
If data is missing, state the limitation.
            """
            
            openai_service = get_openai_service()
            response = await openai_service.generate_response(
                query=query,
                context=context,
                system_prompt=system_prompt
            )
            
            # Log GPT response
            logging_service.log_gpt_response(user_id, query, response, self.name, session_id)
            
            # Update state
            state.update({
                "response": response,
                "context_used": context,
                "processing_node": self.name,
                "rag_enabled": True,
                "current_node": self.name
            })
            
            logger.info(f"TNEA Node processed query successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in TNEANode: {str(e)}")
            logging_service.log_error(
                state.get("user_id", "anonymous"), 
                state.get("query", ""), 
                str(e), 
                "TNEANode processing",
                state.get("session_id")
            )
            
            # Fallback response
            fallback_response = """I apologize"""
            
            state.update({
                "response": fallback_response,
                "processing_node": self.name,
                "error": str(e),
                "current_node": self.name
            })
            return state
    
    async def _get_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for the query using OpenAI.
        """
        try:
            openai_service = get_openai_service()
            embedding = await openai_service.get_embedding(query)
            
            if embedding:
                logger.info(f"Generated real OpenAI embedding of length: {len(embedding)}")
                return embedding
            else:
                logger.warning("Failed to get OpenAI embedding, using dummy embedding")
                return [0.01] * 1536  # Fallback dummy embedding
                
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            logger.warning("Using dummy embedding as fallback")
            return [0.01] * 1536  # Fallback dummy embedding


# Global TNEA node instance
tnea_node = TNEANode()
