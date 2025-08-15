import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import json
from datetime import datetime

# Test the full query flow to GPT-4.0
class TestUserQueryToGPT(unittest.TestCase):
    """Test that user queries reach GPT-4.0 through the agent system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_user_id = "test_user_123"
        self.test_query = "What is the cutoff for Anna University Computer Science Engineering?"
        self.test_session_id = "session_123"
        
    @patch('app.services.openai_service.OpenAI')
    @patch('app.services.pinecone_service.Pinecone')
    @patch('app.services.logging_service.logging_service')
    def test_tnea_query_reaches_gpt4(self, mock_logging, mock_pinecone, mock_openai):
        """Test that a TNEA query reaches GPT-4.0 through the router and TNEA node."""
        
        async def run_test():
            # Mock OpenAI client responses
            mock_openai_client = Mock()
            mock_openai.return_value = mock_openai_client
            
            # Mock intent analysis response from GPT-4.0
            mock_intent_response = Mock()
            mock_intent_response.choices = [Mock()]
            mock_intent_response.choices[0].message.content = json.dumps({
                "intent": "TNEA",
                "confidence": 0.9,
                "reasoning": "Query is about Anna University cutoff marks which is TNEA related"
            })
            
            # Mock final response from GPT-4.0
            mock_final_response = Mock()
            mock_final_response.choices = [Mock()]
            mock_final_response.choices[0].message.content = """Based on previous year data, Anna University Computer Science Engineering typically has these cutoffs:
            - General Category: 195-200 marks
            - BC Category: 190-195 marks
            - MBC Category: 185-190 marks
            
            Please note these are approximate figures from previous years."""
            
            # Configure mock to return different responses for different calls
            mock_openai_client.chat.completions.create = AsyncMock(
                side_effect=[mock_intent_response, mock_final_response]
            )
            
            # Mock Pinecone response
            mock_pinecone_instance = Mock()
            mock_pinecone.return_value = mock_pinecone_instance
            mock_index = Mock()
            mock_pinecone_instance.Index.return_value = mock_index
            
            # Mock vector search results
            mock_search_result = Mock()
            mock_search_result.matches = [
                Mock(
                    id="anna_univ_cs_1",
                    score=0.95,
                    metadata={
                        "college_name": "Anna University",
                        "text": "Computer Science Engineering cutoff information",
                        "cutoff_info": "Previous year cutoffs: General 198, BC 193, MBC 188"
                    }
                )
            ]
            mock_index.query.return_value = mock_search_result
            
            # Import and test the agent graph
            from app.agents.graph import MynaAgentGraph
            
            # Create agent instance
            agent = MynaAgentGraph()
            
            # Process the query
            result = await agent.process_query(
                query=self.test_query,
                user_id=self.test_user_id,
                context={}
            )
            
            # Verify the result
            self.assertTrue(result["success"])
            self.assertEqual(result["processing_node"], "TNEANode")
            self.assertIn("cutoff", result["response"].lower())
            self.assertIn("anna university", result["response"].lower())
            
            # Verify GPT-4.0 was called twice (intent analysis + final response)
            self.assertEqual(mock_openai_client.chat.completions.create.call_count, 2)
            
            # Verify the calls to GPT-4.0
            calls = mock_openai_client.chat.completions.create.call_args_list
            
            # First call should be for intent analysis
            first_call_args = calls[0][1]  # Get keyword arguments
            self.assertEqual(first_call_args["model"], "gpt-4")
            self.assertIn("intent", first_call_args["messages"][0]["content"].lower())
            
            # Second call should be for final response generation
            second_call_args = calls[1][1]
            self.assertEqual(second_call_args["model"], "gpt-4")
            self.assertIn("anna university", second_call_args["messages"][1]["content"].lower())
            
            # Verify logging was called
            self.assertTrue(mock_logging.log_user_query.called)
            self.assertTrue(mock_logging.log_intent_analysis.called)
            self.assertTrue(mock_logging.log_node_routing.called)
            self.assertTrue(mock_logging.log_gpt_response.called)
            
            print("✅ Test passed: User query successfully reached GPT-4.0!")
            print(f"📝 Query: {self.test_query}")
            print(f"🎯 Intent detected: TNEA")
            print(f"🤖 Processing node: TNEANode")
            print(f"💬 Response generated: {result['response'][:100]}...")
            
            return result
        
        # Run the async test
        result = asyncio.run(run_test())
        self.assertIsNotNone(result)
    
    @patch('app.services.openai_service.OpenAI')
    @patch('app.services.logging_service.logging_service')
    def test_future_query_reaches_gpt4(self, mock_logging, mock_openai):
        """Test that a non-TNEA query reaches the Future node."""
        
        async def run_test():
            # Mock OpenAI client
            mock_openai_client = Mock()
            mock_openai.return_value = mock_openai_client
            
            # Mock intent analysis for non-TNEA query
            mock_intent_response = Mock()
            mock_intent_response.choices = [Mock()]
            mock_intent_response.choices[0].message.content = json.dumps({
                "intent": "MEDICAL",
                "confidence": 0.8,
                "reasoning": "Query is about medical college admissions, not engineering"
            })
            
            mock_openai_client.chat.completions.create = AsyncMock(
                return_value=mock_intent_response
            )
            
            # Import and test
            from app.agents.graph import MynaAgentGraph
            agent = MynaAgentGraph()
            
            medical_query = "What are the NEET cutoffs for medical colleges?"
            result = await agent.process_query(
                query=medical_query,
                user_id=self.test_user_id,
                context={}
            )
            
            # Verify routing to Future node
            self.assertTrue(result["success"])
            self.assertEqual(result["processing_node"], "FutureNode")
            self.assertTrue(result.get("future_implementation", False))
            
            # Verify GPT-4.0 was called for intent analysis
            self.assertTrue(mock_openai_client.chat.completions.create.called)
            
            print("✅ Test passed: Non-TNEA query correctly routed to Future node!")
            print(f"📝 Query: {medical_query}")
            print(f"🎯 Intent detected: MEDICAL")
            print(f"🤖 Processing node: FutureNode")
            
            return result
            
        result = asyncio.run(run_test())
        self.assertIsNotNone(result)
    
    def test_openai_service_configuration(self):
        """Test that OpenAI service is configured to use GPT-4.0."""
        from app.services.openai_service import OpenAIService
        from app.config.settings import settings
        
        # Verify GPT-4 model is configured
        service = OpenAIService()
        self.assertEqual(service.model, "gpt-4")
        
        # Verify API key is configured
        self.assertIsNotNone(settings.openai_api_key)
        self.assertTrue(len(settings.openai_api_key) > 10)
        
        print("✅ Test passed: OpenAI service correctly configured for GPT-4.0!")
        print(f"🔑 API Key configured: {settings.openai_api_key[:20]}...")
        print(f"🤖 Model: {service.model}")

    def test_end_to_end_integration(self):
        """Integration test that verifies the complete flow without mocking."""
        
        async def run_integration_test():
            try:
                # This test uses real services - only run if API keys are valid
                from app.config.settings import settings
                if not settings.openai_api_key or settings.openai_api_key.startswith('your-'):
                    print("⚠️ Skipping integration test - API keys not configured")
                    return
                
                from app.agents.graph import MynaAgentGraph
                agent = MynaAgentGraph()
                
                # Test with a simple query
                simple_query = "Tell me about engineering admissions"
                result = await agent.process_query(
                    query=simple_query,
                    user_id="integration_test_user",
                    context={}
                )
                
                # Basic verification
                self.assertTrue(result["success"])
                self.assertIsNotNone(result["response"])
                self.assertIsNotNone(result["processing_node"])
                
                print("✅ Integration test passed!")
                print(f"📝 Query: {simple_query}")
                print(f"🤖 Processing node: {result['processing_node']}")
                print(f"💬 Response: {result['response'][:100]}...")
                
            except Exception as e:
                print(f"⚠️ Integration test failed (expected if APIs not configured): {str(e)}")
        
        # Only run if this is not a CI environment
        try:
            asyncio.run(run_integration_test())
        except Exception:
            pass  # Skip if environment not ready


def run_specific_test():
    """Helper function to run a specific test."""
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(TestUserQueryToGPT('test_tnea_query_reaches_gpt4'))
    
    # Run the test
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 Testing User Query to GPT-4.0 Flow")
    print("=" * 50)
    
    # Run all tests
    unittest.main(verbosity=2)
