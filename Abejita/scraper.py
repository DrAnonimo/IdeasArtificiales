"""
Web scraper for CloudBees knowledge base articles.
Supports scraping from URLs or sitemaps.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Set, Optional
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudBeesScraper:
    """Scraper for CloudBees documentation/knowledge base."""
    
    def __init__(self, base_url: str, delay: float = 1.0):
        """
        Initialize scraper.
        
        Args:
            base_url: Base URL of the knowledge base
            delay: Delay between requests (seconds)
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def scrape_url(self, url: str) -> Dict[str, str]:
        """
        Scrape a single URL and extract text content.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with 'url', 'title', and 'content'
        """
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Untitled"
            
            # Try to find main content area (common patterns for documentation sites)
            # CloudBees docs might use specific classes/ids
            main_content = (
                soup.find('main') or
                soup.find('article') or
                soup.find('div', id=lambda x: x and ('content' in x.lower() or 'main' in x.lower())) or
                soup.find('div', class_=lambda x: x and any(term in x.lower() for term in ['content', 'article', 'documentation', 'docs-content', 'doc-content'])) or
                soup.find('div', role='main') or
                soup.find('body')
            )
            
            # Extract text
            text = main_content.get_text(separator='\n', strip=True) if main_content else soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            content = '\n'.join(lines)
            
            time.sleep(self.delay)  # Be respectful
            
            return {
                'url': url,
                'title': title_text,
                'content': content
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def scrape_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of scraped documents
        """
        documents = []
        for url in urls:
            doc = self.scrape_url(url)
            if doc and doc['content']:
                documents.append(doc)
        return documents
    
    def find_links(self, url: str, same_domain: bool = True, filter_pattern: Optional[str] = None) -> List[str]:
        """
        Find all links on a page (useful for crawling).
        
        Args:
            url: URL to search for links
            same_domain: Only return links from the same domain
            filter_pattern: Optional pattern to filter URLs (e.g., '/docs/cloudbees-ci/')
            
        Returns:
            List of URLs
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            base_domain = urlparse(url).netloc
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                
                # Remove fragments
                parsed = urlparse(full_url)
                full_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    full_url += f"?{parsed.query}"
                
                # Apply domain filter
                if same_domain:
                    if urlparse(full_url).netloc != base_domain:
                        continue
                
                # Apply pattern filter
                if filter_pattern and filter_pattern not in full_url:
                    continue
                
                # Skip non-HTML files
                if any(full_url.lower().endswith(ext) for ext in ['.pdf', '.zip', '.jpg', '.png', '.gif', '.svg', '.css', '.js']):
                    continue
                
                links.append(full_url)
            
            return list(set(links))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error finding links on {url}: {e}")
            return []
    
    def crawl_documentation(self, 
                           start_url: str, 
                           max_pages: Optional[int] = None,
                           filter_pattern: str = "/docs/cloudbees-ci/") -> List[str]:
        """
        Crawl documentation site starting from a base URL.
        
        Args:
            start_url: Starting URL to crawl from
            max_pages: Maximum number of pages to crawl (None for unlimited)
            filter_pattern: Pattern to filter URLs (default: CloudBees CI docs)
            
        Returns:
            List of discovered URLs
        """
        visited: Set[str] = set()
        to_visit: deque = deque([start_url])
        discovered_urls: List[str] = []
        
        logger.info(f"Starting crawl from: {start_url}")
        logger.info(f"Filter pattern: {filter_pattern}")
        
        while to_visit and (max_pages is None or len(discovered_urls) < max_pages):
            current_url = to_visit.popleft()
            
            # Skip if already visited
            if current_url in visited:
                continue
            
            # Normalize URL (remove fragments, trailing slashes)
            parsed = urlparse(current_url)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
            if parsed.query:
                normalized += f"?{parsed.query}"
            
            if normalized in visited:
                continue
            
            visited.add(normalized)
            
            try:
                logger.info(f"Discovering links from: {normalized} ({len(discovered_urls)} pages found so far)")
                
                # Find links on this page
                links = self.find_links(normalized, same_domain=True, filter_pattern=filter_pattern)
                
                for link in links:
                    # Check limit before processing more links
                    if max_pages is not None and len(discovered_urls) >= max_pages:
                        break
                    
                    # Normalize the link too
                    link_parsed = urlparse(link)
                    link_normalized = f"{link_parsed.scheme}://{link_parsed.netloc}{link_parsed.path.rstrip('/')}"
                    if link_parsed.query:
                        link_normalized += f"?{link_parsed.query}"
                    
                    if link_normalized not in visited and link_normalized not in to_visit:
                        # Check if it matches our filter
                        if filter_pattern in link_normalized:
                            discovered_urls.append(link_normalized)
                            to_visit.append(link_normalized)
                            logger.debug(f"Found: {link_normalized}")
                
                # Check limit again after processing links from this page
                if max_pages is not None and len(discovered_urls) >= max_pages:
                    break
                
                time.sleep(self.delay)  # Be respectful
                
            except Exception as e:
                logger.error(f"Error crawling {normalized}: {e}")
                continue
        
        logger.info(f"Crawl complete! Found {len(discovered_urls)} documentation pages")
        return discovered_urls

