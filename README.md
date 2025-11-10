# Unified Strands Agents API

A comprehensive FastAPI application demonstrating the complete **Strands Agents SDK** ecosystem, consolidating all three educational labs into a unified, production-ready platform. Based on the official [Strands Agents Samples](https://github.com/strands-agents/samples/tree/main/02-samples/11-personal-finance-assistant).

> ⚠️ **EDUCATIONAL PURPOSE ONLY**: This application demonstrates AI agent capabilities for financial analysis. This is NOT financial advice. All analysis should be verified against expert advice.

## 🎯 Unified Architecture

This project consolidates all three Strands Agents labs into a single, cohesive platform that demonstrates:

### 🤖 Agent Types
- **Basic Agent**: Simple conversational AI
- **Financial Agent**: Finance-focused assistance
- **Memory Agent**: Agents with persistent memory (mem0)
- **Budget Agent**: Budget analysis with visualization tools
- **Portfolio Orchestrator**: Multi-agent coordination system

### 🛠️ Key Features
- **Memory Integration**: Short-term (conversation) and long-term (mem0) memory
- **Custom Tools**: Budget calculation, financial visualization, data analysis
- **Multi-Agent Orchestration**: Specialist agents for portfolio management
- **Unified API**: Clean endpoints without lab-specific prefixes
- **Flexible Configuration**: Support for multiple memory backends

### 🏗️ Architecture

```
Unified FastAPI Application
├── UnifiedAgentService (Core Service)
│   ├── Agent Lifecycle Management
│   ├── Memory Operations (mem0)
│   ├── Custom Tools & Visualizations
│   └── Multi-Agent Orchestration
│
├── API Routes (Unified Endpoints)
│   ├── Chat & Conversation
│   ├── Memory Management
│   ├── Budget Analysis
│   ├── Portfolio Orchestration
│   └── Agent State Management
│
└── Shared Infrastructure
    ├── Configuration & Settings
    ├── Pydantic Models
    └── Utility Functions
```

## 🏗️ Architecture

```
FastAPI Application
├── Lab 1: Foundations
│   ├── Basic Agent Creation
│   ├── Custom Tools (@tool decorator)
│   ├── Budget Calculation
│   ├── Visualization Tools
│   └── AWS Bedrock Guardrails
│
├── Lab 2: Memory Integration
│   ├── Conversation History (Sliding Window)
│   ├── Agent State Management
│   ├── Request State
│   ├── Long-term Memory (mem0)
│   └── Personalized Responses
│
└── Lab 3: Multi-Agent Orchestration
    ├── Stock Data Agent
    ├── Growth Strategy Agent
    ├── Diversified Strategy Agent
    ├── Performance Calculator Agent
    ├── Visualization Agent
    ├── Validation Agent
    └── Portfolio Orchestrator
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- AWS Account with Bedrock access
- AWS credentials configured

### Installation

```bash
# Clone the repository
cd strands

# Install dependencies using uv
uv sync

# Create .env file
cp .env.example .env

# Configure your .env file with AWS credentials
```

### Environment Variables

Create a `.env` file in the project root:

```env
# AWS Configuration
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0

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

```bash
# Development mode with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

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

## 🎯 Usage Examples

### Chat with Different Agent Types

```bash
# Financial advice agent
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are some good budgeting strategies?",
    "user_id": "user123",
    "session_id": "financial"
  }'

# Memory-enabled agent
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Remember that I want to save 30% for retirement",
    "user_id": "user123",
    "session_id": "memory"
  }'

# Budget analysis agent
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me create a budget with $5000 monthly income",
    "user_id": "user123",
    "session_id": "budget"
  }'

# Portfolio orchestrator
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a diversified portfolio for moderate risk",
    "user_id": "user123",
    "session_id": "orchestrator"
  }'
```

### Budget Analysis

```bash
# Calculate 50/30/20 budget
curl -X POST "http://localhost:8000/api/v1/budget/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_income": 5000
  }'

# Create budget visualization
curl -X POST "http://localhost:8000/api/v1/budget/chart" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "Housing": 1500,
      "Food": 600,
      "Transportation": 400,
      "Savings": 1000
    },
    "title": "Monthly Budget Breakdown"
  }'
```

### Memory Operations

```bash
# Store user preferences
curl -X POST "http://localhost:8000/api/v1/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "content": "User prefers aggressive investment strategies with 70% stocks, 30% bonds"
  }'

# Retrieve relevant memories
curl -X POST "http://localhost:8000/api/v1/memory/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "query": "investment preferences",
    "max_results": 3
  }'
```

### Portfolio Orchestration

```bash
# Run complete portfolio analysis
curl -X POST "http://localhost:8000/api/v1/portfolio/orchestrate" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Create an optimal portfolio for retirement with moderate risk tolerance"
  }'

# Get visualizations
curl -X GET "http://localhost:8000/api/v1/portfolio/visualizations"
```

## 🏗️ Key Concepts
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

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.115.6
- **AI SDK**: Strands Agents SDK
- **AI Model**: AWS Bedrock (Claude 3.7 Sonnet)
- **Memory**: mem0ai, FAISS, OpenSearch (optional)
- **Data Analysis**: pandas, numpy
- **Visualization**: matplotlib
- **Financial Data**: yfinance
- **Python**: 3.13+
- **Package Manager**: uv

## 📖 API Documentation

### Interactive Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example Requests

#### Lab 1: Basic Chat
```bash
curl -X POST "http://localhost:8000/api/v1/lab1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I make $6000 per month. Can you create a budget breakdown?"
  }'
```

#### Lab 2: Store Memory
```bash
curl -X POST "http://localhost:8000/api/v1/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "content": "My monthly budget is $5000. I prefer to save 30%."
  }'
```

#### Lab 2: Chat with Memory
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my savings goals?",
    "user_id": "user_123"
  }'
```

#### Lab 3: Portfolio Orchestration
```bash
curl -X POST "http://localhost:8000/api/v1/lab3/orchestrate" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Create an optimal investment portfolio using your multi-agent system",
    "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
    "investment_amount": 1000
  }'
```

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
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API route definitions
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Application settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Lab 2 schemas
│   │   └── lab1_schemas.py     # Lab 1 schemas
│   └── services/
│       ├── __init__.py
│       ├── agent_service.py    # Lab 2 service
│       ├── lab1_service.py     # Lab 1 service
│       ├── lab3_service.py     # Lab 3 service
│       └── lab3_utils.py       # Lab 3 utilities
├── tests/                      # Test files
├── docs/                       # Additional documentation
├── .env.example                # Example environment variables
├── pyproject.toml              # Project dependencies (uv)
├── README.md                   # This file
└── requirements.txt            # Legacy pip requirements
```

## 🔐 AWS Bedrock Guardrails (Lab 1)

Lab 1 demonstrates how to integrate AWS Bedrock Guardrails for safety:

### Creating a Guardrail

```python
import boto3

bedrock_client = boto3.client('bedrock')

response = bedrock_client.create_guardrail(
    name='guardrail-no-investment-advice',
    description='Prevents stock investment advice',
    topicPolicyConfig={
        'topicsConfig': [{
            'name': 'Stock Investment Advice',
            'definition': 'Providing personalized investment advice...',
            'type': 'DENY'
        }]
    }
)

guardrail_id = response['guardrailId']
```

### Using with Strands Agent

```python
from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    guardrail_id=guardrail_id,
    guardrail_version="DRAFT"
)

agent = Agent(model=model, tools=[...])
```

## 💾 Memory Backends (Lab 2)

Lab 2 supports three memory backends:

### 1. FAISS (Default - Local Development)
```env
MEMORY_BACKEND=faiss
```
No additional configuration needed. Uses local vector storage.

### 2. OpenSearch (AWS Recommended)
```env
MEMORY_BACKEND=opensearch
OPENSEARCH_HOST=your-opensearch-endpoint
AWS_REGION=us-west-2
```

### 3. Mem0 Platform
```env
MEMORY_BACKEND=mem0_platform
MEM0_API_KEY=your_mem0_api_key
```

## 🤝 Multi-Agent Pattern (Lab 3)

Lab 3 demonstrates the "agents as tools" pattern:

```python
# Create specialist agents
stock_data_agent = create_stock_data_agent()
growth_strategy_agent = create_growth_strategy_agent()
diversified_strategy_agent = create_diversified_strategy_agent()

# Create orchestrator that uses specialists as tools
orchestrator = Agent(
    system_prompt="Coordinate specialist agents...",
    tools=[
        stock_data_agent,
        growth_strategy_agent,
        diversified_strategy_agent
    ]
)

# Orchestrator automatically delegates to specialists
result = orchestrator("Create an optimal portfolio")
```

## 🎓 Learning Path

1. **Start with Lab 1**: Learn basic agent creation and custom tools
2. **Progress to Lab 2**: Add memory capabilities for personalization
3. **Master Lab 3**: Coordinate multiple specialist agents

Each lab builds on concepts from the previous one, creating a comprehensive understanding of Strands Agents patterns.

## 📝 Key Takeaways

### From Lab 1:
- Agent creation with AWS Bedrock
- Custom tool development with `@tool`
- System prompt engineering
- Safety filters with Guardrails

### From Lab 2:
- Three types of short-term memory
- Long-term memory with mem0
- Conversation management patterns
- User preference persistence

### From Lab 3:
- Multi-agent coordination patterns
- Specialist agent design
- Orchestrator implementation
- Human-in-the-loop workflows
- Real-world portfolio analysis

## 🔗 Resources

- [Strands Agents Documentation](https://strandsagents.ai/docs)
- [Strands Agents SDK (Python)](https://github.com/strands-agents/sdk-python)
- [Strands Agents Samples](https://github.com/strands-agents/samples)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📄 License

This project is for educational purposes, based on the Strands Agents samples.

## 🙏 Acknowledgments

- Strands Agents team for the excellent SDK and samples
- AWS for Bedrock AI services
- FastAPI team for the amazing web framework

---

**Built with ❤️ for learning Strands Agents patterns through practical examples**