"""
Helper script to export Instagram cookies from browser
Run this after logging into Instagram manually, then use the cookies file
"""

import json
import asyncio
from playwright.async_api import async_playwright


async def export_cookies(headless: bool = False):
    """
    Export Instagram cookies by logging in manually
    """
    print("="*60)
    print("Instagram Cookie Exporter")
    print("="*60)
    print("\nThis script will:")
    print("1. Open Instagram login page")
    print("2. You log in manually (including OTP if needed)")
    print("3. Export cookies to instagram_cookies.json")
    print("\nStarting browser...\n")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-IN',
        timezone_id='Asia/Kolkata'
    )
    
    page = await context.new_page()
    
    # Navigate to Instagram
    print("📱 Opening Instagram...")
    await page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
    
    print("\n" + "="*60)
    print("🔐 Please log in to Instagram in the browser window")
    print("="*60)
    print("   - Enter your username and password")
    print("   - Complete any OTP/verification if required")
    print("   - Wait until you're logged in and see your Instagram feed")
    print("   - Then press Enter here to export cookies")
    print("="*60 + "\n")
    
    # Wait for user to press Enter
    input("Press Enter after you've logged in successfully...")
    
    # Check if logged in
    current_url = page.url
    if "accounts/login" in current_url.lower():
        print("\n⚠️  Still on login page. Make sure you're logged in!")
        print("   Run this script again and complete the login.")
        await browser.close()
        return
    
    # Export cookies
    cookies = await context.cookies()
    
    if cookies:
        filename = "instagram_cookies.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Successfully exported {len(cookies)} cookies to {filename}")
        print(f"💡 You can now use this file with the scraper:")
        print(f"   python instagram_scraper_business_indian.py skinkare 50 false {filename}")
        print(f"\n   Or set INSTAGRAM_COOKIES_FILE={filename} in .env file")
    else:
        print("\n❌ No cookies found. Make sure you're logged in!")
    
    await browser.close()


if __name__ == "__main__":
    import sys
    headless = sys.argv[1].lower() == 'true' if len(sys.argv) > 1 else False
    asyncio.run(export_cookies(headless))
