# Product Q&A Agent Architecture

## Overview

This document outlines the recommended architecture for an AI model that answers product-related questions using LangGraph, agents, and MCP (Model Context Protocol). The system prioritizes information from a pre-existing vector database corpus while leveraging MCP for additional context.

## Core Components

### LangGraph Workflow Structure

The system uses a state-based graph with the following nodes:

1. **Entry Node**: Receives and initializes user queries
2. **Router Agent**: Determines if corpus retrieval is needed and routes the query appropriately
3. **RAG Retrieval Node**: Searches the vector database for relevant information
4. **MCP Integration Node**: Handles external tools/context via MCP protocol
5. **Synthesis Agent**: Combines retrieved information and MCP context intelligently
6. **Response Generation Node**: Produces final answers with corpus data prioritized

## Prioritization Strategy

### Tiered Information Hierarchy

The system implements a three-tier information hierarchy:

1. **Tier 1 (Highest Priority)**: Direct matches from the vector database corpus
   - Highest confidence scores
   - Explicit product information
   - Verified knowledge base content

2. **Tier 2 (Medium Priority)**: MCP-provided context and real-time data
   - External API data
   - Real-time inventory/availability
   - Dynamic information sources

3. **Tier 3 (Lowest Priority)**: Fallback LLM knowledge
   - Only used when corpus and MCP sources are insufficient
   - General product knowledge
   - Inferred information

## Technical Stack Recommendations

### Vector Database
- **Primary**: Qdrant (based on project requirements)
- Alternatives considered: Pinecone, Weaviate, Chroma, FAISS

### LangGraph Components
- `StateGraph` for managing agent state
- Conditional edges for routing based on confidence scores
- Checkpoints for conversation history management
- State persistence for multi-turn conversations

### MCP Integration
- MCP servers for external tools (databases, APIs, file systems)
- Protocol handlers for structured context injection
- Standardized interfaces for context retrieval

### Additional Dependencies
- Embedding models (OpenAI, Cohere, or local)
- LLM provider for agents (OpenAI, Anthropic, or local)
- Python libraries: langgraph, langchain, qdrant-client

## Architecture Flow

```
User Query
    ↓
Router Agent (analyzes query intent & confidence)
    ↓
    ├─→ [High confidence → needs corpus] → Vector DB Retrieval
    │                                       ↓
    │                                   RAG Context Builder
    │                                       ↓
    │                                   Score & Rank Results
    │                                       ↓
    └─→ [Low confidence/needs external] → MCP Context Retrieval
                                              ↓
                                    Information Synthesis Agent
                                              ↓
                                    Priority Filter (corpus > MCP > LLM)
                                              ↓
                                    Response Generation
                                              ↓
                                    Source Attribution
                                              ↓
                                    Final Answer
```

## Implementation Structure

```
maya/
├── agents/
│   ├── router_agent.py      # Determines query routing strategy
│   ├── rag_agent.py         # Handles vector DB retrieval
│   ├── mcp_agent.py         # MCP integration and context retrieval
│   └── synthesis_agent.py   # Combines information sources intelligently
├── graph/
│   └── product_qa_graph.py  # Main LangGraph workflow definition
├── retrieval/
│   ├── vector_store.py      # Vector DB interface and abstraction
│   └── embeddings.py        # Embedding generation utilities
├── mcp/
│   ├── mcp_client.py        # MCP protocol client implementation
│   └── mcp_servers.py       # MCP server configurations
├── prompts/
│   ├── router_prompt.py     # Router agent prompting templates
│   ├── synthesis_prompt.py  # Synthesis agent prompting templates
│   └── response_prompt.py   # Response generation prompting templates
├── config/
│   └── settings.py          # Configuration management and environment variables
├── schemas/
│   └── state.py             # LangGraph state schema definitions
└── main.py                  # Application entry point
```

## Prioritization Implementation Details

### Scoring Mechanism

1. **Corpus Results Scoring**:
   - Relevance score from vector similarity search
   - Confidence score based on match quality
   - Metadata-based relevance (e.g., product category match)

2. **Prompt-Level Prioritization**:
   - Explicit instructions to synthesis agent: "When corpus information is available, prioritize it over other sources"
   - Weighted context injection (corpus > MCP > LLM knowledge)
   - Clear source hierarchy in prompt templates

3. **Response Formatting**:
   - Source attribution in responses
   - Confidence indicators
   - Transparency about information sources

## MCP Integration Points

Potential MCP server integrations:

- **Product Inventory**: Real-time stock and availability
- **Pricing Information**: Current pricing and promotions
- **Customer Support Data**: Historical support interactions
- **External Knowledge Bases**: Additional product information sources
- **Analytics**: Product performance metrics
- **File Systems**: Additional documentation access

## Key Design Decisions Needed

### Vector Database
- ✅ Qdrant (confirmed)
- Collection structure and organization
- Embedding model compatibility

### Embedding Model
- Which model for corpus embeddings? (OpenAI, Cohere, local)
- Model version and dimensions
- Consistency between indexing and querying

### LLM Provider
- For agent reasoning (OpenAI, Anthropic, local)
- Model selection for different agent roles
- API key management

### MCP Servers
- Which tools/context sources to integrate
- MCP server endpoints
- Authentication requirements

### Retrieval Strategy
- Top-k results count (e.g., 5, 10, 20)
- Reranking approach (if any)
- Hybrid search configuration (sparse + dense)
- Score thresholds

### Corpus Metadata
- Available filter fields
- Product categorization structure
- Temporal information handling

## State Management

### LangGraph State Schema

```python
{
    "query": str,                    # Original user query
    "routing_decision": str,         # Router agent decision
    "corpus_results": List[Dict],    # Vector DB retrieval results
    "mcp_context": Dict,             # MCP-provided context
    "synthesized_context": Dict,     # Combined information
    "final_answer": str,             # Generated response
    "sources": List[str],            # Source attribution
    "confidence": float,             # Overall confidence score
    "conversation_history": List     # Multi-turn conversation context
}
```

## Error Handling & Fallbacks

1. **Vector DB Unavailable**: Fallback to MCP and LLM knowledge
2. **Low Confidence Scores**: Request clarification or indicate uncertainty
3. **No Relevant Results**: Graceful degradation to general knowledge
4. **MCP Timeout**: Continue with corpus results only

## Performance Considerations

- Response time targets
- Caching strategies for frequent queries
- Batch processing capabilities
- Concurrent request handling

## Security & Privacy

- API key management
- Data privacy for product information
- Access control for corpus data
- Audit logging

## Next Steps

1. Collect Qdrant integration details (see `QDRANT_INTEGRATION.md`)
2. Confirm embedding model and LLM provider choices
3. Define MCP server requirements
4. Implement core retrieval and agent logic
5. Build and test LangGraph workflow
6. Iterate on prioritization and synthesis logic

