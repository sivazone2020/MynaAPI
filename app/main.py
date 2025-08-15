from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.auth.routes import router as auth_router, get_current_user
from app.auth.models import User
from app.models.request_models import QueryRequest, HealthCheckRequest
from app.models.response_models import QueryResponse, ErrorResponse, HealthCheckResponse
from app.agents.graph import myna_agent
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to MynaAPI - College Recommendation Service",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.utcnow()
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Basic health checks
        services_status = {
            "api": "healthy",
            "openai": "healthy",  # Could add actual OpenAI ping
            "pinecone": "healthy",  # Could add actual Pinecone ping
            "logging": "healthy"
        }
        
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            services=services_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )


@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Main query processing endpoint.
    Requires authentication.
    """
    try:
        logger.info(f"Processing query for user: {current_user.username}")
        
        # Process query through the agent graph
        result = await myna_agent.process_query(
            query=request.query,
            user_id=current_user.username,
            context=request.context
        )
        
        if result.get("success", False):
            return QueryResponse(
                response=result["response"],
                session_id=result["session_id"],
                processing_node=result["processing_node"],
                intent=result.get("intent"),
                confidence=result.get("confidence"),
                timestamp=result["timestamp"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Processing failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/api/v1/logs")
async def get_logs(current_user: User = Depends(get_current_user)):
    """
    Get application logs (admin endpoint).
    """
    try:
        # Simple log retrieval - in production, implement proper log management
        with open("logs/interactions.log", "r") as f:
            logs = f.readlines()[-100:]  # Last 100 lines
        
        return {
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.utcnow()
        }
    except FileNotFoundError:
        return {
            "logs": [],
            "count": 0,
            "message": "No logs found",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve logs"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc) if settings.environment == "development" else "An error occurred",
        timestamp=datetime.utcnow()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.environment == "development" else False
    )
