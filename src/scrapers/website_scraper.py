from typing import Dict, List, Optional
from bs4 import BeautifulSoup, Tag
from src.scrapers.base_scraper import BaseScraper
import json
from datetime import datetime
import os
from urllib.parse import urlparse, urljoin
from src.config import DATA_DIR
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class WebsiteScraper(BaseScraper):
    """Scraper for extracting customer profile relevant content from websites."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_sections = {
            'about': ['about', 'company', 'mission', 'team', 'story'],
            'products': ['products', 'solutions', 'features', 'platform', 'tools'],
            'pricing': ['pricing', 'plans', 'packages', 'subscription'],
            'testimonials': ['testimonials', 'reviews', 'customers', 'success stories'],
            'contact': ['contact', 'support', 'help']
        }
        self.case_study_urls = [
            '/customers',
            '/case-studies',
            '/customer-stories',
            '/success-stories',
            '/testimonials'
        ]
    
    def scrape_website(self, url: str) -> Dict:
        """Main method to scrape website content."""
        try:
            # First try with regular requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()

            # Extract base data
            data = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'title': self._extract_title(soup),
                'meta_description': self._extract_meta_description(soup),
                'sections': self._extract_sections(soup),
                'testimonials': [],
                'stats': self._extract_stats(soup),
                'value_props': self._extract_value_props(soup),
                'images': self._extract_images(soup),
                'links': self._extract_links(soup)
            }

            # Try to get dynamic content with Selenium
            dynamic_testimonials = self._get_dynamic_testimonials(url)
            if dynamic_testimonials:
                data['testimonials'].extend(dynamic_testimonials)

            # Try to get testimonials from case studies
            case_study_testimonials = self._get_case_study_testimonials(url)
            if case_study_testimonials:
                data['testimonials'].extend(case_study_testimonials)

            # Try to get testimonials from embedded content
            embedded_testimonials = self._get_embedded_testimonials(soup)
            if embedded_testimonials:
                data['testimonials'].extend(embedded_testimonials)

            # Save raw data
            self._save_raw_data(data)
            return data

        except Exception as e:
            print(f"Error occurred while scraping: {str(e)}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ''
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ''
    
    def _clean_text(self, text):
        """Clean extracted text by removing extra whitespace and unwanted content."""
        if not text:
            return ''
        
        # Remove script and style content
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove CSS-like content
        text = re.sub(r'\{[^}]*\}', '', text)
        text = re.sub(r'[a-z-]+:[^;]+;', '', text)
        
        # Remove special characters and normalize whitespace
        text = re.sub(r'[\n\t\r]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Skip if text starts with programming keywords
        if text.lower().startswith(('var ', 'function ', 'class ')):
            return ''
        
        return text
    
    def _extract_sections(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract content from different sections of the website."""
        sections = {}
        
        for section_type, keywords in self.content_sections.items():
            section_content = []
            
            # Find sections by ID or class containing keywords
            for keyword in keywords:
                # Look for elements with matching ID or class
                elements = soup.find_all(lambda tag: (
                    tag.get('id', '').lower().find(keyword) >= 0 or
                    any(keyword in cls.lower() for cls in tag.get('class', []))
                ) and len(tag.get_text().strip()) > 50)
                
                for element in elements:
                    # Skip if element contains mostly CSS/styling content
                    if len(re.findall(r'[{};]', str(element))) > 10:
                        continue
                        
                    text = self._clean_text(element.get_text())
                    if text and len(text) > 50:  # Only include substantial content
                        section_content.append(text)
            
            # Look for headings containing keywords
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                if any(keyword in heading.get_text().lower() for keyword in keywords):
                    content = self._get_content_after_heading(heading)
                    if content:
                        section_content.append(content)
            
            if section_content:
                # Remove duplicates while preserving order
                seen = set()
                unique_content = []
                for content in section_content:
                    if content not in seen and not content.startswith(('var', 'function', 'class')):
                        seen.add(content)
                        unique_content.append(content)
                sections[section_type] = ' '.join(unique_content)
        
        return sections
    
    def _get_content_after_heading(self, heading: Tag) -> Optional[str]:
        """Get content between this heading and the next heading."""
        content = []
        current = heading.find_next_sibling()
        
        while current and current.name not in ['h1', 'h2', 'h3']:
            if current.name in ['p', 'div', 'section'] and not current.find_parent('nav'):
                # Skip if element contains mostly CSS/styling content
                if len(re.findall(r'[{};]', str(current))) > 10:
                    current = current.find_next_sibling()
                    continue
                    
                text = self._clean_text(current.get_text())
                if text and len(text) > 30 and not text.startswith(('var', 'function', 'class')):
                    content.append(text)
            current = current.find_next_sibling()
        
        return ' '.join(content) if content else None
    
    def _get_dynamic_testimonials(self, url: str) -> List[Dict]:
        """Extract testimonials from dynamically loaded content using Selenium."""
        testimonials = []
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for dynamic content to load
            time.sleep(5)
            
            # Look for testimonial elements
            testimonial_elements = driver.find_elements(By.CSS_SELECTOR, 
                '[class*="testimonial"], [class*="review"], [class*="quote"], [class*="customer-story"]')
            
            for element in testimonial_elements:
                try:
                    # Wait for element to be visible
                    WebDriverWait(driver, 5).until(
                        EC.visibility_of(element)
                    )
                    
                    # Extract testimonial content
                    text = element.text.strip()
                    if text and len(text) > 30:
                        testimonial = {
                            'text': text,
                            'author': '',
                            'company': ''
                        }
                        
                        # Try to find author and company
                        author_elem = element.find_element(By.CSS_SELECTOR, 
                            '[class*="author"], [class*="name"], [class*="customer"]')
                        if author_elem:
                            testimonial['author'] = author_elem.text.strip()
                            
                        company_elem = element.find_element(By.CSS_SELECTOR, 
                            '[class*="company"], [class*="organization"]')
                        if company_elem:
                            testimonial['company'] = company_elem.text.strip()
                            
                        testimonials.append(testimonial)
                except:
                    continue
                    
            driver.quit()
        except Exception as e:
            print(f"Error getting dynamic testimonials: {str(e)}")
            
        return testimonials

    def _get_case_study_testimonials(self, base_url: str) -> List[Dict]:
        """Extract testimonials from case studies and customer stories pages."""
        testimonials = []
        try:
            # Try each case study URL pattern
            for path in self.case_study_urls:
                url = urljoin(base_url, path)
                try:
                    response = requests.get(url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for testimonial elements
                    for element in soup.find_all(['div', 'article', 'section'], 
                        class_=lambda x: x and any(word in str(x).lower() for word in ['testimonial', 'review', 'quote', 'case-study'])):
                        
                        text = self._clean_text(element.get_text())
                        if text and len(text) > 30:
                            testimonial = {
                                'text': text,
                                'author': '',
                                'company': ''
                            }
                            
                            # Try to find author and company
                            author_elem = element.find(['span', 'div', 'p'], 
                                class_=lambda x: x and any(word in str(x).lower() for word in ['author', 'name', 'customer']))
                            if author_elem:
                                testimonial['author'] = self._clean_text(author_elem.get_text())
                                
                            company_elem = element.find(['span', 'div', 'p'], 
                                class_=lambda x: x and any(word in str(x).lower() for word in ['company', 'organization']))
                            if company_elem:
                                testimonial['company'] = self._clean_text(company_elem.get_text())
                                
                            testimonials.append(testimonial)
                            
                except:
                    continue
                    
        except Exception as e:
            print(f"Error getting case study testimonials: {str(e)}")
            
        return testimonials

    def _get_embedded_testimonials(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract testimonials from embedded content like videos, iframes, and embedded players."""
        testimonials = []
        
        # Common video platforms and their patterns
        video_platforms = {
            'youtube': r'youtube\.com|youtu\.be',
            'vimeo': r'vimeo\.com',
            'wistia': r'wistia\.com',
            'vidyard': r'vidyard\.com',
            'brightcove': r'brightcove\.net'
        }
        
        # Look for video elements and iframes
        for element in soup.find_all(['video', 'iframe', 'div']):
            try:
                # Check if element is a video player
                src = element.get('src', '')
                data_src = element.get('data-src', '')
                video_url = src or data_src
                
                # Check various video-related attributes
                video_attrs = {
                    'src': video_url,
                    'data-video-id': element.get('data-video-id', ''),
                    'data-player-id': element.get('data-player-id', ''),
                    'class': ' '.join(element.get('class', [])),
                    'id': element.get('id', ''),
                    'title': element.get('title', '')
                }
                
                # Check if this is a known video platform embed
                is_video_platform = any(
                    re.search(pattern, video_url, re.I) 
                    for pattern in video_platforms.values()
                )
                
                # Check if element contains testimonial indicators
                testimonial_indicators = [
                    'testimonial', 'review', 'customer story', 'success story',
                    'case study', 'customer testimonial', 'client story'
                ]
                
                is_testimonial = any(
                    indicator in str(element).lower() 
                    for indicator in testimonial_indicators
                )
                
                if is_video_platform and is_testimonial:
                    # Extract metadata from the video element
                    metadata = {}
                    
                    # Try to get video title
                    title_elem = element.find_parent(['div', 'section']).find(
                        ['h1', 'h2', 'h3', 'h4', '.title', '.video-title']
                    ) if element.find_parent(['div', 'section']) else None
                    
                    if title_elem:
                        metadata['title'] = self._clean_text(title_elem.get_text())
                    
                    # Try to get video description
                    desc_elem = element.find_parent(['div', 'section']).find(
                        ['p', '.description', '.video-description']
                    ) if element.find_parent(['div', 'section']) else None
                    
                    if desc_elem:
                        metadata['description'] = self._clean_text(desc_elem.get_text())
                    
                    # Try to get customer/company info
                    customer_elem = element.find_parent(['div', 'section']).find(
                        ['p', 'div', 'span'],
                        class_=lambda x: x and any(term in str(x).lower() for term in ['customer', 'company', 'client'])
                    ) if element.find_parent(['div', 'section']) else None
                    
                    if customer_elem:
                        customer_text = self._clean_text(customer_elem.get_text())
                        if ' at ' in customer_text:
                            author, company = customer_text.split(' at ', 1)
                        elif ' from ' in customer_text:
                            author, company = customer_text.split(' from ', 1)
                        else:
                            author = customer_text
                            company = 'Unknown'
                    else:
                        author = 'Anonymous'
                        company = 'Unknown'
                    
                    # Construct testimonial text from available metadata
                    testimonial_text = []
                    if metadata.get('title'):
                        testimonial_text.append(metadata['title'])
                    if metadata.get('description'):
                        testimonial_text.append(metadata['description'])
                    
                    text = ' '.join(testimonial_text)
                    if text and len(text) > 30:
                        testimonials.append({
                            'text': text,
                            'author': author,
                            'company': company,
                            'source': 'video',
                            'platform': next(
                                (platform for platform, pattern in video_platforms.items() 
                                 if re.search(pattern, video_url, re.I)),
                                'unknown'
                            )
                        })
                
                # Check for embedded testimonial widgets
                elif element.name == 'iframe':
                    widget_indicators = [
                        'trustpilot', 'g2crowd', 'capterra', 'reviews', 
                        'testimonials', 'feedback'
                    ]
                    
                    if any(indicator in str(element).lower() for indicator in widget_indicators):
                        # Try to get content from the iframe's parent container
                        parent = element.find_parent(['div', 'section'])
                        if parent:
                            # Look for review/testimonial text
                            review_elems = parent.find_all(
                                ['div', 'p'],
                                class_=lambda x: x and any(term in str(x).lower() for term in ['review', 'testimonial', 'feedback'])
                            )
                            
                            for review in review_elems:
                                text = self._clean_text(review.get_text())
                                if text and len(text) > 30:
                                    # Try to find author/company info
                                    author_elem = review.find_next(
                                        ['div', 'span', 'p'],
                                        class_=lambda x: x and any(term in str(x).lower() for term in ['author', 'reviewer', 'customer'])
                                    )
                                    
                                    if author_elem:
                                        author_text = self._clean_text(author_elem.get_text())
                                        if ' at ' in author_text:
                                            author, company = author_text.split(' at ', 1)
                                        elif ' from ' in author_text:
                                            author, company = author_text.split(' from ', 1)
                                        else:
                                            author = author_text
                                            company = 'Unknown'
                                    else:
                                        author = 'Anonymous'
                                        company = 'Unknown'
                                    
                                    testimonials.append({
                                        'text': text,
                                        'author': author,
                                        'company': company,
                                        'source': 'review_widget'
                                    })
            
            except Exception as e:
                print(f"Error processing embedded content: {str(e)}")
                continue
        
        return testimonials
    
    def _extract_stats(self, soup: BeautifulSoup) -> List[str]:
        """Extract statistical claims and metrics."""
        stats = []
        stat_elements = soup.find_all(
            ['div', 'p', 'span'],
            class_=lambda x: x and any(word in str(x).lower() for word in ['stat', 'metric', 'number', 'figure'])
        )
        
        for element in stat_elements:
            # Skip if element contains mostly CSS/styling content
            if len(re.findall(r'[{};]', str(element))) > 10:
                continue
            
            text = self._clean_text(element.get_text())
            if text and any(char.isdigit() for char in text) and not text.startswith(('var', 'function', 'class')):
                stats.append(text)
        
        return stats
    
    def _extract_value_props(self, soup: BeautifulSoup) -> List[str]:
        """Extract value propositions and key benefits."""
        value_props = []
        
        # Look for elements that typically contain value propositions
        elements = soup.find_all(
            ['div', 'section', 'li'],
            class_=lambda x: x and any(word in str(x).lower() for word in ['feature', 'benefit', 'value', 'advantage'])
        )
        
        for element in elements:
            # Skip if element contains mostly CSS/styling content
            if len(re.findall(r'[{};]', str(element))) > 10:
                continue
            
            # Look for headings or strong text within these elements
            props = element.find_all(['h2', 'h3', 'h4', 'strong', 'p'])
            for prop in props:
                text = self._clean_text(prop.get_text())
                if text and len(text) > 10 and not text.startswith(('var', 'function', 'class')):
                    value_props.append(text)
        
        return value_props
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract images from the website."""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src and not src.startswith('data:'):  # Exclude base64 encoded images
                images.append({'src': src, 'alt': alt})
        return images
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract links from the website."""
        links = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = self._clean_text(link.get_text())
            if href and text and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                links.append({'href': href, 'text': text})
        return links
    
    def _save_raw_data(self, content: Dict):
        """Save raw scraped data to JSON file."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        # Generate filename based on URL and timestamp
        domain = urlparse(content['url']).netloc
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"icp_analysis_{domain}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    def _extract_testimonials(self, soup):
        """Extract testimonials from the page."""
        testimonials = []
        seen_quotes = set()  # Track unique quotes
        
        # Common patterns for testimonial sections
        testimonial_patterns = [
            'testimonial', 'review', 'quote', 'customer-story',
            'success-story', 'case-study', 'customer-quote'
        ]
        
        # Find all potential testimonial sections
        for pattern in testimonial_patterns:
            sections = soup.find_all(class_=lambda x: x and pattern.lower() in x.lower())
            sections.extend(soup.find_all(id=lambda x: x and pattern.lower() in x.lower()))
            sections.extend(soup.find_all('blockquote'))
            sections.extend(soup.find_all('q'))
            
            for section in sections:
                # Skip if section contains mostly CSS/styling content
                if self._is_css_content(section.get_text()):
                    continue
                    
                # Extract quote text
                quote_text = self._clean_text(section.get_text())
                if not quote_text or len(quote_text) < 30:  # Skip very short quotes
                    continue
                    
                # Skip if we've seen this quote before
                normalized_quote = quote_text.lower().strip()
                if normalized_quote in seen_quotes:
                    continue
                seen_quotes.add(normalized_quote)
                
                # Extract author and company information
                author = ''
                company = ''
                
                # Look for author/company in nearby elements
                author_elements = section.find_all(class_=lambda x: x and any(p in x.lower() for p in ['author', 'name', 'title']))
                company_elements = section.find_all(class_=lambda x: x and any(p in x.lower() for p in ['company', 'organization', 'firm']))
                
                if author_elements:
                    author = self._clean_text(author_elements[0].get_text())
                if company_elements:
                    company = self._clean_text(company_elements[0].get_text())
                
                # If no explicit company found, try to extract from combined string
                if author and not company:
                    parts = author.split(',')  # Try comma separation
                    if len(parts) > 1:
                        author = parts[0].strip()
                        company = parts[-1].strip()
                    else:
                        # Try to extract company from position/title
                        parts = author.split('at')
                        if len(parts) > 1:
                            author = parts[0].strip()
                            company = parts[1].strip()
                        else:
                            # Look for common position indicators
                            position_indicators = ['Director', 'Manager', 'VP', 'CEO', 'President', 'Head']
                            for indicator in position_indicators:
                                if indicator in author:
                                    parts = author.split(indicator)
                                    if len(parts) > 1:
                                        company = parts[-1].strip(' of ').strip()
                                        author = parts[0].strip() + ' ' + indicator
                                        break
                
                # Clean up company name
                if company:
                    # Remove position titles from company
                    position_words = ['Director', 'Manager', 'VP', 'CEO', 'President', 'Head', 'of', 'Marketing', 'Sales']
                    company_parts = company.split()
                    company = ' '.join(word for word in company_parts if word not in position_words)
                    company = company.strip()
                
                testimonials.append({
                    'quote': quote_text,
                    'author': author,
                    'company': company
                })
        
        return testimonials 