from typing import Dict, List, Optional
import json
from collections import defaultdict
from datetime import datetime
import os
from urllib.parse import urlparse
from src.config import DATA_DIR
from textblob import TextBlob
import re

class TestimonialAnalyzer:
    """Analyzer for processing and extracting insights from testimonials."""
    
    def __init__(self):
        self.product_keywords = {
            'crm': ['crm', 'sales hub', 'customer platform', 'sales software'],
            'marketing': ['marketing hub', 'marketing automation', 'content hub'],
            'service': ['service hub', 'customer service', 'support'],
            'operations': ['operations hub', 'operations software'],
            'commerce': ['commerce hub', 'b2b commerce']
        }
        
        self.benefit_keywords = {
            'efficiency': ['efficient', 'automation', 'automate', 'reduce manual work', 'save time'],
            'visibility': ['visibility', 'track', 'monitor', 'see', 'view'],
            'integration': ['integrate', 'connect', 'combine', 'unite'],
            'scalability': ['scale', 'growing', 'growth', 'expand'],
            'user_experience': ['easy to use', 'intuitive', 'user-friendly', 'simple'],
            'reporting': ['report', 'analytics', 'data', 'insights']
        }
        
        self.pain_point_keywords = {
            'manual_work': ['manual work', 'manual process', 'manual tasks'],
            'visibility_issues': ['lack of visibility', 'can\'t see', 'no visibility'],
            'integration_problems': ['disconnected', 'separate systems', 'not integrated'],
            'scaling_challenges': ['scaling issues', 'growth challenges', 'can\'t scale'],
            'complexity': ['complex', 'complicated', 'difficult to use']
        }
    
    def analyze_testimonials(self, data: Dict) -> Dict:
        """Analyze testimonials and generate insights."""
        testimonials = data.get('testimonials', [])
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_testimonials': len(testimonials),
            'product_mentions': self._analyze_product_mentions(testimonials),
            'benefits_mentioned': self._analyze_benefits(testimonials),
            'pain_points': self._analyze_pain_points(testimonials),
            'sentiment_analysis': self._analyze_sentiment(testimonials),
            'key_themes': self._extract_key_themes(testimonials),
            'customer_segments': self._analyze_customer_segments(testimonials)
        }
        
        # Save analysis results
        self._save_analysis(analysis, data['url'])
        
        return analysis
    
    def _analyze_product_mentions(self, testimonials: List[Dict]) -> Dict[str, int]:
        """Analyze which products are mentioned in testimonials."""
        mentions = defaultdict(int)
        
        for testimonial in testimonials:
            text = testimonial['text'].lower()
            for product, keywords in self.product_keywords.items():
                if any(keyword in text for keyword in keywords):
                    mentions[product] += 1
        
        return dict(mentions)
    
    def _analyze_benefits(self, testimonials: List[Dict]) -> Dict[str, List[str]]:
        """Analyze benefits mentioned in testimonials."""
        benefits = defaultdict(list)
        
        for testimonial in testimonials:
            text = testimonial['text'].lower()
            for benefit_type, keywords in self.benefit_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        # Extract the sentence containing the benefit
                        sentences = re.split(r'[.!?]+', text)
                        for sentence in sentences:
                            if keyword in sentence.lower():
                                benefits[benefit_type].append(sentence.strip())
        
        return dict(benefits)
    
    def _analyze_pain_points(self, testimonials: List[Dict]) -> Dict[str, List[str]]:
        """Analyze pain points mentioned in testimonials."""
        pain_points = defaultdict(list)
        
        for testimonial in testimonials:
            text = testimonial['text'].lower()
            for pain_type, keywords in self.pain_point_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        # Extract the sentence containing the pain point
                        sentences = re.split(r'[.!?]+', text)
                        for sentence in sentences:
                            if keyword in sentence.lower():
                                pain_points[pain_type].append(sentence.strip())
        
        return dict(pain_points)
    
    def _analyze_sentiment(self, testimonials: List[Dict]) -> Dict[str, float]:
        """Analyze sentiment of testimonials."""
        sentiments = []
        
        for testimonial in testimonials:
            blob = TextBlob(testimonial['text'])
            sentiments.append(blob.sentiment.polarity)
        
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            return {
                'average_sentiment': avg_sentiment,
                'positive_count': len([s for s in sentiments if s > 0]),
                'negative_count': len([s for s in sentiments if s < 0]),
                'neutral_count': len([s for s in sentiments if s == 0])
            }
        
        return {
            'average_sentiment': 0.0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0
        }
    
    def _extract_key_themes(self, testimonials: List[Dict]) -> List[str]:
        """Extract key themes from testimonials."""
        themes = defaultdict(int)
        
        # Common theme keywords
        theme_keywords = [
            'automation', 'efficiency', 'integration', 'scaling',
            'visibility', 'reporting', 'user experience', 'customer service',
            'growth', 'productivity', 'collaboration', 'data'
        ]
        
        for testimonial in testimonials:
            text = testimonial['text'].lower()
            for keyword in theme_keywords:
                if keyword in text:
                    themes[keyword] += 1
        
        # Sort themes by frequency and return top themes
        sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, count in sorted_themes[:5]]
    
    def _analyze_customer_segments(self, testimonials: List[Dict]) -> Dict[str, List[Dict]]:
        """Analyze testimonials by customer segments."""
        segments = defaultdict(list)
        
        for testimonial in testimonials:
            company = testimonial.get('company', '').lower()
            
            # Define segment keywords
            if any(word in company for word in ['inc', 'llc', 'corp', 'corporation']):
                segments['enterprise'].append(testimonial)
            elif any(word in company for word in ['startup', 'small business']):
                segments['small_business'].append(testimonial)
            elif any(word in company for word in ['agency', 'consulting']):
                segments['agency'].append(testimonial)
            else:
                segments['other'].append(testimonial)
        
        return dict(segments)
    
    def _save_analysis(self, analysis: Dict, url: str):
        """Save analysis results to JSON file."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        # Generate filename based on URL and timestamp
        domain = urlparse(url).netloc
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"testimonial_analysis_{domain}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False) 