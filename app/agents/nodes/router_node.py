from typing import Dict, Any, List
from app.services.openai_service import get_openai_service
from app.services.logging_service import logging_service
import uuid
import logging

logger = logging.getLogger(__name__)


class RouterNode:
    """
    Router Node - Entry point for all queries.
    Analyzes intent and routes to appropriate nodes.
    """
    
    def __init__(self):
        self.name = "RouterNode"
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the incoming query and determine routing.
        
        Args:
            state: Current graph state containing query and context
            
        Returns:
            Updated state with routing decision
        """
        try:
            query = state.get("query", "")
            user_id = state.get("user_id", "anonymous")
            session_id = state.get("session_id", str(uuid.uuid4()))
            
            # Log the query
            logging_service.log_user_query(user_id, query, session_id)
            
            # Analyze intent using OpenAI
            openai_service = get_openai_service()
            intent_result = await openai_service.analyze_intent(query, state.get("context", {}))
            
            # Log intent analysis
            logging_service.log_intent_analysis(user_id, query, intent_result, session_id)
            
            # Determine next node based on intent
            intent = intent_result.get("intent", "FUTURE").upper()
            confidence = intent_result.get("confidence", 0.0)
            
            if intent == "TNEA" and confidence > 0.5:
                next_node = "TNEANode"
            else:
                next_node = "FutureNode"
            
            # Log routing decision
            logging_service.log_node_routing(user_id, query, next_node, session_id)
            
            # Update state
            state.update({
                "intent": intent,
                "confidence": confidence,
                "next_node": next_node,
                "session_id": session_id,
                "routing_reasoning": intent_result.get("reasoning", ""),
                "current_node": self.name
            })
            
            logger.info(f"Router processed query, routing to: {next_node}")
            return state
            
        except Exception as e:
            logger.error(f"Error in RouterNode: {str(e)}")
            logging_service.log_error(
                state.get("user_id", "anonymous"), 
                state.get("query", ""), 
                str(e), 
                "RouterNode processing",
                state.get("session_id")
            )
            
            # Default to future node on error
            state.update({
                "intent": "ERROR",
                "confidence": 0.0,
                "next_node": "FutureNode",
                "error": str(e),
                "current_node": self.name
            })
            return state


# Global router node instance
router_node = RouterNode()
