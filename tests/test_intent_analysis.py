"""
Test script to verify the updated intent analysis logic
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

from app.services.openai_service import OpenAIService

async def test_intent_analysis():
    """Test the updated intent analysis with various queries."""
    
    openai_service = OpenAIService()
    
    test_queries = [
        "I want to study Computer Science. I scored 175 marks in TNEA. Which colleges can I get?",
        "I scored 180 marks. Which engineering colleges can I get admission?",
        "What are the cutoff marks for Computer Science engineering?",
        "I want to study engineering. My marks are 170. Help me find colleges.",
        "Which IT colleges are available for my score of 165?",
        "I want to become a doctor. NEET preparation tips?",
        "Tell me about mechanical engineering colleges.",
        "I scored 175 marks. Can I get admission in good colleges?",
        "What is the admission process for engineering?",
        "Help me with career guidance in general."
    ]
    
    print("🧪 Testing Updated Intent Analysis")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        
        try:
            result = await openai_service.analyze_intent(query)
            
            print(f"📊 Intent: {result.get('intent', 'N/A')}")
            print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
            print(f"💭 Reasoning: {result.get('reasoning', 'N/A')}")
            
            # Expected vs Actual analysis
            expected_tnea = any(keyword in query.lower() for keyword in [
                'computer science', 'engineering', 'cutoff', 'marks', 'score', 
                'admission', 'colleges', 'it', 'mechanical'
            ]) and 'doctor' not in query.lower() and 'neet' not in query.lower()
            
            actual_tnea = result.get('intent') == 'TNEA'
            
            if expected_tnea == actual_tnea:
                print("✅ Classification correct!")
            else:
                print(f"❌ Classification mismatch! Expected: {'TNEA' if expected_tnea else 'FUTURE'}, Got: {result.get('intent')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Intent analysis testing completed!")

if __name__ == "__main__":
    asyncio.run(test_intent_analysis())
