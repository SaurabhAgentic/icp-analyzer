from src.scrapers.website_scraper import WebsiteScraper
import json
import sys

def main():
    # Get URL from command line argument or use default
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.momos.com/"
    
    # Initialize the scraper
    scraper = WebsiteScraper()
    
    try:
        # Scrape the website
        print(f"Scraping {url}...")
        content = scraper.scrape_website(url)
        
        # Print results
        print("\nScraping Results:")
        print("-" * 50)
        print(f"Title: {content.get('title', 'N/A')}")
        print(f"Meta Description: {content.get('meta_description', 'N/A')}")
        
        print("\nSections:")
        for section_name, section_content in content.get('sections', {}).items():
            print(f"\n{section_name.title()}:")
            print(section_content[:200] + "..." if len(section_content) > 200 else section_content)
        
        print("\nTestimonials:")
        for testimonial in content.get('testimonials', []):
            print(f"\nQuote: {testimonial.get('text', 'N/A')}")
            print(f"Author: {testimonial.get('author', 'N/A')}")
            print(f"Company: {testimonial.get('company', 'N/A')}")
        
        print("\nPricing Plans:")
        for plan in content.get('pricing', []):
            print(f"\nPlan: {plan.get('name', 'N/A')}")
            print(f"Price: {plan.get('price', 'N/A')}")
            print("Features:")
            for feature in plan.get('features', []):
                print(f"- {feature}")
        
        print(f"\nTotal Images: {len(content.get('images', []))}")
        print(f"Total Links: {len(content.get('links', []))}")
        
        print("\nRaw data has been saved to the data directory.")
        
    except Exception as e:
        print(f"Error occurred while scraping: {str(e)}")

if __name__ == "__main__":
    main() 