"""
Client for interacting with Ollama API.
"""
import ollama
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama API."""
    
    def __init__(self, model_name: str = "ibm/granite4:350m-h"):
        """
        Initialize Ollama client.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        self.model_name = model_name
        logger.info(f"Initialized Ollama client with model: {model_name}")
    
    def generate(self, prompt: str, context: Optional[str] = None, sources: Optional[List[Dict]] = None, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate response using Ollama.
        
        Args:
            prompt: User prompt/question
            context: Additional context (e.g., retrieved documents)
            sources: List of source dictionaries with 'title' and 'url' keys
            temperature: Temperature for generation (0.0-1.0)
            **kwargs: Additional parameters for Ollama options
            
        Returns:
            Generated response
        """
        # Build full prompt with context
        if context:
            # Build source reference instructions
            source_refs = ""
            if sources:
                source_refs = "\n\nWhen referencing information from the documentation, cite the source using the format [Source: Title](URL). "
                source_refs += "Available sources:\n"
                for i, source in enumerate(sources, 1):
                    source_refs += f"{i}. {source.get('title', 'Untitled')} - {source.get('url', '')}\n"
            
            full_prompt = f"""You are a helpful support engineer assistant for CloudBees. 
Use the following documentation to answer the question comprehensively. If the answer is not in the documentation, say so.

CRITICAL INSTRUCTIONS:
1. Provide a DETAILED, COMPREHENSIVE explanation that fully answers the question
2. Include step-by-step instructions, requirements, configurations, or explanations as needed
3. Do NOT just list sources or provide brief answers - give a thorough, helpful response
4. When referencing information from the documentation, cite the source inline using the format [Source: Title](URL)
5. The answer should be informative enough that users understand the topic, with citations as supporting evidence

Documentation:
{context}
{source_refs}

Question: {prompt}

Provide a detailed, comprehensive answer that fully addresses the question. Include specific steps, requirements, configurations, or explanations as relevant. Cite sources inline using [Source: Title](URL) when referencing documentation:"""
        else:
            full_prompt = prompt
        
        try:
            # Ollama requires parameters like temperature to be in an 'options' dict
            options = kwargs.get('options', {})
            options['temperature'] = temperature
            # Merge any other options from kwargs
            for key, value in kwargs.items():
                if key != 'options':
                    options[key] = value
            
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                options=options
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def chat(self, messages: List[Dict], temperature: float = 0.7, **kwargs) -> str:
        """
        Chat with Ollama using message format.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for generation (0.0-1.0)
            **kwargs: Additional parameters for Ollama options
            
        Returns:
            Generated response
        """
        try:
            # Ollama requires parameters like temperature to be in an 'options' dict
            options = kwargs.get('options', {})
            options['temperature'] = temperature
            # Merge any other options from kwargs
            for key, value in kwargs.items():
                if key != 'options':
                    options[key] = value
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options=options
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise

