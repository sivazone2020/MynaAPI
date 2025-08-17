"""
Test script to query specific college cutoff information
Testing: CSE cutoff for Gojan School of Business and Technology
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

from app.agents.graph import MynaAgentGraph

async def test_gojan_cse_cutoff():
    """Test query for CSE cutoff in Gojan School of Business and Technology."""
    
    print("🎯 Testing Specific College Cutoff Query")
    print("=" * 60)
    
    # Initialize the agent graph
    agent_graph = MynaAgentGraph()
    
    # Test query for specific college and branch
    test_query = "What is the cutoff for CSE in Gojan School of Business and Technology?"
    user_id = "test_user_gojan"
    
    print(f"📝 Query: {test_query}")
    print(f"👤 User ID: {user_id}")
    print(f"🏫 Target College: Gojan School of Business and Technology")
    print(f"📚 Target Branch: Computer Science Engineering (CSE)")
    
    try:
        print(f"\n🚀 Processing query...")
        
        result = await agent_graph.process_query(
            query=test_query,
            user_id=user_id
        )
        
        print(f"\n✅ Query processed successfully!")
        print(f"⏱️  Processing time: {result.get('duration', 'N/A')} seconds")
        print(f"🎯 Processing node: {result.get('processing_node', 'N/A')}")
        print(f"🧠 Intent: {result.get('intent', 'N/A')}")
        print(f"📊 Confidence: {result.get('confidence', 'N/A')}")
        
        print(f"\n📋 RESPONSE:")
        print("=" * 60)
        print(result.get('response', 'No response'))
        print("=" * 60)
        
        # Extract key information if available
        response_text = result.get('response', '').lower()
        
        print(f"\n🔍 ANALYSIS:")
        if 'gojan' in response_text:
            print("✅ Found information about Gojan School of Business and Technology")
        else:
            print("❌ No specific information about Gojan found in response")
            
        if 'computer science' in response_text or 'cse' in response_text:
            print("✅ Response contains CSE/Computer Science information")
        else:
            print("❌ No CSE-specific information found")
            
        if 'cutoff' in response_text:
            print("✅ Response contains cutoff information")
        else:
            print("❌ No cutoff information found")
            
        # Check if actual numbers are mentioned
        import re
        numbers = re.findall(r'\b\d{2,3}\b', result.get('response', ''))
        if numbers:
            print(f"📊 Cutoff marks mentioned: {numbers}")
        else:
            print("📊 No specific cutoff marks found")
            
        return result
        
    except Exception as e:
        print(f"❌ Error in query processing: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_alternative_gojan_queries():
    """Test alternative phrasings for Gojan queries."""
    
    print(f"\n🔄 Testing Alternative Query Phrasings")
    print("=" * 60)
    
    agent_graph = MynaAgentGraph()
    
    alternative_queries = [
        "Tell me about computer science cutoff in Gojan college",
        "Gojan School of Business and Technology CSE admission marks",
        "What are the cutoff marks for IT in Gojan college?",
        "I want to study in Gojan college. What marks do I need for Computer Science?"
    ]
    
    for i, query in enumerate(alternative_queries, 1):
        print(f"\n🔍 Alternative Query {i}: {query}")
        
        try:
            result = await agent_graph.process_query(
                query=query,
                user_id=f"test_user_alt_{i}"
            )
            
            response = result.get('response', '')
            
            # Check if Gojan is mentioned
            if 'gojan' in response.lower():
                print(f"✅ Found Gojan information!")
                # Extract any cutoff numbers
                import re
                numbers = re.findall(r'\b\d{2,3}\b', response)
                if numbers:
                    print(f"📊 Cutoff marks: {numbers}")
                else:
                    print("📊 No specific cutoff marks found")
            else:
                print(f"❌ No Gojan-specific information found")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎓 GOJAN COLLEGE CSE CUTOFF TEST")
    print("=" * 60)
    
    # Run the main test
    main_result = asyncio.run(test_gojan_cse_cutoff())
    
    # Run alternative queries
    asyncio.run(test_alternative_gojan_queries())
    
    print(f"\n🏁 Test completed!")
    if main_result and main_result.get('success'):
        print("✅ Main test passed - API is working correctly")
    else:
        print("❌ Main test failed - Check for issues")
