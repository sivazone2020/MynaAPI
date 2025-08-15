from openai import OpenAI
from app.config.settings import settings
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def analyze_intent(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user query to determine intent and routing.
        Returns intent classification and confidence.
        """
        system_prompt = """You are an intelligent router for a college recommendation system. 
        Analyze the user query and determine the intent:
        
        1. Classify as "TNEA" if the query is about:
           - Engineering colleges or courses (Computer Science, IT, ECE, Mechanical, Civil, etc.)
           - Admission to engineering programs
           - Cutoff marks or scores for engineering admission
           - Getting seats in engineering colleges
           - Tamil Nadu Engineering Admissions (TNEA) process
           - Questions mentioning marks/scores and asking about college eligibility
           - Questions about which engineering colleges are available
           
        2. Classify as "FUTURE" only for:
           - Medical admissions (NEET, medical colleges)
           - Other non-engineering courses
           - General career guidance without specific engineering focus
        
        Remember: If a user mentions their marks/score and asks about getting admission or seats in colleges, 
        it's most likely about engineering admission (TNEA) unless explicitly stated otherwise.
        
        Return a JSON response with:
        - intent: "TNEA" or "FUTURE"
        - confidence: float between 0.0 and 1.0
        - reasoning: brief explanation of classification
        """
        
        try:
            response = await self._chat_completion(
                system_prompt=system_prompt,
                user_message=user_query
            )
            
            # Parse the JSON response
            import json
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # If response isn't valid JSON, extract intent manually with engineering focus
                response_lower = response.lower()
                query_lower = user_query.lower()
                
                # Check for engineering-related keywords
                engineering_keywords = [
                    'engineering', 'computer science', 'cs', 'it', 'information technology',
                    'ece', 'electronics', 'mechanical', 'civil', 'chemical', 'biotechnology',
                    'cutoff', 'marks', 'score', 'admission', 'seat', 'college', 'tnea',
                    'anna university', 'engineering college'
                ]
                
                medical_keywords = ['medical', 'neet', 'mbbs', 'doctor', 'medicine']
                
                # Check if query contains engineering keywords
                has_engineering_terms = any(keyword in query_lower for keyword in engineering_keywords)
                has_medical_terms = any(keyword in query_lower for keyword in medical_keywords)
                
                if has_medical_terms and not has_engineering_terms:
                    result = {"intent": "FUTURE", "confidence": 0.8, "reasoning": "Detected medical keywords"}
                elif has_engineering_terms or 'tnea' in response_lower:
                    result = {"intent": "TNEA", "confidence": 0.8, "reasoning": "Detected engineering/admission keywords"}
                else:
                    # Default to TNEA if mentions marks/scores and college
                    has_marks = any(word in query_lower for word in ['mark', 'score', 'point'])
                    has_college = any(word in query_lower for word in ['college', 'admission', 'seat', 'get'])
                    
                    if has_marks and has_college:
                        result = {"intent": "TNEA", "confidence": 0.7, "reasoning": "Mentions marks and college - likely engineering admission"}
                    else:
                        result = {"intent": "FUTURE", "confidence": 0.5, "reasoning": "Could not parse JSON, no clear engineering indicators"}
            
            logger.info(f"Intent analysis result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in intent analysis: {str(e)}")
            return {
                "intent": "FUTURE",
                "confidence": 0.0,
                "reasoning": f"Error in analysis: {str(e)}"
            }
    
    async def generate_response(self, query: str, context: str = "", system_prompt: str = "") -> str:
        """
        Generate response using GPT-4.0 based on query and context.
        """
        if not system_prompt:
            system_prompt = """You are a helpful assistant for college admissions in Tamil Nadu. 
            Provide accurate, helpful, and detailed responses based on the context provided. 
            If you don't have specific information, be honest about limitations."""
        
        try:
            full_prompt = f"Context: {context}\n\nUser Query: {query}" if context else query
            
            response = await self._chat_completion(
                system_prompt=system_prompt,
                user_message=full_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in response generation: {str(e)}")
            return f"I'm sorry, but I encountered an error while processing your request: {str(e)}"
    
    async def _chat_completion(self, system_prompt: str, user_message: str, response_format: Dict = None) -> str:
        """Internal method for chat completion."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        kwargs = {
            "model": "gpt-4",
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get text embedding using OpenAI's embedding model.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            logger.info(f"Generating embedding for text: {text[:50]}...")
            response = self.client.embeddings.create(
                model="text-embedding-3-large",  # 3072 dimensions
                input=text
            )
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding of dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding from OpenAI: {str(e)}")
            raise


# Service factory function
def get_openai_service():
    return OpenAIService()
