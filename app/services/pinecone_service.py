from pinecone import Pinecone
from app.config.settings import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PineconeService:
    def __init__(self):
        # Initialize Pinecone with the new v7.x API
        try:
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            self.index_name = settings.pinecone_index
            self.index = None
            self._initialize_index()
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            self.index = None
    
    def _initialize_index(self):
        """Initialize the Pinecone index."""
        try:
            # List available indexes to verify our target index exists
            indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            
            if self.index_name not in index_names:
                logger.error(f"Index '{self.index_name}' not found. Available indexes: {index_names}")
                return
            
            # Connect to the index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Successfully connected to Pinecone index: {self.index_name}")
            
            # Get and log index stats
            stats = self.index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
            
        except Exception as e:
            logger.error(f"Failed to initialize index: {str(e)}")
            self.index = None
    
    async def search_similar(self, query_vector: List[float], top_k: int = 5, filter_dict: Dict = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Pinecone.
        
        Args:
            query_vector: The query vector to search with
            top_k: Number of top results to return
            filter_dict: Optional metadata filter
        
        Returns:
            List of similar documents with metadata
        """
        try:
            if not self.index:
                raise Exception("Pinecone index not initialized - check API key and index configuration")
            
            # Perform the search
            search_kwargs = {
                "vector": query_vector,
                "top_k": top_k,
                "include_metadata": True,
                "include_values": False
            }
            
            if filter_dict:
                search_kwargs["filter"] = filter_dict
            
            logger.info(f"Performing Pinecone search with vector length: {len(query_vector)}")
            results = self.index.query(**search_kwargs)
            
            # Format results
            formatted_results = []
            if hasattr(results, 'matches'):
                for match in results.matches:
                    formatted_results.append({
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata if hasattr(match, 'metadata') else {}
                    })
            
            logger.info(f"Pinecone search completed: {len(formatted_results)} documents found")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in Pinecone search: {str(e)}")
            raise  # Re-raise the exception instead of returning mock data
    
    async def get_context_for_query(self, query_embedding: List[float], max_context_length: int = 2000) -> str:
        """
        Get relevant context from Pinecone for RAG.
        
        Args:
            query_embedding: Vector representation of the query
            max_context_length: Maximum length of context to return
        
        Returns:
            Concatenated context string from relevant documents
        """
        try:
            # Search for relevant documents in REAL Pinecone
            logger.info("Searching Pinecone for relevant context...")
            results = await self.search_similar(query_embedding, top_k=5)
            
            if not results:
                logger.warning("No documents found in Pinecone index - index may be empty")
                return "No specific documents found in the knowledge base. This may indicate the index needs to be populated with TNEA data."
            
            # Extract and concatenate text content
            context_parts = []
            current_length = 0
            
            for i, result in enumerate(results):
                metadata = result.get("metadata", {})
                text_content = metadata.get("text", "")
                college_name = metadata.get("college_name", "")
                cutoff_info = metadata.get("cutoff_info", "")
                score = result.get("score", 0)
                
                # Format the context piece
                context_piece = f"Document {i+1} (relevance: {score:.3f}):\nCollege: {college_name}\n{text_content}\nCutoff Info: {cutoff_info}\n\n"
                
                if current_length + len(context_piece) > max_context_length:
                    break
                
                context_parts.append(context_piece)
                current_length += len(context_piece)
            
            final_context = "".join(context_parts) if context_parts else "No relevant context extracted from documents."
            logger.info(f"Generated context: {len(final_context)} characters from {len(results)} Pinecone documents")
            return final_context
            
        except Exception as e:
            logger.error(f"Error getting context from Pinecone: {str(e)}")
            raise  # Re-raise to ensure errors are visible
    
    def check_index_status(self) -> Dict[str, Any]:
        """Check Pinecone index status and stats."""
        try:
            if not self.index:
                return {"status": "disconnected", "error": "Index not initialized"}
            
            stats = self.index.describe_index_stats()
            return {
                "status": "connected",
                "total_vector_count": stats.total_vector_count if hasattr(stats, 'total_vector_count') else 0,
                "index_fullness": stats.index_fullness if hasattr(stats, 'index_fullness') else 0,
                "dimension": stats.dimension if hasattr(stats, 'dimension') else 'unknown'
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Service factory function
def get_pinecone_service():
    return PineconeService()
