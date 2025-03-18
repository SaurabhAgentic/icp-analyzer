from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
from src.scrapers.website_scraper import WebsiteScraper
from src.analyzers.testimonial_analyzer import TestimonialAnalyzer
from src.analyzers.comparative_analyzer import ComparativeAnalyzer
from src.analyzers.competitive_analyzer import CompetitiveAnalyzer
from src.analyzers.advanced_analyzer import AdvancedAnalyzer
from src.reporting.report_generator import ReportGenerator
from src.config import DATA_DIR, REPORTS_DIR, VISUALIZATIONS_DIR
import json
from typing import Dict, Any, List

# Initialize Flask app and extensions
app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
app.config['RATELIMIT_STRATEGY'] = 'fixed-window'

# Request parsers
analysis_parser = reqparse.RequestParser()
analysis_parser.add_argument('urls', type=str, action='append', required=True)
analysis_parser.add_argument('analysis_type', type=str, choices=['single', 'comparative', 'competitive'], required=True)
analysis_parser.add_argument('days_back', type=int, default=30)
analysis_parser.add_argument('include_advanced', type=bool, default=False)

report_parser = reqparse.RequestParser()
report_parser.add_argument('analysis_data', type=dict, required=True)
report_parser.add_argument('report_type', type=str, choices=['pdf', 'pptx', 'docx', 'excel'], required=True)
report_parser.add_argument('metrics', type=list, location='json')
report_parser.add_argument('branding', type=dict, location='json')

class AnalysisResource(Resource):
    @jwt_required()
    def post(self):
        """Handle analysis requests."""
        args = analysis_parser.parse_args()
        
        try:
            # Scrape websites
            scraper = WebsiteScraper()
            all_testimonials = []
            for url in args['urls']:
                data = scraper.scrape_website(url)
                if not data:
                    return {'error': f'Failed to scrape website: {url}'}, 500
                all_testimonials.extend(data['testimonials'])
            
            # Perform analysis based on type
            if args['analysis_type'] == 'single':
                analyzer = TestimonialAnalyzer()
                analysis = analyzer.analyze_testimonials(all_testimonials)
                
                if args['include_advanced']:
                    advanced_analyzer = AdvancedAnalyzer()
                    advanced_results = advanced_analyzer.analyze_testimonials(all_testimonials)
                    analysis['advanced_analysis'] = advanced_results
                
                return {
                    'success': True,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat()
                }
            
            elif args['analysis_type'] == 'comparative':
                analyzer = ComparativeAnalyzer()
                comparison = analyzer.compare_websites(args['urls'])
                
                if args['include_advanced']:
                    advanced_analyzer = AdvancedAnalyzer()
                    advanced_results = advanced_analyzer.analyze_testimonials(all_testimonials)
                    comparison['advanced_analysis'] = advanced_results
                
                return {
                    'success': True,
                    'comparison': comparison,
                    'timestamp': datetime.now().isoformat()
                }
            
            elif args['analysis_type'] == 'competitive':
                if len(args['urls']) < 2:
                    return {'error': 'At least two URLs required for competitive analysis'}, 400
                
                analyzer = CompetitiveAnalyzer()
                analysis = analyzer.analyze_competitor(
                    args['urls'][0],
                    args['urls'][1:],
                    args['days_back']
                )
                
                if args['include_advanced']:
                    advanced_analyzer = AdvancedAnalyzer()
                    advanced_results = advanced_analyzer.analyze_testimonials(all_testimonials)
                    analysis['advanced_analysis'] = advanced_results
                
                return {
                    'success': True,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat()
                }
            
        except Exception as e:
            return {'error': str(e)}, 500

class ReportResource(Resource):
    @jwt_required()
    def post(self):
        """Generate reports."""
        args = report_parser.parse_args()
        
        try:
            generator = ReportGenerator()
            filename = generator.generate_report(
                analysis_data=args['analysis_data'],
                report_type=args['report_type'],
                metrics=args.get('metrics'),
                branding=args.get('branding')
            )
            
            return {
                'success': True,
                'filename': filename,
                'download_url': f'/api/download_report/{filename}'
            }
            
        except Exception as e:
            return {'error': str(e)}, 500

class WebhookResource(Resource):
    @jwt_required()
    def post(self):
        """Register webhook for asynchronous analysis."""
        webhook_url = request.json.get('webhook_url')
        if not webhook_url:
            return {'error': 'Webhook URL is required'}, 400
        
        # Store webhook URL for the user
        user_id = get_jwt_identity()
        webhook_data = {
            'user_id': user_id,
            'webhook_url': webhook_url,
            'created_at': datetime.now().isoformat()
        }
        
        # Save webhook data
        webhook_file = os.path.join(DATA_DIR, f'webhook_{user_id}.json')
        with open(webhook_file, 'w') as f:
            json.dump(webhook_data, f)
        
        return {
            'success': True,
            'message': 'Webhook registered successfully'
        }

class ExportResource(Resource):
    @jwt_required()
    def post(self):
        """Export analysis results to external platforms."""
        platform = request.json.get('platform')
        analysis_data = request.json.get('analysis_data')
        
        if not platform or not analysis_data:
            return {'error': 'Platform and analysis data are required'}, 400
        
        try:
            # Export logic for different platforms
            if platform == 'salesforce':
                # Implement Salesforce export
                pass
            elif platform == 'hubspot':
                # Implement HubSpot export
                pass
            else:
                return {'error': f'Unsupported platform: {platform}'}, 400
            
            return {
                'success': True,
                'message': f'Successfully exported to {platform}'
            }
            
        except Exception as e:
            return {'error': str(e)}, 500

# Register API routes
api.add_resource(AnalysisResource, '/api/analyze')
api.add_resource(ReportResource, '/api/report')
api.add_resource(WebhookResource, '/api/webhook')
api.add_resource(ExportResource, '/api/export')

# Error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'Token has expired',
        'message': 'Please request a new token'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error': 'Invalid token',
        'message': 'Please provide a valid token'
    }), 401

if __name__ == '__main__':
    app.run(debug=True) 