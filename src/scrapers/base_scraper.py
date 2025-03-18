import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
from urllib.parse import urljoin, urlparse
import time
from src.config import DEFAULT_TIMEOUT, MAX_RETRIES

class BaseScraper:
    """Base class for web scraping with common functionality."""
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, max_retries: int = MAX_RETRIES):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {url}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
        return None
    
    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Get BeautifulSoup object from URL."""
        response = self._make_request(url)
        if response:
            return BeautifulSoup(response.text, 'html.parser')
        return None
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalize URL by joining with base URL if necessary."""
        if not self._is_valid_url(url):
            return urljoin(base_url, url)
        return url
    
    def _extract_text(self, element) -> str:
        """Extract text from HTML element, handling nested elements."""
        if not element:
            return ""
        return " ".join(text.strip() for text in element.stripped_strings)
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page."""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            normalized_url = self._normalize_url(href, base_url)
            if self._is_valid_url(normalized_url):
                links.append(normalized_url)
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images with their alt text."""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                normalized_src = self._normalize_url(src, base_url)
                images.append({
                    'src': normalized_src,
                    'alt': alt
                })
        return images 