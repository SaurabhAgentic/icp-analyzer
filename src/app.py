from flask import Flask, render_template, request, jsonify, send_file
from src.scrapers.website_scraper import WebsiteScraper
from src.analyzers.testimonial_analyzer import TestimonialAnalyzer
from src.analyzers.comparative_analyzer import ComparativeAnalyzer
from src.analyzers.competitive_analyzer import CompetitiveAnalyzer
from src.analyzers.advanced_analyzer import AdvancedAnalyzer
from src.reporting.report_generator import ReportGenerator
import os
from src.config import DATA_DIR, REPORTS_DIR, VISUALIZATIONS_DIR
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle URL submission and analysis."""
    urls = request.form.getlist('urls[]')
    analysis_type = request.form.get('analysis_type', 'single')
    days_back = int(request.form.get('days_back', 30))
    include_advanced = request.form.get('include_advanced', 'false').lower() == 'true'
    
    if not urls:
        return jsonify({'error': 'At least one URL is required'}), 400
    
    try:
        # Scrape all websites first
        scraper = WebsiteScraper()
        all_testimonials = []
        for url in urls:
            data = scraper.scrape_website(url)
            if not data:
                return jsonify({'error': f'Failed to scrape website: {url}'}), 500
            all_testimonials.extend(data['testimonials'])
        
        # Perform analysis based on type
        if analysis_type == 'single':
            analyzer = TestimonialAnalyzer()
            analysis = analyzer.analyze_testimonials(all_testimonials)
            
            # Add advanced analysis if requested
            if include_advanced:
                advanced_analyzer = AdvancedAnalyzer()
                advanced_results = advanced_analyzer.analyze_testimonials(all_testimonials)
                analysis['advanced_analysis'] = advanced_results
                
                # Generate visualizations
                visualization_files = advanced_analyzer.generate_visualizations(
                    advanced_results,
                    os.path.join(VISUALIZATIONS_DIR, datetime.now().strftime('%Y%m%d_%H%M%S'))
                )
                analysis['visualization_files'] = visualization_files
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            })
        
        elif analysis_type == 'comparative':
            analyzer = ComparativeAnalyzer()
            comparison = analyzer.compare_websites(urls)
            
            # Add advanced analysis if requested
            if include_advanced:
                advanced_analyzer = AdvancedAnalyzer()
                advanced_results = advanced_analyzer.analyze_testimonials(all_testimonials)
                comparison['advanced_analysis'] = advanced_results
                
                # Generate visualizations
                visualization_files = advanced_analyzer.generate_visualizations(
                    advanced_results,
                    os.path.join(VISUALIZATIONS_DIR, datetime.now().strftime('%Y%m%d_%H%M%S'))
                )
                comparison['visualization_files'] = visualization_files
            
            return jsonify({
                'success': True,
                'comparison': comparison,
                'timestamp': datetime.now().isoformat()
            })
        
        elif analysis_type == 'competitive':
            if len(urls) < 2:
                return jsonify({'error': 'At least two URLs required for competitive analysis'}), 400
            
            analyzer = CompetitiveAnalyzer()
            analysis = analyzer.analyze_competitor(urls[0], urls[1:], days_back)
            
            # Add advanced analysis if requested
            if include_advanced:
                advanced_analyzer = AdvancedAnalyzer()
                advanced_results = advanced_analyzer.analyze_testimonials(all_testimonials)
                analysis['advanced_analysis'] = advanced_results
                
                # Generate visualizations
                visualization_files = advanced_analyzer.generate_visualizations(
                    advanced_results,
                    os.path.join(VISUALIZATIONS_DIR, datetime.now().strftime('%Y%m%d_%H%M%S'))
                )
                analysis['visualization_files'] = visualization_files
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            })
        
        else:
            return jsonify({'error': 'Invalid analysis type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<filename>')
def get_results(filename):
    """Retrieve analysis results by filename."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Results not found'}), 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return jsonify(data)

@app.route('/download/<filename>')
def download_results(filename):
    """Download analysis results as JSON file."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Results not found'}), 404
    
    return send_file(
        filepath,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )

@app.route('/recent')
def get_recent_analyses():
    """Get list of recent analyses."""
    files = []
    for filename in os.listdir(DATA_DIR):
        if (filename.startswith('testimonial_analysis_') or 
            filename.startswith('comparative_analysis_') or
            filename.startswith('competitive_analysis_')) and filename.endswith('.json'):
            filepath = os.path.join(DATA_DIR, filename)
            files.append({
                'filename': filename,
                'timestamp': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                'url': filename.split('_')[2] if 'testimonial' in filename else 'Multiple URLs',
                'type': 'competitive' if 'competitive' in filename else 
                       'comparative' if 'comparative' in filename else 'single'
            })
    
    # Sort by timestamp, most recent first
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(files[:10])  # Return 10 most recent analyses

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate a report in the specified format."""
    try:
        data = request.json
        analysis_data = data.get('analysis_data')
        report_type = data.get('report_type')
        metrics = data.get('metrics')
        branding = data.get('branding')
        
        if not analysis_data or not report_type:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        generator = ReportGenerator()
        filename = generator.generate_report(
            analysis_data=analysis_data,
            report_type=report_type,
            metrics=metrics,
            branding=branding
        )
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download_report/{filename}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_report/<filename>')
def download_report(filename):
    """Download a generated report."""
    filepath = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Report not found'}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )

@app.route('/export_chart', methods=['POST'])
def export_chart():
    """Export a chart as an image."""
    try:
        data = request.json
        chart_data = data.get('chart_data')
        chart_type = data.get('chart_type')
        title = data.get('title')
        filename = data.get('filename')
        
        if not chart_data or not chart_type or not title:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        generator = ReportGenerator()
        filename = generator.export_chart(
            chart_data=chart_data,
            chart_type=chart_type,
            title=title,
            filename=filename
        )
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download_report/{filename}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualizations/<filename>')
def get_visualization(filename):
    """Retrieve a visualization file."""
    filepath = os.path.join(VISUALIZATIONS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Visualization not found'}), 404
    
    return send_file(filepath)

if __name__ == '__main__':
    app.run(debug=True) 