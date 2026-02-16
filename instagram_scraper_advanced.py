"""
Advanced Instagram Scraper with Login Support
More robust approach for scraping Instagram accounts
"""

import asyncio
import re
import json
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AdvancedInstagramScraper:
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, headless: bool = True):
        self.headless = headless
        # Load from .env file, fallback to environment variables or provided values
        self.username = username or os.getenv('INSTAGRAM_USERNAME') or os.getenv('INSTAGRAM_USER')
        self.password = password or os.getenv('INSTAGRAM_PASSWORD') or os.getenv('INSTAGRAM_PASS')
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logged_in = False
        
    async def start(self):
        """Initialize browser and page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create context with realistic settings
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        self.page = await context.new_page()
        
        # Remove webdriver property
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
    async def login(self) -> bool:
        """Login to Instagram"""
        if not self.username or not self.password:
            print("⚠️  No credentials provided. Some features may be limited.")
            return False
            
        if self.logged_in:
            return True
            
        try:
            print("🔐 Logging into Instagram...")
            await self.page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Fill username
            username_input = await self.page.wait_for_selector('input[name="username"]', timeout=10000)
            await username_input.fill(self.username)
            await asyncio.sleep(1)
            
            # Fill password
            password_input = await self.page.wait_for_selector('input[name="password"]', timeout=10000)
            await password_input.fill(self.password)
            await asyncio.sleep(1)
            
            # Click login button
            login_button = await self.page.wait_for_selector('button[type="submit"]', timeout=10000)
            await login_button.click()
            
            # Wait for navigation
            await self.page.wait_for_url("**/accounts/onetap/**", timeout=15000)
            await asyncio.sleep(3)
            
            # Handle "Save Your Login Info" prompt
            try:
                not_now_button = await self.page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
                await not_now_button.click()
                await asyncio.sleep(2)
            except:
                pass
            
            # Handle "Turn on Notifications" prompt
            try:
                not_now_button = await self.page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
                await not_now_button.click()
            except:
                pass
            
            self.logged_in = True
            print("✅ Successfully logged in!")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            print("⚠️  Continuing without login (some features may be limited)")
            return False
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
    
    def parse_followers(self, followers_text: str) -> Optional[int]:
        """Parse follower count from text"""
        if not followers_text:
            return None
            
        text = followers_text.replace(',', '').replace(' ', '').strip()
        match = re.search(r'([\d.]+)\s*([KMB]?)', text, re.IGNORECASE)
        if not match:
            return None
            
        number = float(match.group(1))
        unit = match.group(2).upper()
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        multiplier = multipliers.get(unit, 1)
        
        return int(number * multiplier)
    
    def is_valid_follower_count(self, followers: Optional[int]) -> bool:
        """Check if follower count is between 10K and 50K"""
        if followers is None:
            return False
        return 10000 <= followers <= 50000
    
    async def search_by_keyword(self, keyword: str, max_results: int = 50) -> List[Dict]:
        """
        Search for accounts using keyword with multiple methods
        """
        if not self.page:
            raise Exception("Browser not started. Call start() first.")
        
        print(f"🔍 Searching for accounts matching: {keyword}")
        
        accounts = []
        seen_usernames = set()
        
        # Method 1: Search hashtag page and extract from posts
        try:
            print("📱 Searching hashtag page...")
            search_url = f"https://www.instagram.com/explore/tags/{keyword}/"
            await self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)
            
            # Find post links
            post_selectors = [
                'article a[href*="/p/"]',
                'a[href*="/p/"]',
                'a[href*="/reel/"]'
            ]
            
            post_links = []
            for selector in post_selectors:
                try:
                    links = await self.page.query_selector_all(selector)
                    if links:
                        post_links = links[:max_results * 3]
                        break
                except:
                    continue
            
            print(f"   Found {len(post_links)} posts to check")
            
            for i, post_link in enumerate(post_links):
                try:
                    href = await post_link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Navigate to post
                    post_url = f"https://www.instagram.com{href}"
                    await self.page.goto(post_url, wait_until="domcontentloaded", timeout=20000)
                    await asyncio.sleep(3)
                    
                    # Extract username from post page
                    username = await self.extract_username_from_post()
                    
                    if username and username not in seen_usernames:
                        seen_usernames.add(username)
                        
                        # Get account info
                        account_data = await self.get_account_info(username)
                        
                        if account_data:
                            followers = account_data.get('followers')
                            if followers and self.is_valid_follower_count(followers):
                                accounts.append(account_data)
                                print(f"✅ [{len(accounts)}/{max_results}] @{username}: {followers:,} followers")
                                
                                if len(accounts) >= max_results:
                                    return accounts
                    
                    await asyncio.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    if not self.headless:
                        print(f"   ⚠️  Error processing post {i+1}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error in search: {str(e)}")
        
        return accounts
    
    async def extract_username_from_post(self) -> Optional[str]:
        """Extract username from a post page"""
        try:
            # Method 1: Look for profile link in header
            header_selectors = [
                'header a[href^="/"]',
                'article header a[href^="/"]',
                'header a',
            ]
            
            for selector in header_selectors:
                try:
                    links = await self.page.query_selector_all(selector)
                    for link in links:
                        href = await link.get_attribute('href')
                        if href:
                            match = re.match(r'^/([a-zA-Z0-9._]+)/?$', href)
                            if match:
                                username = match.group(1)
                                if username not in ['explore', 'accounts', 'direct', 'reels', 'stories', 'p', 'reel']:
                                    return username
                except:
                    continue
            
            # Method 2: Parse from page source
            page_content = await self.page.content()
            username_patterns = [
                r'"owner":\{"username":"([^"]+)"',
                r'"username":"([^"]+)"',
                r'"profilePage_([^"]+)"',
            ]
            
            for pattern in username_patterns:
                match = re.search(pattern, page_content)
                if match:
                    username = match.group(1)
                    if username not in ['explore', 'accounts', 'direct', 'reels', 'stories']:
                        return username
                        
        except Exception as e:
            pass
        
        return None
    
    async def get_account_info(self, username: str) -> Optional[Dict]:
        """Get account information from profile"""
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            await self.page.goto(profile_url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(3)
            
            followers = None
            
            # Method 1: Parse from page source (most reliable)
            try:
                page_content = await self.page.content()
                
                # Look for GraphQL/JSON data
                patterns = [
                    r'"edge_followed_by":\{"count":(\d+)\}',
                    r'"follower_count":(\d+)',
                    r'"followers":\{"count":(\d+)\}',
                    r'"edge_follow":\{"count":(\d+)\}',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, page_content)
                    if matches:
                        try:
                            followers = int(matches[0])
                            break
                        except:
                            continue
                
                # If not found, look for formatted text
                if not followers:
                    text_patterns = [
                        r'(\d+[.,]?\d*[KMB]?)\s*followers',
                        r'followers["\']?\s*:\s*["\']?(\d+[KMB]?)',
                    ]
                    for pattern in text_patterns:
                        matches = re.findall(pattern, page_content, re.IGNORECASE)
                        if matches:
                            followers = self.parse_followers(matches[0])
                            if followers:
                                break
                                
            except Exception as e:
                pass
            
            # Method 2: Try to find follower link text
            if not followers:
                try:
                    follower_links = await self.page.query_selector_all('a[href*="/followers/"]')
                    for link in follower_links:
                        text = await link.inner_text()
                        parsed = self.parse_followers(text)
                        if parsed:
                            followers = parsed
                            break
                except:
                    pass
            
            # Method 3: Look in structured data
            if not followers:
                try:
                    selectors = [
                        'span:has-text("followers")',
                        'li:has-text("followers")',
                        '[aria-label*="followers"]'
                    ]
                    for selector in selectors:
                        try:
                            elements = await self.page.query_selector_all(selector)
                            for element in elements:
                                text = await element.inner_text()
                                parsed = self.parse_followers(text)
                                if parsed:
                                    followers = parsed
                                    break
                            if followers:
                                break
                        except:
                            continue
                except:
                    pass
            
            return {
                'username': username,
                'link': profile_url,
                'followers': followers
            }
            
        except Exception as e:
            if not self.headless:
                print(f"⚠️  Error getting info for @{username}: {str(e)}")
            return None


async def scrape_instagram_advanced(
    keyword: str,
    max_results: int = 50,
    username: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = True
) -> List[Dict]:
    """
    Advanced Instagram scraper with login support
    
    Args:
        keyword: Domain/keyword to search for
        max_results: Maximum number of accounts to return
        username: Instagram username (optional, can use env var)
        password: Instagram password (optional, can use env var)
        headless: Run browser in headless mode
    
    Returns:
        List of dicts with username, link, and followers
    """
    scraper = AdvancedInstagramScraper(username, password, headless)
    
    try:
        await scraper.start()
        await scraper.login()
        accounts = await scraper.search_by_keyword(keyword, max_results)
        
        return accounts
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python instagram_scraper_advanced.py <keyword> [max_results]")
        print("Example: python instagram_scraper_advanced.py skinkare 50")
        print("\nNote: Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD env vars for login")
        sys.exit(1)
    
    keyword = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    print(f"\n🚀 Starting Advanced Instagram Scraper")
    print(f"📝 Keyword: {keyword}")
    print(f"🎯 Follower range: 10K - 50K")
    print(f"📊 Max results: {max_results}\n")
    
    results = asyncio.run(scrape_instagram_advanced(keyword, max_results, headless=True))
    
    if results:
        print(f"\n✨ Found {len(results)} accounts matching criteria:")
        for acc in results:
            print(f"  @{acc['username']}: {acc['followers']:,} followers - {acc['link']}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"instagram_results_{keyword}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {filename}")
    else:
        print("\n❌ No accounts found matching the criteria")
