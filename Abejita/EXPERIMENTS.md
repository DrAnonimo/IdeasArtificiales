# RAG System Experimentation Guide

This document outlines experiments to improve local LLM results in the CloudBees CI RAG system. Each experiment is categorized by impact and implementation difficulty.

## 🎯 High-Impact, Low-Effort Experiments

### 1. **Prompt Engineering Variations**

**Experiment**: Try different prompt templates to see which produces better answers.

**Variations to Test**:

#### A. Few-Shot Examples
```python
# Add examples of good answers in the prompt
full_prompt = f"""You are a helpful support engineer assistant for CloudBees.

Here are examples of good answers:

Example 1:
Q: How do I configure high availability?
A: To configure high availability in CloudBees CI, follow these steps:
1. First, ensure prerequisites are met: [Source: HA Requirements](url)
2. Install HA components: [Source: HA Installation](url)
...

Documentation:
{context}

Question: {prompt}
Answer:"""
```

#### B. Chain-of-Thought Prompting
```python
full_prompt = f"""You are a CloudBees CI support engineer. Answer questions step-by-step.

For the question: {prompt}

Step 1: Identify what the user is asking
Step 2: Find relevant information in the documentation
Step 3: Synthesize a comprehensive answer
Step 4: Cite sources

Documentation:
{context}

Answer:"""
```

#### C. Role-Based Prompting
```python
full_prompt = f"""You are an expert CloudBees CI support engineer with 10 years of experience.
Your answers should be:
- Precise and technical
- Include specific configuration examples
- Reference official documentation
- Provide troubleshooting steps when relevant

Documentation:
{context}

Question: {prompt}
Answer:"""
```

**Implementation**: Modify `ollama_client.py` → `generate()` method
**Expected Impact**: Medium-High (can significantly improve answer quality)
**Difficulty**: Easy

---

### 2. **Retrieval Strategy: Multi-Query**

**Experiment**: Generate multiple query variations and retrieve from each.

**Implementation**:
```python
def multi_query_search(rag, query: str, n_queries: int = 3):
    """Generate multiple query variations and retrieve from each."""
    # Generate query variations using the LLM
    query_prompt = f"""Generate {n_queries} different ways to ask this question:
    Original: {query}
    
    Generate variations that:
    - Use different terminology
    - Focus on different aspects
    - Are more specific or more general
    
    Variations:"""
    
    variations = ollama.generate(query_prompt)
    # Parse variations and search with each
    # Merge and deduplicate results
```

**Expected Impact**: High (better retrieval coverage)
**Difficulty**: Medium

---

### 3. **Reranking Retrieved Chunks**

**Experiment**: Use a cross-encoder to rerank retrieved chunks for better relevance.

**Implementation**:
```python
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    def rerank(self, query: str, chunks: List[Dict], top_k: int = 5):
        pairs = [[query, chunk['text']] for chunk in chunks]
        scores = self.model.predict(pairs)
        # Sort by scores and return top_k
```

**Expected Impact**: High (more relevant context)
**Difficulty**: Medium

---

### 4. **Temperature and Generation Parameters**

**Experiment**: Test different temperature values and other generation parameters.

**Parameters to Test**:
- `temperature`: 0.1 (deterministic) to 0.9 (creative)
- `top_p`: Nucleus sampling (0.9-0.95)
- `top_k`: Top-k sampling (40-50)
- `repeat_penalty`: Reduce repetition (1.1-1.2)

**Implementation**: Add CLI flags:
```bash
python main.py query "question" --temperature 0.3 --top-p 0.9 --top-k 40
```

**Expected Impact**: Medium (affects answer style/quality)
**Difficulty**: Easy

---

## 🔬 High-Impact, Medium-Effort Experiments

### 5. **Hybrid Search (Semantic + Keyword)**

**Experiment**: Combine semantic search with BM25 keyword search.

**Implementation**:
```python
from rank_bm25 import BM25Okapi

class HybridSearch:
    def __init__(self, rag_system):
        self.rag = rag_system
        # Build BM25 index from all documents
        self.bm25 = BM25Okapi([chunk['text'].split() for chunk in all_chunks])
    
    def search(self, query: str, n_results: int = 8, alpha: float = 0.7):
        # Semantic search (alpha weight)
        semantic_results = self.rag.search(query, n_results * 2)
        
        # BM25 keyword search (1-alpha weight)
        keyword_results = self.bm25.get_scores(query.split())
        
        # Combine scores: alpha * semantic + (1-alpha) * keyword
        # Return top n_results
```

**Expected Impact**: High (better for technical terms, exact matches)
**Difficulty**: Medium

---

### 6. **Query Expansion**

**Experiment**: Automatically expand queries with synonyms and related terms.

**Implementation**:
```python
def expand_query(query: str):
    """Expand query with synonyms and related terms."""
    expansions = {
        'ha': ['high availability', 'failover', 'redundancy'],
        'casc': ['configuration as code', 'cas-c', 'bundle'],
        'agent': ['node', 'executor', 'slave'],
        # ... more mappings
    }
    
    expanded = [query]
    for term, synonyms in expansions.items():
        if term in query.lower():
            expanded.extend([query.replace(term, syn) for syn in synonyms])
    
    return expanded
```

**Expected Impact**: Medium-High (better retrieval)
**Difficulty**: Easy-Medium

---

### 7. **Context Window Optimization**

**Experiment**: Summarize or filter retrieved chunks to fit model context better.

**Strategies**:
- **Summarization**: Summarize long chunks before passing to LLM
- **Relevance Filtering**: Remove chunks below similarity threshold
- **Deduplication**: Remove redundant chunks

**Implementation**:
```python
def optimize_context(chunks: List[Dict], max_length: int = 3000):
    """Optimize context to fit within limits."""
    # Sort by relevance score
    sorted_chunks = sorted(chunks, key=lambda x: x['distance'], reverse=True)
    
    # Filter low-relevance chunks
    filtered = [c for c in sorted_chunks if c['distance'] > threshold]
    
    # Truncate to max_length
    context = ""
    for chunk in filtered:
        if len(context) + len(chunk['text']) > max_length:
            break
        context += chunk['text'] + "\n\n"
    
    return context
```

**Expected Impact**: Medium (better focus, less noise)
**Difficulty**: Medium

---

### 8. **Answer Refinement (Multi-Pass)**

**Experiment**: Generate answer, then refine it in a second pass.

**Implementation**:
```python
def generate_refined_answer(query: str, context: str, initial_answer: str):
    """Refine answer in a second pass."""
    refinement_prompt = f"""You previously answered this question:

Question: {query}
Initial Answer: {initial_answer}

Documentation Context:
{context}

Review your answer and improve it:
1. Check for accuracy against the documentation
2. Add missing details
3. Improve clarity
4. Ensure all citations are correct

Refined Answer:"""
    
    return ollama.generate(refinement_prompt)
```

**Expected Impact**: Medium-High (better quality)
**Difficulty**: Medium

---

## 🚀 High-Impact, High-Effort Experiments

### 9. **Multi-Collection RAG (Expert System)**

**Experiment**: Separate collections by topic (CasC, HA, Agents, etc.) with routing.

**Implementation**:
```python
class ExpertRouter:
    def __init__(self):
        self.experts = {
            'casc': RAGSystem(collection_name='cloudbees_kb_casc'),
            'agents': RAGSystem(collection_name='cloudbees_kb_agents'),
            'ha': RAGSystem(collection_name='cloudbees_kb_ha'),
            # ...
        }
    
    def route(self, query: str):
        """Route query to relevant expert(s)."""
        # Classify query topic
        topics = self.classify_topics(query)
        
        # Query relevant experts
        results = []
        for topic in topics:
            expert_results = self.experts[topic].search(query)
            results.extend(expert_results)
        
        return results
```

**Expected Impact**: Very High (specialized, focused answers)
**Difficulty**: High (requires re-ingestion)

---

### 10. **Fine-Tuning the Local Model**

**Experiment**: Fine-tune `ibm/granite4:350m-h` on CloudBees CI Q&A pairs.

**Approach**:
- Collect Q&A pairs from documentation
- Create training dataset
- Fine-tune using Ollama's fine-tuning capabilities (if available) or LoRA

**Expected Impact**: Very High (domain-specific knowledge)
**Difficulty**: Very High (requires ML expertise)

---

### 11. **Ensemble Retrieval**

**Experiment**: Use multiple embedding models and combine results.

**Implementation**:
```python
class EnsembleRAG:
    def __init__(self):
        self.models = [
            SentenceTransformer('all-MiniLM-L6-v2'),
            SentenceTransformer('all-mpnet-base-v2'),
            # ... more models
        ]
    
    def search(self, query: str, n_results: int = 8):
        all_results = []
        for model in self.models:
            results = self._search_with_model(model, query, n_results)
            all_results.extend(results)
        
        # Merge and deduplicate by URL
        # Rank by average score across models
        return merged_results
```

**Expected Impact**: High (more robust retrieval)
**Difficulty**: High (slower, more complex)

---

## 📊 Medium-Impact Experiments

### 12. **Chunking Strategy Variations**

**Experiments**:
- **Semantic Chunking**: Use embeddings to find natural boundaries
- **Sentence-based**: Chunk by sentences instead of characters
- **Hierarchical**: Store chunks at multiple granularities

**Expected Impact**: Medium
**Difficulty**: Medium

---

### 13. **Metadata-Enhanced Retrieval**

**Experiment**: Boost chunks based on metadata (e.g., prioritize installation guides for "how to install" queries).

**Implementation**:
```python
def search_with_metadata_boost(query: str, metadata_filters: Dict):
    """Boost results based on metadata."""
    results = rag.search(query, n_results=20)
    
    # Boost chunks matching metadata
    for result in results:
        if matches_metadata(result, metadata_filters):
            result['distance'] *= 0.8  # Lower distance = higher relevance
    
    return sorted(results, key=lambda x: x['distance'])[:8]
```

**Expected Impact**: Medium
**Difficulty**: Easy-Medium

---

### 14. **Answer Post-Processing**

**Experiment**: Post-process answers to improve formatting, fix citations, etc.

**Operations**:
- Fix broken citation links
- Format code blocks
- Add section headers
- Validate URLs

**Expected Impact**: Low-Medium (better presentation)
**Difficulty**: Easy

---

## 🧪 Testing Framework

Create a test suite to evaluate experiments:

```python
# test_rag_experiments.py

test_queries = [
    {
        "query": "How do I configure high availability?",
        "expected_topics": ["ha", "kubernetes", "installation"],
        "expected_sources": ["ha/", "installation/"]
    },
    # ... more test cases
]

def evaluate_experiment(experiment_name, queries):
    """Evaluate an experiment against test queries."""
    results = []
    for test in queries:
        answer = query(test['query'])
        score = evaluate_answer(answer, test)
        results.append(score)
    return average(results)
```

---

## 📈 Recommended Experiment Order

1. **Start Here** (Quick wins):
   - Prompt engineering variations (#1)
   - Temperature tuning (#4)
   - Query expansion (#6)

2. **Next Level** (Medium effort):
   - Multi-query retrieval (#2)
   - Reranking (#3)
   - Hybrid search (#5)

3. **Advanced** (Higher effort):
   - Multi-collection RAG (#9)
   - Context optimization (#7)
   - Answer refinement (#8)

4. **Expert Level** (Requires expertise):
   - Fine-tuning (#10)
   - Ensemble methods (#11)

---

## 🔍 Metrics to Track

For each experiment, measure:

- **Answer Quality**: Relevance, completeness, accuracy
- **Citation Accuracy**: Are sources correct?
- **Response Time**: Latency impact
- **Retrieval Quality**: Are the right docs retrieved?
- **User Satisfaction**: Subjective quality ratings

---

## 💡 Quick Implementation Template

```python
# experiments/prompt_variations.py

class PromptExperiment:
    def __init__(self, variation_type: str):
        self.variation_type = variation_type
    
    def build_prompt(self, query: str, context: str, sources: List[Dict]):
        if self.variation_type == "few_shot":
            return self._few_shot_prompt(query, context, sources)
        elif self.variation_type == "chain_of_thought":
            return self._cot_prompt(query, context, sources)
        # ... more variations
    
    def _few_shot_prompt(self, query, context, sources):
        # Implementation
        pass
```

---

## 🎯 Success Criteria

An experiment is successful if it:
- ✅ Improves answer quality (more accurate, detailed)
- ✅ Maintains or improves citation accuracy
- ✅ Doesn't significantly increase latency (<2x)
- ✅ Works consistently across different query types

---

**Happy Experimenting!** 🚀

Start with the high-impact, low-effort experiments and iterate based on results.

