# MynaAPI - College Recommendation Backend Service

MynaAPI is an intelligent backend service that helps school students find the best colleges based on their academic marks. The system uses Agentic AI with LangGraph to process user queries and provide intelligent responses.

## Features

- 🤖 **Agentic AI Architecture**: Multi-node processing using LangGraph
- 🎯 **Intent-based Routing**: Intelligent query classification and routing
- 📚 **RAG Implementation**: Retrieval Augmented Generation using Pinecone
- 🔐 **Secure Authentication**: JWT-based API authentication
- 📊 **Comprehensive Logging**: Detailed interaction and system logs
- 🔄 **Extensible Design**: Easy to add new specialized nodes
- 🚀 **REST API**: Full REST API for mobile app integration

## Technology Stack

- **Python 3.13+**
- **FastAPI** - Web framework
- **LangGraph** - Agentic AI implementation
- **OpenAI GPT-4.0** - Natural language processing
- **Pinecone** - Vector database for RAG
- **JWT** - Authentication
- **Uvicorn** - ASGI server

## Project Structure

```
MynaAPI/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config/                 # Configuration management
│   ├── auth/                   # Authentication system
│   ├── agents/                 # LangGraph agents and nodes
│   ├── services/               # External service integrations
│   ├── models/                 # Pydantic models
│   └── utils/                  # Utility functions
├── tests/                      # Unit tests
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── Design.txt                  # Detailed architecture documentation
```

## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd MynaAPI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_HOST=your_pinecone_host
PINECONE_INDEX=your_pinecone_index
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 3. Run the Application

```bash
# Run with Python
python run.py

# Or run with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 4. Local Development with Docker

```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your actual API keys

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f mynaapi

# Stop services
docker-compose down
```

## 🚀 Deployment

### Azure Container Apps (Recommended)

The application is designed for deployment on Azure Container Apps with full CI/CD integration.

#### Quick Deployment

1. **Fork this repository** to your GitHub account

2. **Set up GitHub Secrets** in your repository:
   ```
   AZURE_CREDENTIALS           # Azure service principal JSON
   AZURE_ACR_USERNAME          # Container registry username  
   AZURE_ACR_PASSWORD          # Container registry password
   OPENAI_API_KEY              # Your OpenAI API key
   PINECONE_API_KEY            # Your Pinecone API key
   PINECONE_HOST               # Your Pinecone host URL
   JWT_SECRET_KEY              # Your JWT secret key
   ```

3. **Trigger deployment**:
   - Push to `main` branch for automatic production deployment
   - Use GitHub Actions "Run workflow" for manual deployment

4. **Access your deployed API** at the provided Azure Container Apps URL

#### Manual Deployment

For detailed deployment instructions, see [`deployment/README.md`](deployment/README.md).

```bash
# PowerShell (Windows)
.\deployment\scripts\deploy.ps1 -Environment dev -Action full

# Bash (Linux/macOS)  
./deployment/scripts/deploy.sh dev eastus full
```

#### Deployment Features

- **Auto-scaling**: Scales 1-10 instances based on load
- **Security**: Secrets managed in Azure Key Vault
- **Monitoring**: Application Insights + Log Analytics
- **Health Checks**: Automated health monitoring
- **CI/CD**: GitHub Actions with automated testing
- **Multi-Environment**: Dev, Staging, Production support

### Other Deployment Options

- **Docker**: Use the provided `Dockerfile` for any container platform
- **Azure Container Instances**: For simple single-container deployment
- **Kubernetes**: Deploy to any Kubernetes cluster with provided manifests

## API Endpoints

### Authentication
- `POST /auth/login` - User authentication
- `GET /auth/me` - Get current user info

### Main Service
- `POST /api/v1/query` - Process user queries (requires authentication)
- `GET /health` - Health check
- `GET /api/v1/logs` - Get application logs (admin)

### API Documentation
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Usage Examples

### 1. Authentication

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "secret"}'
```

### 2. Query Processing

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the cutoff for Anna University CSE?", "session_id": "optional"}'
```

## Agent Architecture

### Router Node
- Entry point for all queries
- Analyzes intent using GPT-4.0
- Routes to appropriate specialized nodes

### TNEA Node
- Handles Tamil Nadu Engineering Admissions queries
- Implements RAG using Pinecone vector database
- Provides cutoff marks and college recommendations

### Future Node
- Handles queries not yet implemented
- Provides helpful responses about future features
- Easily extensible for new domains

## Development

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_auth
```

### Adding New Nodes

1. Create new node class in `app/agents/nodes/`
2. Implement the `process()` method
3. Add node to the graph in `app/agents/graph.py`
4. Update routing logic in router node

### Environment Variables

Key environment variables:
- `OPENAI_API_KEY`: OpenAI API key for GPT-4.0
- `PINECONE_API_KEY`: Pinecone API key for vector database
- `PINECONE_HOST`: Pinecone index host URL
- `PINECONE_INDEX`: Pinecone index name
- `JWT_SECRET_KEY`: Secret key for JWT tokens

## Logging

The system provides comprehensive logging:
- **Application logs**: `logs/app.log`
- **Interaction logs**: `logs/interactions.log`

Log entries include:
- User queries and responses
- Intent analysis results
- Node routing decisions
- RAG retrieval information
- Error tracking

## Deployment

### Production Considerations

1. **Environment Variables**: Use production values
2. **Database**: Replace fake user database with real database
3. **Security**: Implement proper CORS, rate limiting
4. **Monitoring**: Add health checks and metrics
5. **Scaling**: Consider containerization with Docker

### Docker Deployment (Future)

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the `Design.txt` file for detailed architecture
- Review API documentation at `/docs`
- Check application logs for debugging

## Roadmap

- [ ] Add more educational domains (Medical, Arts, Commerce)
- [ ] Implement real user database
- [ ] Add caching layer
- [ ] Enhance RAG with better embeddings
- [ ] Add analytics and metrics
- [ ] Mobile app SDK

---

Built with ❤️ for helping students achieve their educational goals.
