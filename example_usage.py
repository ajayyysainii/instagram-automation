"""
Example usage of Instagram Scraper
"""

import asyncio
import json
from datetime import datetime
from instagram_scraper import scrape_instagram, save_results
from instagram_scraper_advanced import scrape_instagram_advanced
import os


async def example_basic():
    """Basic example without login"""
    print("=" * 60)
    print("Example 1: Basic Scraper (No Login)")
    print("=" * 60)
    
    keyword = "skinkare"
    results = await scrape_instagram(keyword, max_results=10, headless=False)
    
    if results:
        print(f"\nFound {len(results)} accounts:")
        for acc in results:
            print(f"  @{acc['username']}: {acc['followers']:,} followers")
        save_results(results, keyword)
    else:
        print("No results found")


async def example_advanced():
    """Advanced example with login"""
    print("\n" + "=" * 60)
    print("Example 2: Advanced Scraper (With Login)")
    print("=" * 60)
    
    # Get credentials from environment variables
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("⚠️  Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD env vars for login")
        print("   Example: export INSTAGRAM_USERNAME='your_username'")
        print("            export INSTAGRAM_PASSWORD='your_password'")
        return
    
    keyword = "apparel"
    results = await scrape_instagram_advanced(
        keyword,
        max_results=20,
        username=username,
        password=password,
        headless=False  # Set to True to run in background
    )
    
    if results:
        print(f"\nFound {len(results)} accounts:")
        for acc in results:
            print(f"  @{acc['username']}: {acc['followers']:,} followers")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"instagram_results_{keyword}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {filename}")
    else:
        print("No results found")


async def example_multiple_keywords():
    """Example: Search multiple keywords"""
    print("\n" + "=" * 60)
    print("Example 3: Multiple Keywords")
    print("=" * 60)
    
    keywords = ["skinkare", "apparel", "skincare"]
    all_results = []
    
    for keyword in keywords:
        print(f"\n🔍 Searching: {keyword}")
        results = await scrape_instagram(keyword, max_results=5, headless=True)
        all_results.extend(results)
        await asyncio.sleep(5)  # Delay between searches
    
    if all_results:
        print(f"\n✨ Total accounts found: {len(all_results)}")
        save_results(all_results, "multiple_keywords")


if __name__ == "__main__":
    import sys
    
    # Run basic example by default
    if len(sys.argv) > 1 and sys.argv[1] == "advanced":
        asyncio.run(example_advanced())
    elif len(sys.argv) > 1 and sys.argv[1] == "multiple":
        asyncio.run(example_multiple_keywords())
    else:
        asyncio.run(example_basic())
