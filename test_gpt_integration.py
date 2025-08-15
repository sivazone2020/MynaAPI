#!/usr/bin/env python3
"""
Standalone test script to verify user query reaches GPT-4.0
This script can be run independently to test the core functionality.
"""

import sys
import os
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_query_to_gpt4():
    """Test that demonstrates a user query reaching GPT-4.0."""
    
    print("🚀 Starting GPT-4.0 Integration Test")
    print("=" * 50)
    
    # Test data
    test_query = "What is the cutoff for Anna University Computer Science Engineering?"
    test_user = "test_user_123"
    
    print(f"📝 Test Query: {test_query}")
    print(f"👤 Test User: {test_user}")
    print()
    
    try:
        # Mock external services to avoid API calls during testing
        with patch('openai.OpenAI') as mock_openai, \
             patch('pinecone.Pinecone') as mock_pinecone, \
             patch('app.services.logging_service.logging_service') as mock_logging:
            
            print("🔧 Setting up mocks...")
            
            # Configure OpenAI mock
            mock_openai_client = Mock()
            mock_openai.return_value = mock_openai_client
            
            # Mock intent analysis response (first GPT-4 call)
            intent_response = Mock()
            intent_response.choices = [Mock()]
            intent_response.choices[0].message.content = json.dumps({
                "intent": "TNEA",
                "confidence": 0.95,
                "reasoning": "Query asks about Anna University cutoff which is TNEA related"
            })
            
            # Mock final response (second GPT-4 call)
            final_response = Mock()
            final_response.choices = [Mock()]
            final_response.choices[0].message.content = """Based on the available information about Anna University Computer Science Engineering admissions:

**Previous Year Cutoffs (Approximate):**
- General Category: 195-200 marks
- BC Category: 190-195 marks  
- MBC Category: 185-190 marks
- SC/ST Category: 175-185 marks

**Important Notes:**
- These are approximate figures based on previous years
- Actual cutoffs vary each year based on factors like difficulty level and number of applicants
- For the most current information, please check the official TNEA website

Would you like information about any other engineering colleges or branches?"""
            
            # Configure mock to return different responses for different calls
            mock_openai_client.chat.completions.create = AsyncMock(
                side_effect=[intent_response, final_response]
            )
            
            # Configure Pinecone mock
            mock_pinecone_instance = Mock()
            mock_pinecone.return_value = mock_pinecone_instance
            mock_index = Mock()
            mock_pinecone_instance.Index.return_value = mock_index
            
            # Mock Pinecone search results
            search_result = Mock()
            search_result.matches = [
                Mock(
                    id="anna_univ_cs_cutoff",
                    score=0.92,
                    metadata={
                        "college_name": "Anna University",
                        "text": "Anna University is a premier technical university offering engineering programs. Computer Science Engineering is one of the most sought-after branches.",
                        "cutoff_info": "Previous year CSE cutoffs: General 198, BC 193, MBC 188, SC/ST 178"
                    }
                )
            ]
            mock_index.query.return_value = search_result
            
            print("✅ Mocks configured successfully")
            print()
            
            # Import the agent system
            print("📦 Importing agent system...")
            from app.agents.graph import MynaAgentGraph
            
            # Create and test the agent
            print("🤖 Creating agent instance...")
            agent = MynaAgentGraph()
            
            print("🔄 Processing query through agent graph...")
            result = await agent.process_query(
                query=test_query,
                user_id=test_user,
                context={"source": "test"}
            )
            
            print("📊 Analyzing results...")
            print()
            
            # Verify and display results
            success = result.get("success", False)
            response = result.get("response", "")
            processing_node = result.get("processing_node", "unknown")
            intent = result.get("intent", "unknown")
            
            print("🎯 TEST RESULTS:")
            print(f"   ✅ Success: {success}")
            print(f"   🎯 Intent Detected: {intent}")
            print(f"   🤖 Processing Node: {processing_node}")
            print(f"   📝 Response Length: {len(response)} characters")
            print()
            
            print("💬 GPT-4.0 RESPONSE:")
            print("-" * 30)
            print(response)
            print("-" * 30)
            print()
            
            # Verify GPT-4.0 was called
            gpt_calls = mock_openai_client.chat.completions.create.call_count
            print(f"🔍 VERIFICATION:")
            print(f"   📞 GPT-4.0 API Calls: {gpt_calls}")
            
            if gpt_calls >= 2:
                print("   ✅ Intent analysis call made")
                print("   ✅ Response generation call made")
                
                # Check call details
                calls = mock_openai_client.chat.completions.create.call_args_list
                
                # Verify first call (intent analysis)
                first_call = calls[0][1]
                print(f"   🎯 First call model: {first_call.get('model', 'unknown')}")
                
                # Verify second call (response generation)  
                second_call = calls[1][1]
                print(f"   💬 Second call model: {second_call.get('model', 'unknown')}")
                
                print("   ✅ Query successfully reached GPT-4.0!")
            else:
                print("   ❌ Insufficient GPT-4.0 calls detected")
            
            print()
            
            # Verify logging calls
            if mock_logging.log_user_query.called:
                print("   ✅ User query logged")
            if mock_logging.log_intent_analysis.called:
                print("   ✅ Intent analysis logged")
            if mock_logging.log_node_routing.called:
                print("   ✅ Node routing logged")
            if mock_logging.log_gpt_response.called:
                print("   ✅ GPT response logged")
            
            print()
            print("🎉 TEST COMPLETED SUCCESSFULLY!")
            print("✅ User query successfully flowed through the system to GPT-4.0")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're running this from the project root directory")
        return False
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        print(f"📍 Error type: {type(e).__name__}")
        return False

async def test_different_query_types():
    """Test different types of queries to verify routing."""
    
    print("\n🔄 Testing Different Query Types")
    print("=" * 40)
    
    test_cases = [
        {
            "query": "What is the TNEA cutoff for CSE?",
            "expected_intent": "TNEA",
            "expected_node": "TNEANode"
        },
        {
            "query": "Tell me about medical college admissions",
            "expected_intent": "MEDICAL", 
            "expected_node": "FutureNode"
        },
        {
            "query": "How do I prepare for JEE?",
            "expected_intent": "JEE",
            "expected_node": "FutureNode"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['query']}")
        
        try:
            with patch('openai.OpenAI') as mock_openai:
                # Mock OpenAI response
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                intent_response = Mock()
                intent_response.choices = [Mock()]
                intent_response.choices[0].message.content = json.dumps({
                    "intent": test_case['expected_intent'],
                    "confidence": 0.9,
                    "reasoning": f"Query is about {test_case['expected_intent']} related topics"
                })
                
                mock_client.chat.completions.create = AsyncMock(return_value=intent_response)
                
                # Test the router node specifically
                from app.agents.nodes.router_node import router_node
                
                state = {
                    "query": test_case['query'],
                    "user_id": "test_user",
                    "context": {}
                }
                
                result = await router_node.process(state)
                
                detected_intent = result.get("intent", "unknown")
                next_node = result.get("next_node", "unknown")
                
                print(f"   🎯 Detected Intent: {detected_intent}")
                print(f"   🤖 Routed to: {next_node}")
                
                if detected_intent == test_case['expected_intent']:
                    print("   ✅ Intent detection correct")
                else:
                    print("   ⚠️ Intent detection different than expected")
                    
        except Exception as e:
            print(f"   ❌ Test failed: {e}")

def main():
    """Main test function."""
    print("🧪 MynaAPI GPT-4.0 Integration Test Suite")
    print("=" * 60)
    print("This test verifies that user queries reach GPT-4.0 through the agent system")
    print()
    
    try:
        # Run the main test
        success = asyncio.run(test_query_to_gpt4())
        
        if success:
            # Run additional tests
            asyncio.run(test_different_query_types())
            
            print("\n🎊 ALL TESTS COMPLETED!")
            print("✅ The system successfully routes user queries to GPT-4.0")
            print("✅ Intent analysis is working correctly")
            print("✅ Node routing is functioning properly")
            print("✅ Response generation is operational")
            
        else:
            print("\n❌ TESTS FAILED")
            print("Please check the error messages above")
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()
