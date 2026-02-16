"""
Simple test script to verify the scraper works
"""

import asyncio
from instagram_scraper_working import scrape_instagram_working


async def test_scraper():
    """Test the scraper with a simple keyword"""
    print("=" * 60)
    print("Testing Instagram Scraper")
    print("=" * 60)
    
    # Test with a common keyword
    keyword = "skincare"  # Change this to your keyword
    max_results = 5  # Start with small number for testing
    
    print(f"\nTesting with keyword: '{keyword}'")
    print(f"Looking for accounts with 10K-50K followers\n")
    
    try:
        results = await scrape_instagram_working(
            keyword=keyword,
            max_results=max_results,
            headless=False  # Set to False to see what's happening
        )
        
        if results:
            print(f"\n✅ SUCCESS! Found {len(results)} accounts:")
            for i, acc in enumerate(results, 1):
                print(f"\n{i}. Username: @{acc['username']}")
                print(f"   Followers: {acc['followers']:,}")
                print(f"   Link: {acc['link']}")
        else:
            print("\n❌ No results found")
            print("\nTroubleshooting tips:")
            print("1. Make sure you're connected to the internet")
            print("2. Try running with headless=False to see what's happening")
            print("3. Add Instagram login credentials for better results")
            print("4. Check if the keyword exists on Instagram")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_scraper())
