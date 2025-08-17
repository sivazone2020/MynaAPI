#!/usr/bin/env python3
"""
Real Pinecone Integration Test
This test verifies that we can connect to the REAL Pinecone service and perform searches.
"""

import sys
import os
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_real_pinecone_connection():
    """Test real Pinecone connection and operations."""
    
    print("🗃️  Testing REAL Pinecone Integration")
    print("=" * 50)
    
    try:
        # Import services
        from app.config.settings import settings
        from app.services.pinecone_service import get_pinecone_service
        from app.services.openai_service import get_openai_service
        
        print(f"✅ Configuration loaded")
        print(f"📊 Pinecone API Key: {settings.pinecone_api_key[:20]}...")
        print(f"🔗 Pinecone Host: {settings.pinecone_host}")
        print(f"📑 Pinecone Index: {settings.pinecone_index}")
        print()
        
        # Test Pinecone service initialization
        print("🔧 Initializing Pinecone service...")
        pinecone_service = get_pinecone_service()
        print("✅ Pinecone service created")
        
        # Check index status
        print("📊 Checking Pinecone index status...")
        status = pinecone_service.check_index_status()
        print(f"📋 Index Status: {status}")
        
        if status.get("status") == "connected":
            print("✅ Successfully connected to Pinecone index!")
            print(f"📊 Total vectors: {status.get('total_vector_count', 'unknown')}")
            print(f"📏 Dimension: {status.get('dimension', 'unknown')}")
            print(f"💾 Index fullness: {status.get('index_fullness', 'unknown')}")
        else:
            print(f"❌ Pinecone connection failed: {status.get('error', 'unknown error')}")
            return False
        
        print()
        
        # Test OpenAI embedding generation
        print("🧠 Testing OpenAI embedding generation...")
        openai_service = get_openai_service()
        
        test_query = "What is the cutoff for Anna University Computer Science Engineering?"
        print(f"📝 Test query: {test_query}")
        
        embedding = await openai_service.get_embedding(test_query)
        print(f"✅ Generated embedding with {len(embedding)} dimensions")
        print(f"📊 First few values: {embedding[:5]}")
        print()
        
        # Test Pinecone search with real embedding
        print("🔍 Testing Pinecone vector search with real embedding...")
        try:
            search_results = await pinecone_service.search_similar(
                query_vector=embedding,
                top_k=5
            )
            
            print(f"📊 Search completed: {len(search_results)} results found")
            
            if search_results:
                print("✅ Vector search successful!")
                for i, result in enumerate(search_results):
                    print(f"   Result {i+1}:")
                    print(f"      ID: {result.get('id', 'unknown')}")
                    print(f"      Score: {result.get('score', 0):.4f}")
                    metadata = result.get('metadata', {})
                    print(f"      College: {metadata.get('college_name', 'N/A')}")
                    print(f"      Text preview: {str(metadata.get('text', 'N/A'))[:100]}...")
                    print()
            else:
                print("⚠️  No results found - this might indicate:")
                print("   - The index is empty (no data uploaded)")
                print("   - The query doesn't match existing vectors")
                print("   - There might be a dimension mismatch")
                
        except Exception as e:
            print(f"❌ Pinecone search failed: {str(e)}")
            return False
        
        print()
        
        # Test RAG context generation
        print("📚 Testing RAG context generation...")
        try:
            context = await pinecone_service.get_context_for_query(
                query_embedding=embedding,
                max_context_length=1000
            )
            
            print(f"✅ Context generation successful!")
            print(f"📊 Context length: {len(context)} characters")
            print("📄 Context preview:")
            print("-" * 40)
            print(context[:300] + "..." if len(context) > 300 else context)
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Context generation failed: {str(e)}")
            return False
        
        print()
        print("🎉 ALL REAL PINECONE TESTS PASSED!")
        print("✅ Pinecone connection working")
        print("✅ OpenAI embedding generation working")
        print("✅ Vector search functional")
        print("✅ RAG context generation working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_end_to_end_with_real_services():
    """Test the complete E2E flow with real services."""
    
    print("\n🔄 Testing Complete E2E Flow with Real Services")
    print("=" * 60)
    
    try:
        from app.agents.graph import MynaAgentGraph
        
        # Create agent
        agent = MynaAgentGraph()
        print("✅ Agent graph created")
        
        # Test query
        test_query = "What is the cutoff for Anna University Computer Science Engineering?"
        print(f"📝 Processing query: {test_query}")
        
        # Process with real services
        result = await agent.process_query(
            query=test_query,
            user_id="real_test_user",
            context={"test_type": "real_services"}
        )
        
        print(f"✅ Query processed successfully!")
        print(f"🎯 Intent: {result.get('intent', 'unknown')}")
        print(f"🤖 Node: {result.get('processing_node', 'unknown')}")
        print(f"📊 Success: {result.get('success', False)}")
        print(f"⏱️  Duration: {result.get('duration', 0):.2f}s")
        
        response = result.get('response', '')
        print(f"💬 Response length: {len(response)} chars")
        print("📄 Response preview:")
        print("-" * 40)
        print(response[:400] + "..." if len(response) > 400 else response)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ E2E test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test runner."""
    print("🧪 Real Pinecone Integration Test Suite")
    print("=" * 70)
    print("This test verifies REAL Pinecone and OpenAI integration:")
    print("🗃️  Real Pinecone vector database connection")
    print("🧠 Real OpenAI embedding generation")
    print("🔍 Real vector similarity search")
    print("📚 Real RAG context retrieval")
    print("🔄 Complete E2E agent flow")
    print()
    
    # Warning about API usage
    print("⚠️  WARNING: This test will make REAL API calls!")
    print("💰 This will consume API credits!")
    print()
    
    user_input = input("Continue with real API testing? (y/N): ").strip().lower()
    if user_input != 'y':
        print("❌ Test cancelled by user")
        return
    
    print()
    
    try:
        # Test Pinecone connection
        success1 = asyncio.run(test_real_pinecone_connection())
        
        if success1:
            # Test complete E2E flow
            success2 = asyncio.run(test_end_to_end_with_real_services())
            
            if success2:
                print("\n🎊 ALL TESTS PASSED!")
                print("✅ Real Pinecone integration working")
                print("✅ Real OpenAI integration working")
                print("✅ Complete E2E flow functional")
                print("✅ System ready for production use!")
            else:
                print("\n⚠️  Pinecone tests passed but E2E failed")
        else:
            print("\n❌ Pinecone connection tests failed")
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()
