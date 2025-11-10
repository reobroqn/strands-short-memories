# Unified Strands Agents API

A comprehensive FastAPI application demonstrating the complete **Strands Agents SDK** ecosystem, consolidating all three educational labs into a unified, production-ready platform. Based on the official [Strands Agents Samples](https://github.com/strands-agents/samples/tree/main/02-samples/11-personal-finance-assistant).

> [WARNING] **EDUCATIONAL PURPOSE ONLY**: This application demonstrates AI agent capabilities for financial analysis. This is NOT financial advice. All analysis should be verified against expert advice.

## [TARGET] Unified Architecture

This project consolidates all three Strands Agents labs into a single, cohesive platform that demonstrates:

### [AI] Agent Types
- **Basic Agent**: Simple conversational AI
- **Financial Agent**: Finance-focused assistance
- **Memory Agent**: Agents with persistent memory (mem0)
- **Budget Agent**: Budget analysis with visualization tools
- **Portfolio Orchestrator**: Multi-agent coordination system

### [TOOLS] Key Features
- **Memory Integration**: Short-term (conversation) and long-term (mem0) memory
- **Custom Tools**: Budget calculation, financial visualization, data analysis
- **Multi-Agent Orchestration**: Specialist agents for portfolio management
- **Unified API**: Clean endpoints without lab-specific prefixes
- **Flexible Configuration**: Support for multiple memory backends

### [STRUCTURE] Architecture

```
Unified FastAPI Application
├── Services Layer
│   ├── Agent Manager - Strands SDK integration
│   ├── Memory Service - Long-term memory with mem0
│   └── Utils - Data analysis and utilities
│
├── API Layer
│   ├── Chat & Conversation endpoints
│   ├── Memory Management endpoints
│   ├── Budget Analysis endpoints
│   └── System Health endpoints
│
└── Configuration
    ├── Environment settings (Google Gemini)
    ├── Pydantic models
    └── Application startup
```

## [START] Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Gemini API key (get one at [Google AI Studio](https://aistudio.google.com/app/apikey))

### Installation

```bash
# Clone the repository
cd strands

# Install dependencies using uv
uv sync

# Create .env file
cp .env.example .env

# Configure your .env file with Google Gemini API key
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_ID=gemini-2.0-flash-exp

# Memory Backend (Lab 2)
MEMORY_BACKEND=faiss  # Options: faiss, opensearch, mem0_platform

# Optional: Mem0 Platform
# MEM0_API_KEY=your_mem0_api_key

# Optional: OpenSearch
# OPENSEARCH_HOST=your_opensearch_host

# Application Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Running the Application

#### Option 1: FastAPI CLI (Recommended)

```bash
# Development mode with auto-reload and debugging
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000

# Production mode with optimized settings
uv run fastapi run app/main.py --host 0.0.0.0 --port 8000 --workers 4
```

#### Option 2: Project Scripts (After Installation)

```bash
# Install in development mode first
uv pip install -e .

# Then use convenient shortcuts
strands-dev     # Development server
strands-prod    # Production server  
strands-start   # Development server (alias)
```

**Key Benefits of FastAPI CLI over uvicorn:**
- **Built-in production features**: Automatic worker management, SSL handling, process monitoring
- **Performance optimizations**: Pre-configured for production workloads
- **Standardized commands**: Consistent with FastAPI ecosystem and best practices
- **Future-proof**: Aligned with FastAPI development direction

Access the API:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## 📚 API Endpoints

### Chat & Agents
- `POST /api/v1/chat` - Interact with any agent type (basic, financial, memory, budget, orchestrator)
- `GET /api/v1/agent/state/{user_id}` - Get agent state information
- `GET /api/v1/agent/history/{user_id}` - Get conversation history
- `POST /api/v1/agent/reset/{user_id}` - Reset all agents for user
- `POST /api/v1/preferences/initialize` - Initialize user preferences

### Memory Management
- `POST /api/v1/memory/store` - Store information in long-term memory
- `POST /api/v1/memory/retrieve` - Semantic search through memories
- `GET /api/v1/memory/list/{user_id}` - List all stored memories

### Budget & Financial Analysis
- `POST /api/v1/budget/calculate` - Calculate 50/30/20 budget breakdown
- `POST /api/v1/budget/chart` - Create financial visualizations
- `GET /api/v1/budget/sample-data` - Generate sample spending data

### Portfolio Orchestration
- `POST /api/v1/portfolio/orchestrate` - Run multi-agent portfolio analysis
- `GET /api/v1/portfolio/visualizations` - Get cached charts and graphs
- `GET /api/v1/portfolio/data` - Get cached portfolio data
- `DELETE /api/v1/portfolio/cache` - Clear all cached data

### System
- `GET /api/v1/health` - Health check and system status

## [USAGE] Usage

### Interactive API Documentation

Once the application is running, visit the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The interactive documentation provides a clean interface to explore all available endpoints, view request/response schemas, and test the API directly in your browser.

## [CONCEPTS] Key Concepts
- **Conversation History**: Managed by `SlidingWindowConversationManager`
- **Agent State**: Key-value storage for user preferences
- **Request State**: Per-request context
- **Long-term Memory**: Persistent storage with mem0

**Endpoints:**
- `POST /api/v1/chat` - Chat with memory-enabled agent
- `POST /api/v1/memory/store` - Store information in memory
- `POST /api/v1/memory/retrieve` - Retrieve relevant memories
- `GET /api/v1/memory/list/{user_id}` - List all user memories
- `GET /api/v1/agent/state/{user_id}` - Get agent state
- `GET /api/v1/agent/history/{user_id}` - Get conversation history
- `POST /api/v1/preferences/initialize` - Initialize user preferences

### Lab 3: Multi-Agent Orchestration

**Learning Objectives:**
- Implement multi-agent coordination using "agents as tools" pattern
- Create specialist agents with focused responsibilities
- Build a portfolio orchestrator coordinating multiple agents
- Enable human-in-the-loop decision making
- Validate AI recommendations against actual data

**Key Concepts:**
- **Agents as Tools**: Specialist agents used by orchestrator
- **Portfolio Orchestrator**: Master agent coordinating specialists
- **Stock Data Agent**: Fetches and analyzes market data
- **Strategy Agents**: Create growth and diversified portfolios
- **Performance Calculator**: Projects concrete investment returns
- **Visualization Agent**: Creates professional charts
- **Validation Agent**: Tests against actual market data

**Endpoints:**
- `POST /api/v1/lab3/orchestrate` - Run full portfolio orchestration
- `POST /api/v1/lab3/portfolio/growth` - Create growth portfolio
- `POST /api/v1/lab3/portfolio/diversified` - Create diversified portfolio
- `GET /api/v1/lab3/visualizations` - Get cached visualizations
- `POST /api/v1/lab3/validate` - Validate portfolio performance

## [TECH] Technology Stack

- **Framework**: FastAPI (modern ASGI framework with built-in CLI)
- **AI SDK**: Strands Agents SDK (v1.15.0+)
- **AI Model**: Google Gemini (gemini-2.0-flash-exp)
- **Memory**: mem0ai with FAISS backend (local vector similarity search)
- **Financial Data**: yfinance for market data and analysis
- **Code Quality**: Ruff (linting and formatting)
- **Python**: 3.13+
- **Package Manager**: uv (recommended for FastAPI projects)

## 📖 API Documentation

### Interactive Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing the API

Use the interactive documentation at http://localhost:8000/docs to test all endpoints with a user-friendly interface.

## 🧪 Testing

Run tests using pytest:

```bash
# Run all tests
uv run pytest

# Run specific lab tests
uv run pytest tests/test_lab1.py
uv run pytest tests/test_lab2.py
uv run pytest tests/test_lab3.py

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

## 📁 Project Structure

```
strands/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route definitions
│   │   ├── __init__.py
│   │   ├── system_routes.py    # Health check endpoints
│   │   ├── chat_routes.py      # Chat endpoints
│   │   ├── memory_routes.py    # Memory management endpoints
│   │   └── budget_routes.py    # Budget analysis endpoints
│   ├── config/
│   │   ├── __init__.py
│   │   ├── prompts.py          # System prompts for agents
│   │   └── settings.py         # Application settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic models
│   │   ├── memory_schemas.py   # Memory-related models
│   │   └── portfolio_schemas.py # Portfolio models
│   └── services/
│       ├── __init__.py
│       └── agent_manager.py    # Strands agent management with centralized prompts
├── scripts/
│   └── run.py                  # Development scripts for convenience
├── Makefile                    # Development commands (if make is available)
├── .env.example                # Example environment variables
├── pyproject.toml              # Project dependencies and configuration with start scripts
└── README.md                   # This file
```

## [SECURITY] Security Considerations

This application includes several security features:

- **Input Validation**: All API requests are validated using Pydantic models
- **Error Handling**: Graceful error responses without exposing sensitive information
- **Educational Purpose**: Clear disclaimers that this is not financial advice
- **API Key Management**: Environment variables for secure credential handling

## [MEMORY] Memory Backends

### FAISS (Default - Local Vector Similarity Search)

FAISS (Facebook AI Similarity Search) is a library for efficient similarity search and clustering of dense vectors. It provides:

- **In-memory vector storage** with extremely fast search algorithms
- **CPU optimized performance** (faiss-cpu variant)
- **No external dependencies** - perfect for local development
- **Educational focus** - matches Strands Agents lab requirements

```env
MEMORY_BACKEND=faiss
```

**Why FAISS is Perfect for This Project:**
- ✅ **Local Development**: No database server needed
- ✅ **Single-user Memory**: Ideal for educational applications
- ✅ **Fast Prototyping**: Quick setup, high performance
- ✅ **Lab Compliance**: Matches the Strands Agents notebook approach
- ✅ **Simple Architecture**: Less complexity than full vector databases

### Optional Production Backends

For production scenarios requiring persistence or multi-user support:

**OpenSearch (AWS Recommended)**
```env
MEMORY_BACKEND=opensearch
OPENSEARCH_HOST=your-opensearch-endpoint
AWS_REGION=us-west-2
```

**Mem0 Platform**
```env
MEMORY_BACKEND=mem0_platform
MEM0_API_KEY=your_mem0_api_key
```

## [FEATURES] Key Features

### Agent Management
- **Centralized Prompts**: All system prompts defined in `app/config/prompts.py`
- **Multiple Agent Types**: Basic, financial, memory-enabled, and budget analysis agents
- **Clean Architecture**: AgentManager imports prompts without redefinition
- **Google Gemini Integration**: Modern AI model with natural language understanding

### Memory System
- **FAISS Backend**: Local vector similarity search for educational use
- **Short-term Memory**: Conversation history with sliding window management
- **Long-term Memory**: Persistent storage using mem0 for user preferences and context
- **Lab Compliance**: Matches Strands Agents notebook implementation exactly

### Code Quality
- **Optimized Dependencies**: Removed unnecessary packages (e.g., sentence-transformers)
- **Clean Imports**: Fixed relative import issues and module structure
- **FastAPI CLI**: Modern development and deployment commands
- **Project Scripts**: Convenient command-line shortcuts for common operations

### Financial Analysis
- **Budget Planning**: 50/30/20 budget calculations and recommendations
- **Data Visualization**: Chart preparation for client-side rendering
- **Educational Focus**: Clear disclaimers and non-advisory approach

## [LINKS] Resources

- [Strands Agents Documentation](https://strandsagents.ai/docs)
- [Strands Agents SDK (Python)](https://github.com/strands-agents/sdk-python)
- [Google AI Studio](https://aistudio.google.com/app/apikey) - Get your Gemini API key
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [uv Package Manager](https://docs.astral.sh/uv/)

## [LICENSE] License

This project is for educational purposes, based on the Strands Agents samples.

## [THANKS] Acknowledgments

- Strands Agents team for the excellent SDK and samples
- Google for the Gemini AI models
- FastAPI team for the amazing web framework

---

**Built for learning Strands Agents patterns with modern AI technology**