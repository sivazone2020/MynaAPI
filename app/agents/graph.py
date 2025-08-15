from typing import Dict, Any, Callable
from langgraph.graph import StateGraph, END
from app.agents.nodes.router_node import router_node
from app.agents.nodes.tnea_node import tnea_node
from app.agents.nodes.future_node import future_node
from app.services.logging_service import logging_service
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class MynaAgentGraph:
    """
    Main agent graph implementation using LangGraph.
    Orchestrates the flow between different nodes.
    """
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        
        # Define the graph with Dict as state type
        workflow = StateGraph(Dict[str, Any])
        
        # Add nodes
        workflow.add_node("router", self._router_wrapper)
        workflow.add_node("tnea", self._tnea_wrapper)
        workflow.add_node("future", self._future_wrapper)
        
        # Add conditional edges from router
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "tnea": "tnea",
                "future": "future"
            }
        )
        workflow.add_edge("tnea", END)
        workflow.add_edge("future", END)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        return workflow.compile()
    
    async def _router_wrapper(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper for router node."""
        try:
            logger.info(f"Router wrapper called with state keys: {list(state.keys())}")
            result = await router_node.process(state)
            logger.info(f"Router wrapper returning keys: {list(result.keys())}")
            return result
        except Exception as e:
            logger.error(f"Error in router wrapper: {str(e)}")
            raise
    
    async def _tnea_wrapper(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper for TNEA node."""
        try:
            logger.info(f"TNEA wrapper called with state keys: {list(state.keys())}")
            result = await tnea_node.process(state)
            logger.info(f"TNEA wrapper returning keys: {list(result.keys())}")
            return result
        except Exception as e:
            logger.error(f"Error in TNEA wrapper: {str(e)}")
            raise

    async def _future_wrapper(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper for future node."""
        try:
            logger.info(f"Future wrapper called with state keys: {list(state.keys())}")
            result = await future_node.process(state)
            logger.info(f"Future wrapper returning keys: {list(result.keys())}")
            return result
        except Exception as e:
            logger.error(f"Error in future wrapper: {str(e)}")
            raise

    def _route_decision(self, state: Dict[str, Any]) -> str:
        """Decision function for routing after router node."""
        try:
            next_node = state.get("next_node", "future")
            logger.info(f"Routing decision: next_node={next_node}, available keys: {list(state.keys())}")
            
            if next_node == "TNEANode":
                return "tnea"
            else:
                return "future"
        except Exception as e:
            logger.error(f"Error in routing decision: {str(e)}")
            logger.error(f"State keys: {list(state.keys()) if state else 'None'}")
            return "future"
    
    async def process_query(self, query: str, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user query through the agent graph.
        
        Args:
            query: User's question
            user_id: User identifier
            context: Additional context
            
        Returns:
            Processing result with response
        """
        session_id = str(uuid.uuid4())
        
        try:
            # Log session start
            logging_service.log_session_start(user_id, session_id)
            start_time = datetime.utcnow()
            
            # Initialize state
            initial_state = {
                "query": query,
                "user_id": user_id,
                "session_id": session_id,
                "context": context or {},
                "timestamp": start_time.isoformat()
            }
            
            # Run the graph
            result = await self.graph.ainvoke(initial_state)
            
            # Calculate duration and log session end
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            logging_service.log_session_end(user_id, session_id, duration)
            
            # Return formatted result
            return {
                "response": result.get("response", "I'm sorry, I couldn't process your request."),
                "session_id": session_id,
                "processing_node": result.get("processing_node", "unknown"),
                "intent": result.get("intent"),
                "confidence": result.get("confidence"),
                "timestamp": end_time,
                "success": True,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            logging_service.log_error(user_id, query, str(e), "Graph execution", session_id)
            
            return {
                "response": "I'm sorry, but I encountered an error while processing your request. Please try again.",
                "session_id": session_id,
                "processing_node": "error",
                "intent": None,
                "confidence": 0.0,
                "timestamp": datetime.utcnow(),
                "success": False,
                "error": str(e)
            }


# Global graph instance
myna_agent = MynaAgentGraph()
