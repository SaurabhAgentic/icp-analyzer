import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
import platform
from urllib.parse import urljoin

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def scrape_website(self, url: str) -> Dict[str, str]:
        """
        Scrape website content including main text, meta descriptions, and relevant sections
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        try:
            self.logger.info(f"Scraping content from {url}")
            
            # Get main page content
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an error for bad status codes
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract relevant content
            content = {
                'title': self._get_title(soup),
                'meta_description': self._get_meta_description(soup),
                'main_content': self._get_main_content(soup),
                'about_page': self._get_about_page_content(url),
                'target_sections': self._get_target_sections(soup)
            }
            
            self.logger.info("Successfully scraped website content")
            return content
            
        except Exception as e:
            self.logger.error(f"Error scraping website {url}: {str(e)}")
            return {}
            
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title = soup.find('title')
        return title.text.strip() if title else ""
        
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'}) or \
               soup.find('meta', attrs={'property': 'og:description'})
        return meta.get('content', "").strip() if meta else ""
        
    def _get_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page"""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript", "iframe", "head"]):
            script.decompose()
            
        # Get text from main content areas
        main_content = []
        
        # Common content container selectors
        content_selectors = [
            'main',
            'article',
            '#main-content',
            '.main-content',
            '.content',
            '[role="main"]',
            '.hero-section',
            '.landing-page',
            '.homepage-content'
        ]
        
        # Try to get content from specific sections first
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                main_content.append(content_area.get_text(strip=True, separator=' '))
        
        # If no specific content areas found, get all text
        if not main_content:
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            main_content = [' '.join(line for line in lines if line)]
        
        return ' '.join(main_content)
        
    def _get_about_page_content(self, base_url: str) -> str:
        """Try to scrape the about page content"""
        about_paths = [
            '/about',
            '/about-us',
            '/company',
            '/who-we-are',
            '/our-story'
        ]
        
        for path in about_paths:
            try:
                about_url = urljoin(base_url, path)
                self.logger.info(f"Trying to fetch about page: {about_url}")
                
                response = requests.get(about_url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return self._get_main_content(soup)
            except Exception as e:
                self.logger.debug(f"Failed to fetch {about_url}: {str(e)}")
                continue
                
        return ""
        
    def _get_target_sections(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract content from sections likely to contain ICP information"""
        target_sections = {}
        
        # Common class names and IDs that might contain ICP information
        selectors = [
            '.customers', '#customers',
            '.solutions', '#solutions',
            '.industries', '#industries',
            '.target-audience', '#target-audience',
            '.benefits', '#benefits',
            '.features', '#features',
            '.pricing', '#pricing',
            '.enterprise', '#enterprise',
            '.use-cases', '#use-cases'
        ]
        
        for selector in selectors:
            sections = soup.select(selector)
            if sections:
                # Combine text from all matching sections
                text = ' '.join(section.get_text(strip=True, separator=' ') for section in sections)
                if text:
                    target_sections[selector.lstrip('.#')] = text
                
        return target_sections 