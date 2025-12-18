"""
Main script for CloudBees RAG system.
Handles document ingestion and querying.
"""
import argparse
import json
from scraper import CloudBeesScraper
from chunker import DocumentChunker
from rag_system import RAGSystem
from ollama_client import OllamaClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def crawl_and_ingest(start_url: str, max_pages: int = None, filter_pattern: str = "/docs/cloudbees-ci/"):
    """
    Crawl documentation site and ingest all discovered pages.
    
    Args:
        start_url: Starting URL to crawl from
        max_pages: Maximum number of pages to crawl (None for unlimited)
        filter_pattern: Pattern to filter URLs
    """
    logger.info("Starting crawl and ingestion...")
    
    # Initialize components
    scraper = CloudBeesScraper(base_url=start_url, delay=1.0)
    chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
    rag = RAGSystem()
    
    # Crawl to discover URLs
    logger.info("Crawling documentation site to discover pages...")
    discovered_urls = scraper.crawl_documentation(
        start_url=start_url,
        max_pages=max_pages,
        filter_pattern=filter_pattern
    )
    
    if not discovered_urls:
        logger.warning("No URLs discovered. Check the start URL and filter pattern.")
        return
    
    logger.info(f"Discovered {len(discovered_urls)} documentation pages")
    
    # Scrape all discovered URLs
    logger.info("Scraping discovered pages...")
    documents = scraper.scrape_urls(discovered_urls)
    logger.info(f"Successfully scraped {len(documents)} documents")
    
    if not documents:
        logger.warning("No documents were successfully scraped.")
        return
    
    # Chunk documents
    logger.info("Chunking documents...")
    chunks = chunker.chunk_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")
    
    # Add to vector store
    logger.info("Adding chunks to vector store...")
    rag.add_documents(chunks)
    
    # Show collection info
    info = rag.get_collection_info()
    logger.info(f"Ingestion complete! Collection has {info['document_count']} chunks")


def ingest_documents(urls: list, base_url: str = None):
    """
    Ingest documents from URLs into the RAG system.
    
    Args:
        urls: List of URLs to scrape
        base_url: Optional base URL for the scraper
    """
    logger.info("Starting document ingestion...")
    
    # Initialize components
    scraper = CloudBeesScraper(base_url=base_url or urls[0] if urls else "")
    chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
    rag = RAGSystem()
    
    # Scrape documents
    logger.info(f"Scraping {len(urls)} URLs...")
    documents = scraper.scrape_urls(urls)
    logger.info(f"Scraped {len(documents)} documents")
    
    # Chunk documents
    logger.info("Chunking documents...")
    chunks = chunker.chunk_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")
    
    # Add to vector store
    logger.info("Adding chunks to vector store...")
    rag.add_documents(chunks)
    
    # Show collection info
    info = rag.get_collection_info()
    logger.info(f"Ingestion complete! Collection has {info['document_count']} chunks")


def list_documents(limit: int = None):
    """
    List all documents in the vector store.
    
    Args:
        limit: Maximum number of documents to show (None for all)
    """
    rag = RAGSystem()
    
    info = rag.get_collection_info()
    print(f"\n{'='*80}")
    print(f"VECTOR STORE SUMMARY")
    print(f"{'='*80}")
    print(f"Collection: {info['collection_name']}")
    print(f"Total chunks: {info['document_count']}")
    print()
    
    if info['document_count'] == 0:
        print("No documents in the vector store!")
        return
    
    documents = rag.list_documents(limit=limit)
    print(f"{'='*80}")
    print(f"DOCUMENTS ({len(documents)} unique pages)")
    print(f"{'='*80}\n")
    
    for i, doc in enumerate(documents, 1):
        print(f"{i}. {doc['title']}")
        print(f"   URL: {doc['url']}")
        print(f"   Chunks: {doc['chunk_count']}")
        print()


def query(query_text: str, n_results: int = 8, temperature: float = 0.7):
    """
    Query the RAG system.
    
    Args:
        query_text: User question
        n_results: Number of relevant chunks to retrieve
        temperature: Temperature for Ollama generation
    """
    logger.info(f"Querying: {query_text}")
    
    # Initialize components
    rag = RAGSystem()
    ollama = OllamaClient()
    
    # Check if collection has documents
    info = rag.get_collection_info()
    if info['document_count'] == 0:
        logger.error("No documents in the vector store! Please run ingestion first.")
        return
    
    # Search for relevant documents
    logger.info("Searching for relevant documents...")
    results = rag.search(query_text, n_results=n_results)
    
    if not results:
        logger.warning("No relevant documents found")
        response = ollama.generate(
            query_text,
            temperature=temperature
        )
    else:
        logger.info(f"Found {len(results)} relevant documents")
        
        # Build context from retrieved documents and extract sources
        context_parts = []
        sources = []
        seen_urls = set()  # Track unique sources
        
        for i, result in enumerate(results, 1):
            title = result['metadata'].get('title', 'Untitled')
            url = result['metadata'].get('url', '')
            text = result['text']
            context_parts.append(f"[Document {i}: {title}]\nURL: {url}\nContent:\n{text}\n")
            
            # Track unique sources for citation
            if url and url not in seen_urls:
                sources.append({'title': title, 'url': url})
                seen_urls.add(url)
        
        context = "\n\n".join(context_parts)
        
        # Generate response with context and sources
        logger.info("Generating response with Ollama...")
        response = ollama.generate(
            query_text,
            context=context,
            sources=sources,
            temperature=temperature
        )
        
        # Show sources (still useful for reference)
        print("\n" + "="*80)
        print("SOURCES USED:")
        print("="*80)
        for i, source in enumerate(sources, 1):
            print(f"{i}. {source['title']}")
            print(f"   {source['url']}")
            print()
    
    # Show response
    print("="*80)
    print("ANSWER:")
    print("="*80)
    print(response)
    print()


def main():
    parser = argparse.ArgumentParser(description="CloudBees RAG System")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest documents from URLs')
    ingest_parser.add_argument('urls', nargs='+', help='URLs to scrape')
    ingest_parser.add_argument('--base-url', help='Base URL for the scraper')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG system')
    query_parser.add_argument('query', help='Question to ask')
    query_parser.add_argument('--n-results', type=int, default=8, help='Number of results to retrieve (default: 8)')
    query_parser.add_argument('--temperature', type=float, default=0.7, help='Temperature for generation')
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Interactive query mode')
    interactive_parser.add_argument('--n-results', type=int, default=8, help='Number of results to retrieve (default: 8)')
    interactive_parser.add_argument('--temperature', type=float, default=0.7, help='Temperature for generation')
    
    # Crawl command
    crawl_parser = subparsers.add_parser('crawl', help='Crawl documentation site and ingest all pages')
    crawl_parser.add_argument('start_url', help='Starting URL to crawl from')
    crawl_parser.add_argument('--max-pages', type=int, default=None, help='Maximum number of pages to crawl (default: unlimited)')
    crawl_parser.add_argument('--filter-pattern', default='/docs/cloudbees-ci/', help='URL pattern to filter (default: /docs/cloudbees-ci/)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all documents in the vector store')
    list_parser.add_argument('--limit', type=int, default=None, help='Maximum number of documents to show (default: all)')
    
    args = parser.parse_args()
    
    if args.command == 'ingest':
        ingest_documents(args.urls, args.base_url)
    elif args.command == 'crawl':
        crawl_and_ingest(args.start_url, args.max_pages, args.filter_pattern)
    elif args.command == 'list':
        list_documents(args.limit)
    elif args.command == 'query':
        query(args.query, args.n_results, args.temperature)
    elif args.command == 'interactive':
        print("CloudBees RAG System - Interactive Mode")
        print("Type 'exit' or 'quit' to exit")
        print("="*80)
        
        rag = RAGSystem()
        ollama = OllamaClient()
        
        info = rag.get_collection_info()
        if info['document_count'] == 0:
            print("WARNING: No documents in the vector store! Please run ingestion first.")
            print()
        
        while True:
            try:
                query_text = input("\nQuestion: ").strip()
                if query_text.lower() in ['exit', 'quit', 'q']:
                    break
                
                if not query_text:
                    continue
                
                query(query_text, args.n_results, args.temperature)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

