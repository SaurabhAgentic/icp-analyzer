import json
import os
from src.analyzers.testimonial_analyzer import TestimonialAnalyzer
from src.config import DATA_DIR

def main():
    # Initialize the analyzer
    analyzer = TestimonialAnalyzer()
    
    # Get the most recent scraped data file
    data_files = [f for f in os.listdir(DATA_DIR) if f.startswith('icp_analysis_') and f.endswith('.json')]
    if not data_files:
        print("No scraped data files found. Please run the scraper first.")
        return
    
    latest_file = max(data_files, key=lambda x: os.path.getctime(os.path.join(DATA_DIR, x)))
    filepath = os.path.join(DATA_DIR, latest_file)
    
    # Load the scraped data
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Analyze the testimonials
    analysis = analyzer.analyze_testimonials(data)
    
    # Print the analysis results
    print("\n=== Testimonial Analysis Results ===\n")
    
    print(f"Total Testimonials Analyzed: {analysis['total_testimonials']}")
    
    print("\nProduct Mentions:")
    for product, count in analysis['product_mentions'].items():
        print(f"- {product.title()}: {count} mentions")
    
    print("\nKey Themes:")
    for theme in analysis['key_themes']:
        print(f"- {theme.title()}")
    
    print("\nSentiment Analysis:")
    sentiment = analysis['sentiment_analysis']
    print(f"- Average Sentiment: {sentiment['average_sentiment']:.2f}")
    print(f"- Positive Testimonials: {sentiment['positive_count']}")
    print(f"- Negative Testimonials: {sentiment['negative_count']}")
    print(f"- Neutral Testimonials: {sentiment['neutral_count']}")
    
    print("\nCustomer Segments:")
    for segment, testimonials in analysis['customer_segments'].items():
        print(f"- {segment.replace('_', ' ').title()}: {len(testimonials)} testimonials")
    
    print("\nTop Benefits Mentioned:")
    for benefit_type, quotes in analysis['benefits_mentioned'].items():
        if quotes:
            print(f"\n{benefit_type.replace('_', ' ').title()}:")
            for quote in quotes[:3]:  # Show top 3 quotes for each benefit
                print(f"- {quote}")
    
    print("\nPain Points Identified:")
    for pain_type, quotes in analysis['pain_points'].items():
        if quotes:
            print(f"\n{pain_type.replace('_', ' ').title()}:")
            for quote in quotes[:3]:  # Show top 3 quotes for each pain point
                print(f"- {quote}")
    
    print(f"\nAnalysis results have been saved to: {os.path.join(DATA_DIR, f'testimonial_analysis_{os.path.basename(latest_file)}')}")

if __name__ == "__main__":
    main() 