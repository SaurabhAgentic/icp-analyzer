from typing import Dict, List, Optional
import json
from collections import defaultdict
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse
from src.config import DATA_DIR
from textblob import TextBlob
import re

class CompetitiveAnalyzer:
    """Analyzer for competitive intelligence and trend analysis."""
    
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
    
    def analyze_competitor(self, target_url: str, competitor_urls: List[str], days_back: int = 30) -> Dict:
        """Analyze competitor websites and compare with target company."""
        # Get target company data
        target_data = self._load_website_data(target_url)
        if not target_data:
            return {'error': f'No data found for target company: {target_url}'}
        
        # Get competitor data
        competitor_data = []
        for url in competitor_urls:
            data = self._load_website_data(url)
            if data:
                competitor_data.append({
                    'url': url,
                    'data': data
                })
        
        if not competitor_data:
            return {'error': 'No valid competitor data found'}
        
        # Generate competitive analysis
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'target_company': {
                'url': target_url,
                'analysis': self._analyze_website(target_data)
            },
            'competitors': [
                {
                    'url': comp['url'],
                    'analysis': self._analyze_website(comp['data'])
                }
                for comp in competitor_data
            ],
            'competitive_insights': self._generate_competitive_insights(
                target_data, [comp['data'] for comp in competitor_data]
            ),
            'trend_analysis': self._analyze_trends(target_url, days_back)
        }
        
        # Save analysis results
        self._save_analysis(analysis)
        
        return analysis
    
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
    
    def _generate_competitive_insights(self, target_data: Dict, competitor_data: List[Dict]) -> Dict:
        """Generate competitive insights by comparing target with competitors."""
        target_analysis = self._analyze_website(target_data)
        competitor_analyses = [self._analyze_website(comp) for comp in competitor_data]
        
        insights = {
            'market_positioning': self._analyze_market_positioning(target_analysis, competitor_analyses),
            'competitive_advantages': self._find_competitive_advantages(target_analysis, competitor_analyses),
            'market_gaps': self._identify_market_gaps(target_analysis, competitor_analyses),
            'customer_segment_overlap': self._analyze_customer_segment_overlap(target_analysis, competitor_analyses)
        }
        
        return insights
    
    def _analyze_market_positioning(self, target: Dict, competitors: List[Dict]) -> Dict:
        """Analyze market positioning differences."""
        positioning = {
            'product_focus': self._compare_product_focus(target, competitors),
            'benefit_emphasis': self._compare_benefit_emphasis(target, competitors),
            'customer_segment_focus': self._compare_customer_segment_focus(target, competitors)
        }
        
        return positioning
    
    def _compare_product_focus(self, target: Dict, competitors: List[Dict]) -> Dict:
        """Compare product focus between target and competitors."""
        target_products = set(target['product_mentions'].keys())
        competitor_products = set()
        for comp in competitors:
            competitor_products.update(comp['product_mentions'].keys())
        
        return {
            'unique_to_target': list(target_products - competitor_products),
            'unique_to_competitors': list(competitor_products - target_products),
            'common_products': list(target_products & competitor_products)
        }
    
    def _compare_benefit_emphasis(self, target: Dict, competitors: List[Dict]) -> Dict:
        """Compare benefit emphasis between target and competitors."""
        target_benefits = set(target['benefits_mentioned'].keys())
        competitor_benefits = set()
        for comp in competitors:
            competitor_benefits.update(comp['benefits_mentioned'].keys())
        
        return {
            'unique_to_target': list(target_benefits - competitor_benefits),
            'unique_to_competitors': list(competitor_benefits - target_benefits),
            'common_benefits': list(target_benefits & competitor_benefits)
        }
    
    def _compare_customer_segment_focus(self, target: Dict, competitors: List[Dict]) -> Dict:
        """Compare customer segment focus between target and competitors."""
        target_segments = set(target['customer_segments'].keys())
        competitor_segments = set()
        for comp in competitors:
            competitor_segments.update(comp['customer_segments'].keys())
        
        return {
            'unique_to_target': list(target_segments - competitor_segments),
            'unique_to_competitors': list(competitor_segments - target_segments),
            'common_segments': list(target_segments & competitor_segments)
        }
    
    def _find_competitive_advantages(self, target: Dict, competitors: List[Dict]) -> List[str]:
        """Find competitive advantages of the target company."""
        advantages = []
        
        # Compare sentiment
        target_sentiment = target['sentiment_analysis']['average_sentiment']
        competitor_sentiments = [comp['sentiment_analysis']['average_sentiment'] for comp in competitors]
        if target_sentiment > max(competitor_sentiments):
            advantages.append('Higher customer satisfaction')
        
        # Compare unique benefits
        target_benefits = set(target['benefits_mentioned'].keys())
        competitor_benefits = set()
        for comp in competitors:
            competitor_benefits.update(comp['benefits_mentioned'].keys())
        
        unique_benefits = target_benefits - competitor_benefits
        if unique_benefits:
            advantages.append(f'Unique benefits: {", ".join(unique_benefits)}')
        
        # Compare customer segments
        target_segments = set(target['customer_segments'].keys())
        competitor_segments = set()
        for comp in competitors:
            competitor_segments.update(comp['customer_segments'].keys())
        
        unique_segments = target_segments - competitor_segments
        if unique_segments:
            advantages.append(f'Unique customer segments: {", ".join(unique_segments)}')
        
        return advantages
    
    def _identify_market_gaps(self, target: Dict, competitors: List[Dict]) -> List[str]:
        """Identify market gaps and opportunities."""
        gaps = []
        
        # Find pain points not addressed by target
        target_pain_points = set(target['pain_points'].keys())
        competitor_pain_points = set()
        for comp in competitors:
            competitor_pain_points.update(comp['pain_points'].keys())
        
        unaddressed_pain_points = competitor_pain_points - target_pain_points
        if unaddressed_pain_points:
            gaps.append(f'Unaddressed pain points: {", ".join(unaddressed_pain_points)}')
        
        # Find underserved customer segments
        target_segments = set(target['customer_segments'].keys())
        competitor_segments = set()
        for comp in competitors:
            competitor_segments.update(comp['customer_segments'].keys())
        
        underserved_segments = competitor_segments - target_segments
        if underserved_segments:
            gaps.append(f'Underserved customer segments: {", ".join(underserved_segments)}')
        
        return gaps
    
    def _analyze_customer_segment_overlap(self, target: Dict, competitors: List[Dict]) -> Dict:
        """Analyze customer segment overlap between target and competitors."""
        overlap = defaultdict(list)
        
        target_segments = target['customer_segments']
        for comp in competitors:
            comp_segments = comp['customer_segments']
            for segment in set(target_segments.keys()) & set(comp_segments.keys()):
                overlap[segment].append({
                    'competitor_url': comp['url'],
                    'target_count': len(target_segments[segment]),
                    'competitor_count': len(comp_segments[segment])
                })
        
        return dict(overlap)
    
    def _analyze_trends(self, url: str, days_back: int) -> Dict:
        """Analyze trends in testimonials over time."""
        domain = urlparse(url).netloc
        files = [f for f in os.listdir(DATA_DIR) 
                if f.startswith('testimonial_analysis_') 
                and domain in f 
                and f.endswith('.json')]
        
        if not files:
            return {'error': 'No historical data found'}
        
        # Get files within the specified time range
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_files = []
        for filename in files:
            filepath = os.path.join(DATA_DIR, filename)
            if datetime.fromtimestamp(os.path.getctime(filepath)) >= cutoff_date:
                recent_files.append(filepath)
        
        if not recent_files:
            return {'error': 'No data found within specified time range'}
        
        # Analyze trends
        trends = {
            'sentiment_trend': self._analyze_sentiment_trend(recent_files),
            'theme_trends': self._analyze_theme_trends(recent_files),
            'product_trends': self._analyze_product_trends(recent_files),
            'customer_segment_trends': self._analyze_customer_segment_trends(recent_files)
        }
        
        return trends
    
    def _analyze_sentiment_trend(self, files: List[str]) -> Dict:
        """Analyze sentiment trends over time."""
        sentiments = []
        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                analysis = self._analyze_website(data)
                sentiments.append({
                    'date': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                    'sentiment': analysis['sentiment_analysis']['average_sentiment']
                })
        
        # Sort by date
        sentiments.sort(key=lambda x: x['date'])
        
        return {
            'trend': 'increasing' if sentiments[-1]['sentiment'] > sentiments[0]['sentiment'] else 'decreasing',
            'data': sentiments
        }
    
    def _analyze_theme_trends(self, files: List[str]) -> Dict:
        """Analyze theme trends over time."""
        theme_counts = defaultdict(lambda: defaultdict(int))
        
        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                analysis = self._analyze_website(data)
                date = datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                for theme in analysis['key_themes']:
                    theme_counts[theme][date] += 1
        
        return dict(theme_counts)
    
    def _analyze_product_trends(self, files: List[str]) -> Dict:
        """Analyze product mention trends over time."""
        product_counts = defaultdict(lambda: defaultdict(int))
        
        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                analysis = self._analyze_website(data)
                date = datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                for product, count in analysis['product_mentions'].items():
                    product_counts[product][date] = count
        
        return dict(product_counts)
    
    def _analyze_customer_segment_trends(self, files: List[str]) -> Dict:
        """Analyze customer segment trends over time."""
        segment_counts = defaultdict(lambda: defaultdict(int))
        
        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                analysis = self._analyze_website(data)
                date = datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                for segment, testimonials in analysis['customer_segments'].items():
                    segment_counts[segment][date] = len(testimonials)
        
        return dict(segment_counts)
    
    def _save_analysis(self, analysis: Dict):
        """Save analysis results to JSON file."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"competitive_analysis_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
    
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