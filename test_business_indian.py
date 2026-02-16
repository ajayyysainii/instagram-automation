"""
Test script for Indian Business Account Scraper
"""

import asyncio
from instagram_scraper_business_indian import scrape_indian_business_accounts
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


async def test_business_indian_scraper():
    """Test the Indian business account scraper"""
    print("=" * 70)
    print("Testing Indian Business Account Scraper")
    print("=" * 70)
    
    # Get credentials from environment
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("\n⚠️  No Instagram credentials found!")
        print("   Add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD to .env file")
        print("   Login is recommended for better business account detection")
        print("\n   Continuing without login (results may be limited)...\n")
    else:
        print(f"\n✅ Using Instagram account: {username}\n")
    
    # Test with a keyword
    keyword = "skincare"  # Change this to your keyword
    max_results = 5  # Start small for testing
    
    print(f"🔍 Testing with keyword: '{keyword}'")
    print(f"📋 Filters:")
    print(f"   ✅ Business accounts only")
    print(f"   ✅ Indian brands only")
    print(f"   ✅ 10K-50K followers")
    print(f"📊 Max results: {max_results}\n")
    
    try:
        results = await scrape_indian_business_accounts(
            keyword=keyword,
            max_results=max_results,
            username=username,
            password=password,
            headless=False  # Set to False to see what's happening
        )
        
        if results:
            print(f"\n{'='*70}")
            print(f"✅ SUCCESS! Found {len(results)} Indian business accounts:")
            print(f"{'='*70}\n")
            
            for i, acc in enumerate(results, 1):
                print(f"{i}. @{acc['username']}")
                print(f"   Followers: {acc['followers']:,}")
                print(f"   Category: {acc.get('category', 'N/A')}")
                print(f"   Link: {acc['link']}")
                if acc.get('bio'):
                    print(f"   Bio: {acc['bio'][:100]}...")
                print()
            
            print(f"{'='*70}")
            print("✅ Test completed successfully!")
            print(f"{'='*70}\n")
        else:
            print(f"\n{'='*70}")
            print("❌ No results found")
            print(f"{'='*70}\n")
            print("Troubleshooting tips:")
            print("1. Make sure you're connected to the internet")
            print("2. Try running with headless=False to see what's happening")
            print("3. Add Instagram login credentials for better detection")
            print("4. Try a different keyword (e.g., 'skincare', 'fashion', 'beauty')")
            print("5. Check if the keyword has Indian business accounts on Instagram")
            
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ Error: {str(e)}")
        print(f"{'='*70}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_business_indian_scraper())
