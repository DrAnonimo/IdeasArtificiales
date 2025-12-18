# CloudBees CI RAG System

A **Retrieval-Augmented Generation (RAG)** system for querying CloudBees CI documentation using a local Ollama model. This system enables support engineers to quickly find answers to CloudBees CI questions by combining semantic search with generative AI.

## 🎯 Overview

This project implements a RAG pipeline that:
1. **Ingests** CloudBees CI documentation from online sources
2. **Indexes** documents using vector embeddings for semantic search
3. **Retrieves** relevant documentation chunks based on user queries
4. **Generates** detailed, source-cited answers using a local LLM

## 🤖 Model Definition

### Primary Model: IBM Granite 4 (350M parameters)

The system uses **`ibm/granite4:350m-h`** via Ollama, a lightweight, efficient model suitable for local deployment:

- **Model Type**: Granite 4 (350M parameters)
- **Deployment**: Local via Ollama
- **Use Case**: Support engineer Q&A with CloudBees CI documentation
- **Advantages**: 
  - Runs entirely locally (privacy-preserving)
  - Fast inference
  - No API costs
  - Works offline

### Embedding Model: Sentence Transformers

For semantic search, the system uses **`all-MiniLM-L6-v2`**:
- Lightweight (80MB)
- Fast inference
- Good semantic understanding for technical documentation
- Generates 384-dimensional embeddings

## 🏗️ Architecture: How RAG Works

### RAG Pipeline Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION PHASE                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  1. Web Scraping (scraper.py)    │
        │     - Crawls CloudBees docs        │
        │     - Extracts HTML content        │
        │     - Cleans and normalizes text   │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  2. Document Chunking (chunker.py)│
        │     - Splits docs into chunks     │
        │     - Size: 1000 chars            │
        │     - Overlap: 200 chars          │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  3. Embedding Generation          │
        │     - Uses SentenceTransformers   │
        │     - Creates vector embeddings    │
        │     - 384-dimensional vectors      │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  4. Vector Storage (ChromaDB)      │
        │     - Stores embeddings + docs    │
        │     - Indexed for fast search      │
        │     - Persistent storage           │
        └───────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    QUERY PHASE                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  1. Query Embedding              │
        │     - User question → embedding   │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  2. Semantic Search (ChromaDB)    │
        │     - Cosine similarity search    │
        │     - Retrieves top-k chunks      │
        │     - Returns: text + metadata    │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  3. Context Building              │
        │     - Merges retrieved chunks     │
        │     - Extracts source metadata    │
        │     - Builds RAG prompt           │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  4. LLM Generation (Ollama)       │
        │     - Model: ibm/granite4:350m-h  │
        │     - Prompt: context + question  │
        │     - Generates detailed answer   │
        │     - Includes inline citations    │
        └───────────────────────────────────┘
                            │
                            ▼
                    User receives answer
                    with source citations
```

### How Information is Included Using RAG

1. **Document Ingestion**:
   - Documentation pages are scraped from `https://docs.cloudbees.com/docs/cloudbees-ci/latest/`
   - Each page is processed to extract clean text content
   - Documents are split into overlapping chunks (1000 chars with 200 char overlap)

2. **Vector Embedding**:
   - Each chunk is converted to a vector embedding using `all-MiniLM-L6-v2`
   - Embeddings capture semantic meaning, not just keywords
   - Similar concepts map to nearby vectors in embedding space

3. **Storage in ChromaDB**:
   - Embeddings are stored in ChromaDB with:
     - Document text
     - Metadata (URL, title, source)
     - Unique IDs
   - ChromaDB uses HNSW (Hierarchical Navigable Small World) index for fast similarity search

4. **Query-Time Retrieval**:
   - User question is embedded using the same model
   - ChromaDB performs cosine similarity search
   - Top-k most relevant chunks are retrieved (default: 8)
   - Retrieved chunks form the "context" for the LLM

5. **Answer Generation**:
   - Retrieved context + user question → prompt for Ollama
   - Model generates detailed answer using the provided context
   - Answer includes inline source citations: `[Source: Title](URL)`
   - Sources section lists all referenced documentation

## 📁 Project Structure

### Core Files (Most Important)

#### 1. **`rag_system.py`** ⭐ **CRITICAL**
   - **Purpose**: Core RAG implementation
   - **Key Components**:
     - `RAGSystem` class: Manages ChromaDB collection and embeddings
     - `add_documents()`: Ingests chunks into vector store (with batching)
     - `search()`: Performs semantic search and retrieves relevant chunks
     - `list_documents()`: Lists all ingested documents
   - **Technologies**: ChromaDB, SentenceTransformers
   - **Why Important**: This is the heart of the RAG system - handles all vector operations

#### 2. **`ollama_client.py`** ⭐ **CRITICAL**
   - **Purpose**: Interface to local Ollama model
   - **Key Components**:
     - `OllamaClient` class: Wraps Ollama API
     - `generate()`: Generates answers with context and source citations
     - Handles prompt engineering for detailed, cited responses
   - **Model**: `ibm/granite4:350m-h`
   - **Why Important**: Connects RAG retrieval to LLM generation

#### 3. **`main.py`** ⭐ **CRITICAL**
   - **Purpose**: CLI interface and orchestration
   - **Key Functions**:
     - `crawl_and_ingest()`: Crawls docs and ingests into RAG system
     - `query()`: Main query function - retrieval + generation
     - `list_documents()`: Lists ingested documents
   - **Commands**: `crawl`, `ingest`, `query`, `list`, `interactive`
   - **Why Important**: User-facing interface that ties everything together

#### 4. **`scraper.py`** ⭐ **IMPORTANT**
   - **Purpose**: Web scraping for documentation ingestion
   - **Key Components**:
     - `CloudBeesScraper` class: Handles HTTP requests and HTML parsing
     - `scrape_url()`: Extracts text from single page
     - `crawl_documentation()`: Recursively discovers and crawls all docs
   - **Why Important**: Enables automatic ingestion of online documentation

#### 5. **`chunker.py`** ⭐ **IMPORTANT**
   - **Purpose**: Document chunking for optimal retrieval
   - **Key Components**:
     - `DocumentChunker` class: Splits documents intelligently
     - `chunk_text()`: Creates overlapping chunks (1000/200 chars)
     - Preserves context with overlap between chunks
   - **Why Important**: Proper chunking is crucial for RAG performance

### Supporting Files

- **`requirements.txt`**: Python dependencies
- **`.gitignore`**: Git ignore rules (excludes `chroma_db/`, `__pycache__/`, etc.)
- **`chroma_db/`**: Persistent vector database storage (auto-generated, gitignored)

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama installed and running**
3. **IBM Granite 4 model pulled**:
   ```bash
   ollama pull ibm/granite4:350m-h
   ```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify Ollama is running
ollama serve

# Verify model is available
ollama list
```

### Usage

#### 1. Ingest Documentation

**Crawl and ingest all CloudBees CI documentation:**
```bash
python main.py crawl https://docs.cloudbees.com/docs/cloudbees-ci/latest/
```

**Limit number of pages (for testing):**
```bash
python main.py crawl https://docs.cloudbees.com/docs/cloudbees-ci/latest/ --max-pages 100
```

#### 2. Query the System

**Single query:**
```bash
python main.py query "How do I configure high availability for CloudBees CI?"
```

**Interactive mode:**
```bash
python main.py interactive
```

**List ingested documents:**
```bash
python main.py list
```

## 🔧 Configuration

### Embedding Model

Default: `all-MiniLM-L6-v2` (lightweight, fast)

To use a more accurate (but slower) model, edit `rag_system.py`:
```python
rag = RAGSystem(embedding_model="all-mpnet-base-v2")
```

### Chunking Parameters

Default: 1000 chars per chunk, 200 char overlap

To adjust, edit `chunker.py` or modify in `main.py`:
```python
chunker = DocumentChunker(chunk_size=1500, chunk_overlap=300)
```

### Ollama Model

Default: `ibm/granite4:350m-h`

To change, edit `ollama_client.py`:
```python
ollama = OllamaClient(model_name="your-model-name")
```

### Retrieval Parameters

Default: 8 chunks retrieved per query

To adjust:
```bash
python main.py query "your question" --n-results 10
```

## 📊 How It Works: Technical Details

### Embedding Generation

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Method**: Mean pooling of token embeddings
- **Similarity**: Cosine similarity for retrieval

### Vector Storage

- **Database**: ChromaDB (persistent, local)
- **Index**: HNSW (Hierarchical Navigable Small World)
- **Distance Metric**: Cosine similarity
- **Collection**: `cloudbees_kb` (default)

### Retrieval Process

1. Query embedding generated using same model as documents
2. ChromaDB performs approximate nearest neighbor search
3. Top-k chunks retrieved based on cosine similarity
4. Results include: text, metadata (URL, title), similarity score

### Generation Process

1. Retrieved chunks merged into context
2. System prompt instructs model to:
   - Provide detailed, comprehensive answers
   - Include inline source citations
   - Use format: `[Source: Title](URL)`
3. Model generates answer using context + question
4. Answer includes both explanation and citations

## 🎯 Key Features

- ✅ **Automatic Documentation Ingestion**: Crawls and scrapes CloudBees CI docs
- ✅ **Semantic Search**: Finds relevant docs even with different wording
- ✅ **Source Citations**: Inline citations in answers with source URLs
- ✅ **Detailed Answers**: Comprehensive explanations, not just links
- ✅ **Local & Private**: Everything runs on your machine
- ✅ **Batch Processing**: Handles large document sets efficiently
- ✅ **Interactive Mode**: Chat-like interface for queries

## 🛠️ Troubleshooting

### Ollama Connection Error
```bash
# Ensure Ollama is running
ollama serve

# Verify model exists
ollama list
```

### No Results Found
- Check if documents were ingested: `python main.py list`
- Verify `chroma_db/` directory exists and has data
- Try re-ingesting: `python main.py crawl <url>`

### Poor Answer Quality
- Increase retrieved chunks: `--n-results 10`
- Try different embedding model
- Adjust chunk size in `chunker.py`
- Check if relevant docs were ingested

### Batch Size Error
- Already handled: system automatically batches large ingestions
- Default batch size: 4000 chunks per batch

## 📝 Example Queries

```bash
# High Availability
python main.py query "How do I configure high availability for CloudBees CI on Kubernetes?"

# Configuration as Code
python main.py query "How do I create and configure a CasC bundle for CloudBees CI?"

# Agent Connectivity
python main.py query "How do I troubleshoot agent connectivity issues in CloudBees CI?"

# Plugin Management
python main.py query "How do I install and manage plugins in CloudBees CI?"
```

## 🔮 Future Enhancements

Potential improvements:
- **Multi-Collection RAG**: Separate collections for different topics (CasC, HA, Agents, etc.)
- **Router System**: Automatically route queries to relevant expert collections
- **Hybrid Search**: Combine semantic search with keyword search
- **Query Expansion**: Automatically expand queries with synonyms
- **Answer Quality Scoring**: Rate answer quality and suggest improvements

## 📄 License

This project is for internal use as a support engineering tool.

## 🙏 Acknowledgments

- **Ollama**: Local LLM deployment
- **ChromaDB**: Vector database
- **Sentence Transformers**: Embedding models
- **CloudBees**: Documentation source

---

**Built for CloudBees Support Engineers** | Powered by RAG + Local LLMs
