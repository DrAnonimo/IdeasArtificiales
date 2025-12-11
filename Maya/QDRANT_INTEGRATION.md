# Qdrant Vector Database Integration Details

This document outlines the information needed to properly integrate Qdrant into the LangGraph agent system.

## Essential Information Required

### 1. Connection Details

Please provide the following connection information:

- [ ] **Deployment Type**: 
  - [ ] Qdrant Cloud
  - [ ] Local instance
  - [ ] Self-hosted

- [ ] **Connection URL/Endpoint**: 
  - Example: `https://xxx-xxx-xxx.us-east.aws.cloud.qdrant.io` (Cloud)
  - Example: `http://localhost:6333` (Local)

- [ ] **Authentication**:
  - [ ] API key: `_________________`
  - [ ] No authentication (local)
  - [ ] Other: `_________________`

- [ ] **Port Number**: 
  - Default: 6333 (if local)

- [ ] **SSL/TLS**: 
  - [ ] Required (Cloud)
  - [ ] Not required (Local)

---

### 2. Collection Structure

#### Collection Configuration

- [ ] **Collection Name(s)**: 
  - Primary collection: `_________________`
  - Additional collections (if any): `_________________`

- [ ] **Vector Dimensions**: 
  - Example: 384, 768, 1536, 3072
  - Your dimension: `_________________`

- [ ] **Distance Metric**: 
  - [ ] Cosine
  - [ ] Euclidean
  - [ ] Dot
  - [ ] Other: `_________________`

#### Payload/Metadata Schema

Please describe the payload structure stored with each vector:

- [ ] **Payload Fields**:
  ```
  Example structure:
  {
    "text": "product description or content",
    "product_id": "unique identifier",
    "category": "product category",
    "timestamp": "date/time",
    ...
  }
  ```

- [ ] **Your Payload Structure**:
  ```
  {
    "field1": "description",
    "field2": "description",
    ...
  }
  ```

- [ ] **Filterable Fields** (for query filtering):
  - List fields used for filtering: `_________________`
  - Example: `["product_id", "category", "date_range"]`

---

### 3. Data Content

- [ ] **Corpus Content Type**: 
  - [ ] Product descriptions
  - [ ] FAQs
  - [ ] Technical specifications
  - [ ] User reviews
  - [ ] Documentation
  - [ ] Support tickets
  - [ ] Other: `_________________`

- [ ] **Collection Organization**: 
  - [ ] Single collection for all data
  - [ ] Multiple collections (per product/category)
  - [ ] Partitioned structure
  - [ ] Other: `_________________`

- [ ] **Approximate Vector Count**: 
  - Number of vectors: `_________________`
  - Example: 10,000; 100,000; 1,000,000+

---

### 4. Embedding Model

- [ ] **Embedding Model Used**: 
  - Model name: `_________________`
  - Examples: 
    - OpenAI: `text-embedding-3-small`, `text-embedding-3-large`
    - Cohere: `embed-english-v3.0`
    - Local: `all-MiniLM-L6-v2`, `sentence-transformers/all-mpnet-base-v2`

- [ ] **Model Provider**: 
  - [ ] OpenAI
  - [ ] Cohere
  - [ ] Hugging Face (local)
  - [ ] Other: `_________________`

- [ ] **Model Version**: 
  - Version: `_________________`

- [ ] **Query-Time Consistency**: 
  - [ ] Will use the same model for queries
  - [ ] Different model for queries: `_________________`

---

### 5. Retrieval Preferences

#### Search Configuration

- [ ] **Top-K Results**: 
  - Number of results to retrieve: `_________________`
  - Suggested: 5-20 (typical range)

- [ ] **Score Threshold**: 
  - Minimum similarity score: `_________________`
  - Example: 0.7 (for cosine similarity)
  - [ ] No threshold (retrieve all top-k)

- [ ] **Search Strategy**: 
  - [ ] Vector similarity only
  - [ ] Hybrid search (sparse + dense)
  - [ ] Custom scoring

#### Filtering Preferences

- [ ] **Common Filters**: 
  - Product categories: `_________________`
  - Date ranges: `_________________`
  - Product status: `_________________`
  - Other filters: `_________________`

- [ ] **Filter Application**: 
  - [ ] Always apply certain filters
  - [ ] Filter dynamically based on query
  - [ ] No filters

---

## Optional but Helpful Information

### Sample Data Structure

Please provide a sample payload structure if available:

```json
{
  "example_payload": {
    "field1": "example_value",
    "field2": "example_value"
  }
}
```

### Existing Query Patterns

- [ ] Do you have existing query code/patterns? 
  - [ ] Yes, will share
  - [ ] No, starting fresh

- [ ] Preferred query method:
  - [ ] Python client (qdrant-client)
  - [ ] REST API
  - [ ] gRPC

### Update Requirements

- [ ] **Real-time Updates**: 
  - [ ] Corpus is static (pre-indexed)
  - [ ] Updates needed during runtime
  - [ ] Update frequency: `_________________`

### Performance Requirements

- [ ] **Latency Expectations**: 
  - Target query time: `_________________` ms
  - Example: <100ms, <500ms

- [ ] **Concurrent Query Handling**: 
  - Expected concurrent users: `_________________`
  - Peak load: `_________________`

---

## Configuration Template

Once filled out, this will be used in `config/settings.py`:

```python
QDRANT_CONFIG = {
    "url": "YOUR_QDRANT_URL",
    "api_key": "YOUR_API_KEY",  # Optional for local
    "collection_name": "YOUR_COLLECTION_NAME",
    "vector_size": YOUR_VECTOR_DIMENSION,
    "distance": "Cosine",  # or "Euclidean", "Dot"
    "top_k": YOUR_TOP_K_VALUE,
    "score_threshold": YOUR_THRESHOLD,  # Optional
}

EMBEDDING_CONFIG = {
    "model": "YOUR_EMBEDDING_MODEL",
    "provider": "YOUR_PROVIDER",
    "dimensions": YOUR_VECTOR_DIMENSION,
}
```

---

## Notes

- Mark checkboxes as you fill in the information
- Replace placeholder text (indicated by `_________________`) with actual values
- If certain details are unknown, we can design with reasonable defaults
- All information will be used to create a properly configured integration

---

## Questions?

If you're unsure about any of these details:

1. **Vector dimensions**: Check your embedding model documentation or collection settings
2. **Distance metric**: Typically Cosine for semantic similarity, but verify collection configuration
3. **Payload structure**: Inspect a sample document from your corpus or collection schema
4. **Connection details**: Available in Qdrant Cloud dashboard or local configuration

For local Qdrant instances, you can check connection details in:
- Docker compose files
- Configuration files
- Qdrant service logs

