# Azure AI Foundry Agent Service: OpenAPI tool
This repo demonstrates how to use an *OpenAPI-specified API* as a tool for an AI agent in the **Azure AI Foundry Agent Service**. The solution includes a mock FastAPI backend with API key authentication that the agent can query for product inventory data.

The provided Jupyter notebook, `Agent_OpenAPITool.ipynb`, shows the complete end-to-end setup: from testing the backend API to creating and interacting with the agent.

> [!Note]
> The OpenAPI tool requires each operation to have an `operationId`. The API key is securely stored in an Azure project connection and passed automatically by the Agent Service.

## 📑 Table of Contents:
- [Part 1: Configuring the Environment](#part-1-configuring-the-environment)
- [Part 2: Backend API Implementation](#part-2-backend-api-implementation)
- [Part 3: Agent Configuration and Execution](#part-3-agent-configuration-and-execution)

## Part 1: Configuring the Environment

### 1.1. Prerequisites
You need:
- An *Azure AI Foundry* project with a deployed model (e.g., gpt-4.1),
- Python 3.10+ with FastAPI and uvicorn installed.

### 1.2. Project Connection for API Key
Create a project connection in Azure AI Foundry to store the API key:
1. Go to **Management Center** → **Connected Resources** → **Add Connection**
2. Select **Custom Keys** type
3. Configure:
   - **Name**: `product-inventory-api`
   - **Key**: `x-api-key`
   - **Value**: `test-api-key-12345`

### 1.3. Environment Variables
The Jupyter notebook uses the following variables:

| Variable | Description |
| --- | --- |
| `AZURE_AI_PROJECT_ENDPOINT` | Your Azure AI Foundry project endpoint URL |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | Deployed model name (e.g., gpt-4o) |
| `OPENAPI_CONNECTION_NAME` | Name of the project connection storing the API key |

### 1.4. Required Libraries
Install the necessary Python packages:
```bash
pip install azure-ai-projects azure-identity jsonref requests fastapi uvicorn
```

## Part 2: Backend API Implementation

### 2.1. Starting the Backend
Run the FastAPI backend service:
```bash
uvicorn product_inventory_api:app --reload --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

**Test API Key**: `test-api-key-12345`

### 2.2. API Endpoints
The backend provides read-only access to mock product inventory:

| Endpoint | Description |
| --- | --- |
| `GET /products` | List all products (filter by category, stock_status) |
| `GET /products/{id}` | Get specific product details |
| `GET /inventory/summary` | Get inventory totals and statistics |
| `GET /inventory/alerts` | Get low stock and out of stock items |

### 2.3. Testing the API
```bash
# Health check (no auth)
curl http://localhost:8000/

# List products (requires API key)
curl -H "x-api-key: test-api-key-12345" http://localhost:8000/products

# Get inventory summary
curl -H "x-api-key: test-api-key-12345" http://localhost:8000/inventory/summary
```

## Part 3: Agent Configuration and Execution

### 3.1. OpenAPI Specification
The `product_inventory_openapi.json` file defines the API schema for the agent. Key requirements:
- Every operation has an `operationId` (e.g., `listProducts`, `getProduct`)
- Security scheme defines API key authentication via `x-api-key` header
- Descriptive summaries help the LLM choose the correct operation

### 3.2. Defining the Tool
The OpenAPI tool is configured with project connection authentication:
```python
openapi_tool = {
    "type": "openapi",
    "openapi": {
        "name": "product_inventory",
        "description": "Query product inventory data, check stock levels, and get alerts.",
        "spec": openapi_spec,
        "auth": {
            "type": "project_connection",
            "security_scheme": {
                "project_connection_id": connection_id
            }
        },
    }
}
```

### 3.3. Agent Creation
```python
agent = project_client.agents.create_version(
    agent_name="InventoryAgent",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="You are an inventory assistant...",
        tools=[openapi_tool],
    ),
)
```

### 3.4. Sample Interactions
Once created, you can ask the agent questions like:
- *"What products do you have?"*
- *"Show me the inventory summary."*
- *"Are there any stock alerts?"*
- *"Tell me about product PROD-001."*
- *"What electronics do you have?"*

The agent will use the OpenAPI tool to call the appropriate endpoint and return the results.
