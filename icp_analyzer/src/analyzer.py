from typing import Dict, Any
import logging
from datetime import datetime
import json
import os
from src.scraper import WebScraper
from src.processor import ContentProcessor

class ICPAnalyzer:
    def __init__(self):
        """Initialize the ICP Analyzer with its components"""
        self.scraper = WebScraper()
        self.processor = ContentProcessor()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_website(self, url: str, save_results: bool = True) -> Dict[str, Any]:
        """
        Analyze a website to determine its Ideal Customer Profile
        
        Args:
            url: Website URL to analyze
            save_results: Whether to save results to a file
            
        Returns:
            Dictionary containing the ICP analysis results
        """
        try:
            print(f"\nAnalyzing {url}...")
            self.logger.info(f"Starting analysis of {url}")
            
            # Step 1: Scrape website content
            self.logger.info("Scraping website content...")
            scraped_content = self.scraper.scrape_website(url)
            
            if not scraped_content:
                raise ValueError(f"Failed to scrape content from {url}")
            
            # Step 2: Process content
            self.logger.info("Processing content...")
            analysis_results = self.processor.process_content(scraped_content)
            
            # Add metadata
            results = {
                'url': url,
                'analysis_timestamp': datetime.now().isoformat(),
                'icp_analysis': analysis_results['icp_analysis'],
                'extracted_entities': analysis_results.get('extracted_entities', {
                    'organizations': [],
                    'locations': [],
                    'products': []
                }),
                'key_phrases': analysis_results.get('key_phrases', [])
            }
            
            # Save results if requested
            if save_results:
                try:
                    self._save_results(results)
                except Exception as e:
                    self.logger.error(f"Error saving results: {str(e)}")
            
            # Print analysis results
            self._print_analysis_results(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing website: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat(),
                'icp_analysis': {},
                'extracted_entities': {
                    'organizations': [],
                    'locations': [],
                    'products': []
                },
                'key_phrases': []
            }
            
    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save analysis results to a JSON file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Generate filename based on timestamp and domain
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = results['url'].replace('https://', '').replace('http://', '').split('/')[0]
            filename = f"data/icp_analysis_{domain}_{timestamp}.json"
            
            # Save results
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
                
            self.logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            raise Exception(f"Error saving results: {str(e)}")
            
    def _print_analysis_results(self, results: Dict[str, Any]) -> None:
        """Print analysis results in a formatted way"""
        print(f"\nAnalysis Results for {results['url']}\n")
        
        print("1. Basic Information:")
        print("-" * 50)
        print(f"Analysis Timestamp: {results['analysis_timestamp']}\n")
        
        print("2. ICP Analysis:")
        print("-" * 50)
        icp = results['icp_analysis']
        print(f"Industry Focus: {icp.get('industry_focus', '')}")
        print(f"Company Size: {icp.get('company_size', 'Unknown')}")
        print(f"Key Decision Makers: {icp.get('key_decision_makers', '')}")
        print(f"Geographic Focus: {icp.get('geographic_focus', '')}")
        print(f"Technical Sophistication: {icp.get('technical_sophistication', 'Unknown')}")
        print(f"Budget Level: {icp.get('budget_level', 'Unknown')}")
        print(f"Buying Cycle: {icp.get('buying_cycle', 'Unknown')}\n")
        
        print("3. Key Pain Points Addressed:")
        print("-" * 50)
        print("\n")
        
        print("4. Extracted Entities:")
        print("-" * 50)
        entities = results['extracted_entities']
        if entities.get('organizations'):
            print(f"Organizations: {', '.join(entities['organizations'])}")
        if entities.get('locations'):
            print(f"Locations: {', '.join(entities['locations'])}")
        if entities.get('products'):
            print(f"Products: {', '.join(entities['products'])}\n")
        
        print("5. Notable Key Phrases:")
        print("-" * 50)
        for i, phrase in enumerate(results.get('key_phrases', []), 1):
            print(f"{i}. {phrase}")
        print("\n")
            
    def batch_analyze(self, urls: list[str], save_results: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Analyze multiple websites in batch
        
        Args:
            urls: List of website URLs to analyze
            save_results: Whether to save results to files
            
        Returns:
            Dictionary mapping URLs to their analysis results
        """
        results = {}
        for url in urls:
            results[url] = self.analyze_website(url, save_results)
            
        return results 