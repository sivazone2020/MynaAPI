"""
Debug the LangGraph workflow step by step
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

from app.agents.graph import MynaAgentGraph

async def debug_workflow():
    """Debug the workflow step by step."""
    
    print("🔍 Debugging LangGraph Workflow")
    print("=" * 50)
    
    # Initialize the agent graph
    agent_graph = MynaAgentGraph()
    
    # Test query that should route to TNEA
    test_query = "I want to study Computer Science. I scored 175 marks in TNEA. Which colleges can I get?"
    user_id = "debug_user"
    
    print(f"📝 Query: {test_query}")
    print(f"👤 User ID: {user_id}")
    
    try:
        print("\n🚀 Starting workflow...")
        
        result = await agent_graph.process_query(
            query=test_query,
            user_id=user_id
        )
        
        print(f"\n✅ Workflow completed!")
        print(f"📊 Result type: {type(result)}")
        print(f"📋 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print(f"📄 Full result: {result}")
            
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_workflow())
