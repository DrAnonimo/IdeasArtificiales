# Fork Setup Guide for RAG Experiments

This guide helps you fork the project and set up an experimentation environment.

## 🍴 Forking the Project

### Option 1: Git Fork (Recommended)

```bash
# Create a new branch for experiments
git checkout -b experiments/rag-improvements

# Or create a new directory for your fork
cd ..
git clone <original-repo-url> Abejita-experiments
cd Abejita-experiments
```

### Option 2: Copy Directory

```bash
# Simple copy approach
cd ..
cp -r Abejita Abejita-experiments
cd Abejita-experiments
```

## 📁 Recommended Project Structure for Experiments

```
Abejita-experiments/
├── core/                    # Original core files
│   ├── rag_system.py
│   ├── ollama_client.py
│   ├── scraper.py
│   ├── chunker.py
│   └── main.py
├── experiments/             # Experiment implementations
│   ├── __init__.py
│   ├── prompt_variations.py
│   ├── multi_query.py
│   ├── reranker.py
│   ├── hybrid_search.py
│   └── query_expansion.py
├── tests/                   # Test suite
│   ├── test_queries.json
│   ├── evaluate.py
│   └── metrics.py
├── results/                 # Experiment results
│   └── .gitkeep
├── configs/                # Experiment configurations
│   ├── prompt_configs.yaml
│   └── retrieval_configs.yaml
└── requirements.txt
```

## 🚀 Quick Start: First Experiment

### 1. Create Experiment Directory

```bash
mkdir -p experiments tests results
```

### 2. Create Base Experiment Class

Create `experiments/base_experiment.py`:

```python
"""Base class for RAG experiments."""
from abc import ABC, abstractmethod
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class BaseExperiment(ABC):
    """Base class for all RAG experiments."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.results = []
    
    @abstractmethod
    def run(self, query: str, rag_system, ollama_client) -> Dict:
        """Run the experiment and return results."""
        pass
    
    def evaluate(self, answer: str, expected: Dict) -> float:
        """Evaluate answer quality (0.0 to 1.0)."""
        # Simple evaluation - can be enhanced
        score = 0.0
        if expected.get('keywords'):
            for keyword in expected['keywords']:
                if keyword.lower() in answer.lower():
                    score += 0.2
        return min(score, 1.0)
    
    def save_results(self, output_file: str):
        """Save experiment results to file."""
        import json
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
```

### 3. Implement Your First Experiment

Create `experiments/prompt_few_shot.py`:

```python
"""Few-shot prompting experiment."""
from experiments.base_experiment import BaseExperiment
from typing import Dict

class FewShotPromptExperiment(BaseExperiment):
    """Experiment with few-shot examples in prompts."""
    
    def __init__(self):
        super().__init__(
            name="few_shot_prompting",
            description="Add few-shot examples to improve answer quality"
        )
        self.examples = [
            {
                "question": "How do I configure high availability?",
                "answer": "To configure high availability in CloudBees CI... [Source: HA Guide](url)"
            },
            # Add more examples
        ]
    
    def run(self, query: str, rag_system, ollama_client) -> Dict:
        """Run few-shot experiment."""
        # Retrieve context
        results = rag_system.search(query, n_results=8)
        
        # Build few-shot prompt
        examples_text = "\n\n".join([
            f"Q: {ex['question']}\nA: {ex['answer']}"
            for ex in self.examples
        ])
        
        context = self._build_context(results)
        
        prompt = f"""You are a CloudBees CI support engineer.

Here are examples of good answers:

{examples_text}

Documentation:
{context}

Question: {query}
Answer:"""
        
        answer = ollama_client.generate(prompt)
        
        return {
            'query': query,
            'answer': answer,
            'sources': [r['metadata'] for r in results],
            'experiment': self.name
        }
    
    def _build_context(self, results):
        """Build context from retrieved results."""
        return "\n\n".join([
            f"[{r['metadata'].get('title', 'Untitled')}]\n{r['text']}"
            for r in results
        ])
```

### 4. Create Comparison Script

Create `compare_experiments.py`:

```python
"""Compare different experiments."""
from experiments.prompt_few_shot import FewShotPromptExperiment
from rag_system import RAGSystem
from ollama_client import OllamaClient
import json

def compare_experiments(queries_file: str = "tests/test_queries.json"):
    """Compare baseline vs experiment."""
    
    # Load test queries
    with open(queries_file) as f:
        test_queries = json.load(f)
    
    # Initialize systems
    rag = RAGSystem()
    ollama = OllamaClient()
    
    # Baseline (original)
    from main import query as baseline_query
    
    # Experiment
    experiment = FewShotPromptExperiment()
    
    results = []
    for test in test_queries:
        query = test['query']
        
        # Run baseline
        baseline_answer = baseline_query(query, n_results=8)
        
        # Run experiment
        exp_result = experiment.run(query, rag, ollama)
        
        results.append({
            'query': query,
            'baseline': baseline_answer,
            'experiment': exp_result['answer'],
            'expected_keywords': test.get('keywords', [])
        })
    
    # Save comparison
    with open('results/comparison.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Comparison saved to results/comparison.json")

if __name__ == "__main__":
    compare_experiments()
```

### 5. Create Test Queries

Create `tests/test_queries.json`:

```json
[
    {
        "query": "How do I configure high availability for CloudBees CI?",
        "keywords": ["high availability", "HA", "prerequisites", "steps"],
        "expected_topics": ["ha", "kubernetes"],
        "category": "installation"
    },
    {
        "query": "How do I create a CasC bundle?",
        "keywords": ["casc", "bundle", "yaml", "configuration"],
        "expected_topics": ["casc", "configuration"],
        "category": "configuration"
    },
    {
        "query": "How do I troubleshoot agent connectivity issues?",
        "keywords": ["agent", "connectivity", "troubleshoot", "websocket"],
        "expected_topics": ["agents", "networking"],
        "category": "troubleshooting"
    }
]
```

## 🔄 Experiment Workflow

1. **Create experiment class** in `experiments/`
2. **Add test queries** to `tests/test_queries.json`
3. **Run comparison**: `python compare_experiments.py`
4. **Review results** in `results/comparison.json`
5. **Iterate** based on findings

## 📊 Evaluation Metrics

Create `tests/metrics.py`:

```python
"""Metrics for evaluating experiments."""
import re
from typing import Dict, List

def citation_accuracy(answer: str, sources: List[Dict]) -> float:
    """Check if citations in answer match actual sources."""
    # Extract citations from answer
    citations = re.findall(r'\[Source: ([^\]]+)\]\(([^\)]+)\)', answer)
    
    # Check if they match sources
    source_urls = {s['url'] for s in sources}
    matched = sum(1 for _, url in citations if url in source_urls)
    
    return matched / len(sources) if sources else 0.0

def keyword_coverage(answer: str, expected_keywords: List[str]) -> float:
    """Check if answer covers expected keywords."""
    answer_lower = answer.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return found / len(expected_keywords) if expected_keywords else 0.0

def answer_length(answer: str) -> int:
    """Get answer length (longer often = more detailed)."""
    return len(answer)

def evaluate_answer(answer: str, expected: Dict) -> Dict:
    """Comprehensive answer evaluation."""
    return {
        'citation_accuracy': citation_accuracy(answer, expected.get('sources', [])),
        'keyword_coverage': keyword_coverage(answer, expected.get('keywords', [])),
        'length': answer_length(answer),
        'has_citations': bool(re.search(r'\[Source:', answer))
    }
```

## 🎯 Next Steps

1. **Start with one experiment** (e.g., few-shot prompting)
2. **Run it on 5-10 test queries**
3. **Compare results** with baseline
4. **If promising**, implement more variations
5. **Document findings** in `results/`

## 📝 Experiment Log Template

Create `results/experiment_log.md`:

```markdown
# Experiment Log

## Experiment: Few-Shot Prompting
**Date**: 2024-12-17
**Status**: In Progress

### Hypothesis
Adding few-shot examples will improve answer quality and citation accuracy.

### Implementation
- Added 3 example Q&A pairs to prompt
- Examples cover different question types

### Results
- Citation accuracy: 0.85 (baseline: 0.72)
- Keyword coverage: 0.90 (baseline: 0.78)
- Average answer length: 450 words (baseline: 320)

### Conclusion
Few-shot prompting improves answer quality by 15-20%.

### Next Steps
- Try different example sets
- Test with more examples (5-10)
```

---

**Ready to experiment?** Start with the simplest experiment and iterate! 🚀

