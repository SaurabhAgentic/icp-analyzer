from typing import Dict, List, Optional
import json
from collections import defaultdict
from datetime import datetime
import os
from urllib.parse import urlparse
from src.config import DATA_DIR
from textblob import TextBlob
import re

class ComparativeAnalyzer:
    """Analyzer for comparing testimonials across multiple websites."""
    
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
    
    def compare_websites(self, urls: List[str]) -> Dict:
        """Compare testimonials across multiple websites."""
        analyses = []
        
        # Load and analyze each website's data
        for url in urls:
            data = self._load_website_data(url)
            if data:
                analysis = self._analyze_website(data)
                analysis['url'] = url
                analyses.append(analysis)
        
        if not analyses:
            return {'error': 'No valid data found for comparison'}
        
        # Generate comparative analysis
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'websites': analyses,
            'comparative_metrics': self._generate_comparative_metrics(analyses),
            'common_themes': self._find_common_themes(analyses),
            'unique_insights': self._find_unique_insights(analyses)
        }
        
        # Save comparison results
        self._save_comparison(comparison)
        
        return comparison
    
    def _load_website_data(self, url: str) -> Optional[Dict]:
        """Load website data from the most recent analysis file."""
        domain = urlparse(url).netloc
        files = [f for f in os.listdir(DATA_DIR) 
                if f.startswith('testimonial_analysis_') 
                and domain in f 
                and f.endswith('.json')]
        
        if not files:
            return None
        
        # Get the most recent file
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(DATA_DIR, x)))
        filepath = os.path.join(DATA_DIR, latest_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _analyze_website(self, data: Dict) -> Dict:
        """Analyze a single website's testimonials."""
        testimonials = data.get('testimonials', [])
        
        return {
            'total_testimonials': len(testimonials),
            'product_mentions': self._analyze_product_mentions(testimonials),
            'benefits_mentioned': self._analyze_benefits(testimonials),
            'pain_points': self._analyze_pain_points(testimonials),
            'sentiment_analysis': self._analyze_sentiment(testimonials),
            'key_themes': self._extract_key_themes(testimonials),
            'customer_segments': self._analyze_customer_segments(testimonials)
        }
    
    def _generate_comparative_metrics(self, analyses: List[Dict]) -> Dict:
        """Generate metrics comparing the websites."""
        metrics = {
            'total_testimonials': {
                'min': min(a['total_testimonials'] for a in analyses),
                'max': max(a['total_testimonials'] for a in analyses),
                'average': sum(a['total_testimonials'] for a in analyses) / len(analyses)
            },
            'sentiment_comparison': {
                'most_positive': max(analyses, key=lambda x: x['sentiment_analysis']['average_sentiment'])['url'],
                'most_negative': min(analyses, key=lambda x: x['sentiment_analysis']['average_sentiment'])['url']
            },
            'product_mentions_comparison': self._compare_product_mentions(analyses),
            'customer_segments_comparison': self._compare_customer_segments(analyses)
        }
        
        return metrics
    
    def _compare_product_mentions(self, analyses: List[Dict]) -> Dict:
        """Compare product mentions across websites."""
        comparison = defaultdict(list)
        
        for analysis in analyses:
            url = analysis['url']
            for product, count in analysis['product_mentions'].items():
                comparison[product].append({
                    'url': url,
                    'count': count
                })
        
        return dict(comparison)
    
    def _compare_customer_segments(self, analyses: List[Dict]) -> Dict:
        """Compare customer segments across websites."""
        comparison = defaultdict(list)
        
        for analysis in analyses:
            url = analysis['url']
            for segment, testimonials in analysis['customer_segments'].items():
                comparison[segment].append({
                    'url': url,
                    'count': len(testimonials)
                })
        
        return dict(comparison)
    
    def _find_common_themes(self, analyses: List[Dict]) -> List[str]:
        """Find themes common across all websites."""
        theme_counts = defaultdict(int)
        
        for analysis in analyses:
            for theme in analysis['key_themes']:
                theme_counts[theme] += 1
        
        # Return themes that appear in at least 50% of the websites
        threshold = len(analyses) * 0.5
        return [theme for theme, count in theme_counts.items() if count >= threshold]
    
    def _find_unique_insights(self, analyses: List[Dict]) -> Dict[str, List[str]]:
        """Find insights unique to each website."""
        unique_insights = defaultdict(list)
        
        for analysis in analyses:
            url = analysis['url']
            
            # Find unique benefits
            for benefit_type, quotes in analysis['benefits_mentioned'].items():
                if quotes:
                    unique_insights[url].append(f"Unique benefit: {benefit_type}")
            
            # Find unique pain points
            for pain_type, quotes in analysis['pain_points'].items():
                if quotes:
                    unique_insights[url].append(f"Unique pain point: {pain_type}")
            
            # Find unique product mentions
            for product, count in analysis['product_mentions'].items():
                if count > 0:
                    unique_insights[url].append(f"Unique product mention: {product}")
        
        return dict(unique_insights)
    
    def _save_comparison(self, comparison: Dict):
        """Save comparison results to JSON file."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"comparative_analysis_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    # Reuse existing analysis methods from TestimonialAnalyzer
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
        
        sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, count in sorted_themes[:5]]
    
    def _analyze_customer_segments(self, testimonials: List[Dict]) -> Dict[str, List[Dict]]:
        """Analyze testimonials by customer segments."""
        segments = defaultdict(list)
        
        for testimonial in testimonials:
            company = testimonial.get('company', '').lower()
            
            if any(word in company for word in ['inc', 'llc', 'corp', 'corporation']):
                segments['enterprise'].append(testimonial)
            elif any(word in company for word in ['startup', 'small business']):
                segments['small_business'].append(testimonial)
            elif any(word in company for word in ['agency', 'consulting']):
                segments['agency'].append(testimonial)
            else:
                segments['other'].append(testimonial)
        
        return dict(segments) 