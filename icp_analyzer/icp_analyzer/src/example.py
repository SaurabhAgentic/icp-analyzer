from src.analyzer import ICPAnalyzer
import json
from pprint import pprint

def analyze_and_print(analyzer, url):
    """Analyze a website and print results"""
    print(f"\nAnalyzing {url}...")
    results = analyzer.analyze_website(url)
    
    # Print the results in a structured way
    print(f"\nAnalysis Results for {url}")
    print("\n1. Basic Information:")
    print("-" * 50)
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
        
    icp = results['icp_analysis']
    print(f"Analysis Timestamp: {results['analysis_timestamp']}")
    
    print("\n2. ICP Analysis:")
    print("-" * 50)
    print(f"Industry Focus: {icp.get('industry_focus', '')}")
    print(f"Company Size: {icp.get('company_size', 'Unknown')}")
    print(f"Key Decision Makers: {icp.get('key_decision_makers', '')}")
    print(f"Geographic Focus: {icp.get('geographic_focus', '')}")
    print(f"Technical Sophistication: {icp.get('technical_sophistication', 'Unknown')}")
    print(f"Budget Level: {icp.get('budget_level', 'Unknown')}")
    print(f"Buying Cycle: {icp.get('buying_cycle', 'Unknown')}")
    
    print("\n3. Key Pain Points Addressed:")
    print("-" * 50)
    print("\n")
    
    print("\n4. Extracted Entities:")
    print("-" * 50)
    entities = results['extracted_entities']
    for entity_type, values in entities.items():
        if values:
            print(f"{entity_type.title()}: {', '.join(values)}")
    
    print("\n5. Notable Key Phrases:")
    print("-" * 50)
    key_phrases = results.get('key_phrases', [])[:10]  # Show top 10 phrases
    for idx, phrase in enumerate(key_phrases, 1):
        print(f"{idx}. {phrase}")
    print("\n" + "="*80 + "\n")

def main():
    # Initialize the analyzer
    analyzer = ICPAnalyzer()
    
    # Analyze both websites
    analyze_and_print(analyzer, "https://stripe.com")
    analyze_and_print(analyzer, "https://adyen.com")

if __name__ == "__main__":
    main() 