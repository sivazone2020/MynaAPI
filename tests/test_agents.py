import unittest
from app.agents.nodes.router_node import router_node
from app.agents.nodes.future_node import future_node
import asyncio


class TestAgents(unittest.TestCase):
    """Test agent nodes."""
    
    def test_router_node_tnea_intent(self):
        """Test router node with TNEA-related query."""
        async def run_test():
            state = {
                "query": "What is the cutoff for Anna University engineering admissions?",
                "user_id": "test_user"
            }
            result = await router_node.process(state)
            return result
        
        result = asyncio.run(run_test())
        self.assertIn("intent", result)
        self.assertIn("next_node", result)
    
    def test_future_node_response(self):
        """Test future node response generation."""
        async def run_test():
            state = {
                "query": "Tell me about medical college admissions",
                "user_id": "test_user",
                "intent": "MEDICAL"
            }
            result = await future_node.process(state)
            return result
        
        result = asyncio.run(run_test())
        self.assertIn("response", result)
        self.assertTrue(result["future_implementation"])


if __name__ == '__main__':
    unittest.main()
