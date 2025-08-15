"""
End-to-End tests with real API integrations
"""
import pytest
import asyncio
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.graph import MynaAgentGraph
from app.models.request_models import QueryRequest
from app.services.logging_service import LoggingService


@pytest.mark.asyncio
async def test_full_query_flow_with_real_apis():
    """Test the complete query flow using real OpenAI and Pinecone APIs."""
    
    print("\n🚀 Starting E2E test with real APIs...")
    
    # Initialize services
    logging_service = LoggingService()
    agent_graph = MynaAgentGraph()
    
    # Test query - looking for computer science colleges
    test_query = QueryRequest(
        query="I want to study Computer Science. I scored 175 marks in TNEA. Which colleges can I get?"
    )
    
    print(f"📝 Test Query: {test_query.query}")
    print(f"👤 Session ID: {test_query.session_id}")
    print(f"📋 Context: {test_query.context}")
    
    try:
        # Process the query through the agent graph
        print("\n🔄 Processing query through agent graph...")
        result = await agent_graph.process_query(
            query=test_query.query,
            user_id="test_user_123",
            context=test_query.context
        )
        
        print(f"✅ Query processed successfully!")
        print(f"📊 Result type: {type(result)}")
        print(f"📋 Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        # Validate the result structure
        assert result is not None, "Result should not be None"
        
        if isinstance(result, dict):
            # Check for expected response structure
            assert 'status' in result or 'response' in result or 'recommendations' in result, \
                "Result should contain status, response, or recommendations"
            
            print(f"📝 Final result: {result}")
        else:
            print(f"📝 Final result: {result}")
        
        # Test that we can access the result
        print("\n✅ All assertions passed!")
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        raise


@pytest.mark.asyncio
async def test_pinecone_integration():
    """Test Pinecone service integration specifically."""
    
    print("\n🔍 Testing Pinecone integration...")
    
    from app.services.pinecone_service import PineconeService
    from app.services.openai_service import OpenAIService
    
    # Initialize services
    pinecone_service = PineconeService()
    openai_service = OpenAIService()
    
    # Check if Pinecone is properly initialized
    assert pinecone_service.index is not None, "Pinecone index should be initialized"
    
    # Test query
    test_query = "Computer Science engineering colleges"
    
    # Get embedding from OpenAI
    print(f"🔄 Getting embedding for: {test_query}")
    embedding = await openai_service.get_embedding(test_query)
    
    assert embedding is not None, "Should get embedding from OpenAI"
    assert len(embedding) == 3072, f"Embedding should be 3072 dimensions, got {len(embedding)}"
    
    # Search in Pinecone
    print("🔍 Searching in Pinecone...")
    results = await pinecone_service.search_similar(embedding, top_k=5)
    
    assert results is not None, "Should get results from Pinecone"
    assert len(results) > 0, "Should get at least one result"
    
    print(f"📊 Found {len(results)} results")
    
    # Validate result structure
    for i, result in enumerate(results[:3]):
        print(f"  🎯 Result {i+1}:")
        print(f"      ID: {result.get('id', 'N/A')}")
        print(f"      Score: {result.get('score', 'N/A')}")
        print(f"      Metadata keys: {list(result.get('metadata', {}).keys())}")
        
        # Check that results have expected structure
        assert 'id' in result, "Result should have ID"
        assert 'score' in result, "Result should have score"
        assert 'metadata' in result, "Result should have metadata"
    
    print("\n✅ Pinecone integration test passed!")


@pytest.mark.asyncio
async def test_openai_integration():
    """Test OpenAI service integration specifically."""
    
    print("\n🤖 Testing OpenAI integration...")
    
    from app.services.openai_service import OpenAIService
    
    openai_service = OpenAIService()
    
    # Test intent analysis
    test_query = "I want to study Computer Science and scored 175 marks"
    
    print(f"🔄 Analyzing intent for: {test_query}")
    intent = await openai_service.analyze_intent(test_query)
    
    assert intent is not None, "Should get intent analysis"
    assert 'intent' in intent, "Intent should have intent field"
    
    print(f"📊 Intent: {intent}")
    
    # Test response generation
    context = "Sample college information"
    print(f"🔄 Generating response with context...")
    
    response = await openai_service.generate_response(test_query, context)
    
    assert response is not None, "Should get response"
    assert len(response) > 0, "Response should not be empty"
    
    print(f"📝 Generated response length: {len(response)} characters")
    print(f"📝 Response preview: {response[:200]}...")
    
    print("\n✅ OpenAI integration test passed!")


if __name__ == "__main__":
    # Run the tests directly
    asyncio.run(test_full_query_flow_with_real_apis())
    asyncio.run(test_pinecone_integration()) 
    asyncio.run(test_openai_integration())
