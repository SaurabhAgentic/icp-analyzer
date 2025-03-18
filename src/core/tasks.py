from celery import Celery
from typing import List, Dict, Any
import os
from datetime import datetime
import json
import requests
from src.scrapers.website_scraper import WebsiteScraper
from src.analyzers.testimonial_analyzer import TestimonialAnalyzer
from src.analyzers.comparative_analyzer import ComparativeAnalyzer
from src.analyzers.competitive_analyzer import CompetitiveAnalyzer
from src.analyzers.advanced_analyzer import AdvancedAnalyzer
from src.reporting.report_generator import ReportGenerator
from src.core.cache import cache, ANALYSIS_KEY_PATTERN, REPORT_KEY_PATTERN

# Initialize Celery
celery_app = Celery(
    'icp_analyzer',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1
)

@celery_app.task(bind=True)
def analyze_website(self, urls: List[str], analysis_type: str, days_back: int = 30, include_advanced: bool = False) -> Dict[str, Any]:
    """Background task for website analysis."""
    try:
        # Update task state
        self.update_state(state='SCRAPING', meta={'current': 0, 'total': len(urls)})
        
        # Scrape websites
        scraper = WebsiteScraper()
        all_testimonials = []
        for i, url in enumerate(urls):
            data = scraper.scrape_website(url)
            if not data:
                raise Exception(f'Failed to scrape website: {url}')
            all_testimonials.extend(data['testimonials'])
            self.update_state(state='SCRAPING', meta={'current': i + 1, 'total': len(urls)})
        
        # Update task state
        self.update_state(state='ANALYZING', meta={'current': 0, 'total': 1})
        
        # Perform analysis based on type
        if analysis_type == 'single':
            analyzer = TestimonialAnalyzer()
            analysis = analyzer.analyze_testimonials(all_testimonials)
            
            if include_advanced:
                advanced_analyzer = AdvancedAnalyzer()
                advanced_results = advanced_analyzer.analyze_testimonials(all_testimonials)
                analysis['advanced_analysis'] = advanced_results
            
            # Cache results
            cache_key = f"analysis:{datetime.now().isoformat()}"
            cache.set(cache_key, analysis)
            
            return {
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
        
        elif analysis_type == 'comparative':
            analyzer = ComparativeAnalyzer()
            comparison = analyzer.compare_websites(urls)
            
            if include_advanced:
                advanced_analyzer = AdvancedAnalyzer()
                advanced_results = advanced_analyzer.analyze_testimonials(all_testimonials)
                comparison['advanced_analysis'] = advanced_results
            
            # Cache results
            cache_key = f"analysis:{datetime.now().isoformat()}"
            cache.set(cache_key, comparison)
            
            return {
                'success': True,
                'comparison': comparison,
                'timestamp': datetime.now().isoformat()
            }
        
        elif analysis_type == 'competitive':
            if len(urls) < 2:
                raise ValueError('At least two URLs required for competitive analysis')
            
            analyzer = CompetitiveAnalyzer()
            analysis = analyzer.analyze_competitor(urls[0], urls[1:], days_back)
            
            if include_advanced:
                advanced_analyzer = AdvancedAnalyzer()
                advanced_results = advanced_analyzer.analyze_testimonials(all_testimonials)
                analysis['advanced_analysis'] = advanced_results
            
            # Cache results
            cache_key = f"analysis:{datetime.now().isoformat()}"
            cache.set(cache_key, analysis)
            
            return {
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
        
    except Exception as e:
        return {'error': str(e)}

@celery_app.task(bind=True)
def generate_report(self, analysis_data: Dict[str, Any], report_type: str, metrics: List[str] = None, branding: Dict[str, str] = None) -> Dict[str, Any]:
    """Background task for report generation."""
    try:
        # Update task state
        self.update_state(state='GENERATING', meta={'current': 0, 'total': 1})
        
        # Generate report
        generator = ReportGenerator()
        filename = generator.generate_report(
            analysis_data=analysis_data,
            report_type=report_type,
            metrics=metrics,
            branding=branding
        )
        
        # Cache results
        cache_key = f"report:{filename}"
        cache.set(cache_key, {
            'filename': filename,
            'download_url': f'/api/download_report/{filename}'
        })
        
        return {
            'success': True,
            'filename': filename,
            'download_url': f'/api/download_report/{filename}'
        }
        
    except Exception as e:
        return {'error': str(e)}

@celery_app.task
def send_webhook_notification(webhook_url: str, analysis_id: str, status: str, result: Dict[str, Any] = None):
    """Send webhook notification about analysis completion."""
    try:
        payload = {
            'analysis_id': analysis_id,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
        
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        
    except Exception as e:
        # Log webhook failure
        print(f"Failed to send webhook notification: {str(e)}")

@celery_app.task
def cleanup_old_data():
    """Clean up old analysis results and reports."""
    try:
        # Clear old analysis results
        analysis_count = cache.clear_pattern(ANALYSIS_KEY_PATTERN)
        
        # Clear old reports
        report_count = cache.clear_pattern(REPORT_KEY_PATTERN)
        
        return {
            'success': True,
            'cleared_analyses': analysis_count,
            'cleared_reports': report_count
        }
        
    except Exception as e:
        return {'error': str(e)} 