from openai import OpenAI
from app.config.settings import settings
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.tnea_assistant_id = None
        self.active_threads = {}  # Store thread IDs per session
    
    async def get_or_create_tnea_assistant(self) -> str:
        """
        Get or create the TNEA Assistant for efficient conversations.
        This implements Option 3: Assistant API approach.
        """
        if self.tnea_assistant_id:
            return self.tnea_assistant_id
            
        try:
            # Create TNEA Assistant with system instructions
            assistant = self.client.beta.assistants.create(
                name="TNEA Counseling Assistant",
                instructions="""You are a TNEA (Tamil Nadu Engineering Admissions) expert and Query Planner.  
Default year = 2024 unless user explicitly asks for another year.  

Your job is to analyze user queries about Tamil Nadu Engineering Admissions and provide comprehensive guidance based on the provided context.

### Analysis Rules

1. **Cutoff-based queries**  
   - If a student provides their cutoff (e.g., "my cutoff is 180"), suggest colleges and departments where they can get admission.
   - Prioritize colleges with cutoff_OC <= student_score for definite admission chances.
   - Also include colleges slightly above their cutoff (reach options) with clear probability indicators.
   - Order results by cutoff value for better decision making.

2. **Department filtering**  
   - For queries about CSE, Computer Science, focus on relevant engineering branches.
   - Normalize abbreviations: "CSE", "comp sci" → "Computer Science and Engineering"
   - Include related branches when relevant.

3. **Categorized recommendations**
   - "DEFINITE ADMISSION": Cutoffs ≤ student's mark
   - "PROBABLE ADMISSION": Cutoffs 1-2 marks above student's mark  
   - "REACH COLLEGES": Cutoffs 3-4 marks above student's mark

4. **Location considerations**  
   - Prioritize colleges in requested districts/areas when specified.
   - Include location information for better decision making.

5. **Category-specific guidance**  
   - Consider different categories (OC, BC, BCM, MBC, SC, SCA, ST) based on context.
   - Provide category-specific cutoff information when available.

6. **Comprehensive analysis**
   - Extract and present cutoff information in clear, categorized format.
   - Always show actual cutoff values when available.
   - Provide actionable admission guidance and strategy.
   - If specific data is missing, clearly state limitations but provide available related information.

Present information in crisp, well-organized bullet points with clear categories and practical advice.""",
                model="gpt-4-1106-preview",
                tools=[]
            )
            
            self.tnea_assistant_id = assistant.id
            logger.info(f"Created TNEA Assistant with ID: {assistant.id}")
            return assistant.id
            
        except Exception as e:
            logger.error(f"Error creating TNEA Assistant: {str(e)}")
            raise
    
    async def get_or_create_thread(self, session_id: str) -> str:
        """
        Get or create a conversation thread for a session.
        """
        if session_id in self.active_threads:
            return self.active_threads[session_id]
        
        try:
            thread = self.client.beta.threads.create()
            self.active_threads[session_id] = thread.id
            logger.info(f"Created new thread {thread.id} for session {session_id}")
            return thread.id
            
        except Exception as e:
            logger.error(f"Error creating thread for session {session_id}: {str(e)}")
            raise
    
    async def generate_response_with_assistant(self, query: str, context: str = "", session_id: str = "default") -> str:
        """
        Generate response using Assistant API for efficient conversation.
        This saves tokens by not repeating system prompt.
        """
        try:
            # Get or create assistant and thread
            assistant_id = await self.get_or_create_tnea_assistant()
            thread_id = await self.get_or_create_thread(session_id)
            
            # Prepare the user message with context
            user_message = f"Context: {context}\n\nUser Query: {query}" if context else query
            
            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            
            # Wait for completion
            import time
            while run.status in ['queued', 'in_progress']:
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            
            if run.status == 'completed':
                # Get the assistant's response
                messages = self.client.beta.threads.messages.list(thread_id=thread_id)
                latest_message = messages.data[0]
                
                if latest_message.role == "assistant":
                    response_content = latest_message.content[0].text.value
                    logger.info(f"Assistant response generated successfully for session {session_id}")
                    return response_content
                else:
                    raise Exception("Latest message is not from assistant")
            else:
                raise Exception(f"Assistant run failed with status: {run.status}")
                
        except Exception as e:
            logger.error(f"Error in Assistant API response generation: {str(e)}")
            # Fallback to traditional method
            logger.info("Falling back to traditional chat completion method")
            return await self.generate_response_fallback(query, context)
    
    async def generate_response_fallback(self, query: str, context: str = "") -> str:
        """
        Fallback method using traditional chat completion.
        """
        system_prompt = """You are a TNEA (Tamil Nadu Engineering Admissions) expert and Query Planner.  
Default year = 2024 unless user explicitly asks for another year.  

Provide comprehensive guidance based on the provided context with clear categorization and practical advice."""
        
        try:
            full_prompt = f"Context: {context}\n\nUser Query: {query}" if context else query
            
            response = await self._chat_completion(
                system_prompt=system_prompt,
                user_message=full_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in fallback response generation: {str(e)}")
            return f"I'm sorry, but I encountered an error while processing your request: {str(e)}"
    
    def cleanup_thread(self, session_id: str):
        """
        Clean up thread when session ends to free resources.
        """
        if session_id in self.active_threads:
            thread_id = self.active_threads.pop(session_id)
            try:
                self.client.beta.threads.delete(thread_id)
                logger.info(f"Cleaned up thread {thread_id} for session {session_id}")
            except Exception as e:
                logger.warning(f"Error cleaning up thread {thread_id}: {str(e)}")
    
    async def analyze_intent(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user query to determine intent and routing.
        Returns intent classification and confidence.
        """
        system_prompt = """You are an intent router for a college recommendation system.

Classify:
- "TNEA": Queries about Tamil Nadu Engineering Admissions (TNEA), e.g.
  • Marks/cutoff given and asking what college/seat is possible
  • Asking required cutoff for a specific engineering college/branch
- "FUTURE": Anything else (medical, non-engineering, general guidance)

Rule: If marks/scores are mentioned with admission/seat questions, assume TNEA unless clearly stated otherwise.

Return JSON:
{
  "intent": "TNEA" | "FUTURE",
  "confidence": float (0.0–1.0),
  "reasoning": "brief explanation"
}
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
    
    async def generate_response(self, query: str, context: str = "", system_prompt: str = "", session_id: str = "default") -> str:
        """
        Generate response - now uses Assistant API by default for efficiency.
        Falls back to traditional method if Assistant API fails.
        """
        # If session_id is provided, use Assistant API (more efficient)
        if session_id and session_id != "default":
            try:
                return await self.generate_response_with_assistant(query, context, session_id)
            except Exception as e:
                logger.warning(f"Assistant API failed, falling back to traditional method: {str(e)}")
        
        # Fallback to traditional method
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
