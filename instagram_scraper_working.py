"""
Working Instagram Scraper - Robust version that actually finds accounts
Uses multiple methods to search and extract account information
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


class WorkingInstagramScraper:
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, headless: bool = False):
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
        
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        self.page = await context.new_page()
        
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
    async def login(self) -> bool:
        """Login to Instagram"""
        if not self.username or not self.password:
            print("⚠️  No credentials provided. Continuing without login.")
            return False
            
        if self.logged_in:
            return True
            
        try:
            print("🔐 Logging into Instagram...")
            await self.page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
            await asyncio.sleep(3)
            
            # Fill username
            username_selectors = [
                'input[name="username"]',
                'input[aria-label="Phone number, username, or email"]',
                'input[type="text"]'
            ]
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = await self.page.wait_for_selector(selector, timeout=5000)
                    if username_input:
                        break
                except:
                    continue
            
            if not username_input:
                print("❌ Could not find username input")
                return False
                
            await username_input.fill(self.username)
            await asyncio.sleep(1)
            
            # Fill password
            password_selectors = [
                'input[name="password"]',
                'input[aria-label="Password"]',
                'input[type="password"]'
            ]
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(selector, timeout=5000)
                    if password_input:
                        break
                except:
                    continue
            
            if not password_input:
                print("❌ Could not find password input")
                return False
                
            await password_input.fill(self.password)
            await asyncio.sleep(1)
            
            # Click login button
            login_selectors = [
                'button[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Log In")'
            ]
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if login_button:
                        break
                except:
                    continue
            
            if login_button:
                await login_button.click()
                await asyncio.sleep(5)
                
                # Check if login was successful
                current_url = self.page.url
                if "accounts/login" not in current_url:
                    self.logged_in = True
                    print("✅ Successfully logged in!")
                    
                    # Handle prompts
                    await self.handle_prompts()
                    return True
                else:
                    print("❌ Login failed - still on login page")
                    return False
            else:
                print("❌ Could not find login button")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    async def handle_prompts(self):
        """Handle Instagram prompts after login"""
        prompts = [
            'button:has-text("Not Now")',
            'button:has-text("Not now")',
            'button:has-text("Save Info")',
            'button:has-text("Turn On")',
        ]
        
        for _ in range(3):  # Try up to 3 times
            for prompt in prompts:
                try:
                    button = await self.page.wait_for_selector(prompt, timeout=2000)
                    if button:
                        await button.click()
                        await asyncio.sleep(2)
                except:
                    pass
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
    
    def parse_followers(self, followers_text: str) -> Optional[int]:
        """Parse follower count from text"""
        if not followers_text:
            return None
            
        text = str(followers_text).replace(',', '').replace(' ', '').strip()
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
    
    async def search_accounts_by_keyword(self, keyword: str, max_results: int = 50) -> List[Dict]:
        """
        Search for accounts using multiple methods
        """
        if not self.page:
            raise Exception("Browser not started. Call start() first.")
        
        print(f"🔍 Searching for accounts matching: '{keyword}'")
        accounts = []
        seen_usernames = set()
        
        # Method 1: Use Instagram's search page
        try:
            print("📱 Method 1: Using Instagram search page...")
            search_url = f"https://www.instagram.com/explore/tags/{keyword}/"
            await self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)
            
            # Try to find usernames from posts
            usernames_found = await self.extract_usernames_from_page()
            print(f"   Found {len(usernames_found)} potential accounts")
            
            for username in usernames_found:
                if username in seen_usernames:
                    continue
                seen_usernames.add(username)
                
                account_data = await self.get_account_info(username)
                if account_data:
                    followers = account_data.get('followers')
                    if followers and self.is_valid_follower_count(followers):
                        accounts.append(account_data)
                        print(f"✅ @{username}: {followers:,} followers")
                        
                        if len(accounts) >= max_results:
                            return accounts
                
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"   ⚠️  Method 1 failed: {str(e)}")
        
        # Method 2: Search using Instagram's web search API
        if len(accounts) < max_results:
            try:
                print("📱 Method 2: Using Instagram web search API...")
                search_results = await self.search_via_api(keyword)
                
                for result in search_results:
                    username = result.get('username')
                    if not username or username in seen_usernames:
                        continue
                    
                    seen_usernames.add(username)
                    account_data = await self.get_account_info(username)
                    
                    if account_data:
                        followers = account_data.get('followers')
                        if followers and self.is_valid_follower_count(followers):
                            accounts.append(account_data)
                            print(f"✅ @{username}: {followers:,} followers")
                            
                            if len(accounts) >= max_results:
                                return accounts
                    
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"   ⚠️  Method 2 failed: {str(e)}")
        
        # Method 3: Search posts and extract authors
        if len(accounts) < max_results:
            try:
                print("📱 Method 3: Extracting from posts...")
                post_accounts = await self.extract_from_posts(keyword, max_results - len(accounts))
                
                for account in post_accounts:
                    username = account.get('username')
                    if username and username not in seen_usernames:
                        seen_usernames.add(username)
                        if self.is_valid_follower_count(account.get('followers')):
                            accounts.append(account)
                            print(f"✅ @{username}: {account.get('followers', 0):,} followers")
                            
                            if len(accounts) >= max_results:
                                return accounts
                                
            except Exception as e:
                print(f"   ⚠️  Method 3 failed: {str(e)}")
        
        return accounts
    
    async def extract_usernames_from_page(self) -> List[str]:
        """Extract usernames from current page"""
        usernames = []
        
        try:
            # Wait for content to load
            await asyncio.sleep(3)
            
            # Method 1: Find all links that look like profile links
            links = await self.page.query_selector_all('a[href^="/"]')
            for link in links:
                try:
                    href = await link.get_attribute('href')
                    if href:
                        # Match pattern: /username/ or /username
                        match = re.match(r'^/([a-zA-Z0-9._]+)/?$', href)
                        if match:
                            username = match.group(1)
                            # Filter out common non-account paths
                            if username not in ['explore', 'accounts', 'direct', 'reels', 'stories', 'p', '']:
                                if username not in usernames:
                                    usernames.append(username)
                except:
                    continue
            
            # Method 2: Look for username in text content
            try:
                page_text = await self.page.inner_text('body')
                username_pattern = r'@([a-zA-Z0-9._]+)'
                matches = re.findall(username_pattern, page_text)
                for match in matches:
                    if match not in usernames and len(match) > 3:
                        usernames.append(match)
            except:
                pass
                
        except Exception as e:
            print(f"   Error extracting usernames: {str(e)}")
        
        return usernames[:50]  # Limit to 50
    
    async def search_via_api(self, keyword: str) -> List[Dict]:
        """Search using Instagram's internal API"""
        results = []
        
        try:
            # Try to intercept or call Instagram's search API
            search_url = f"https://www.instagram.com/web/search/topsearch/?query={keyword}"
            await self.page.goto(search_url, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # Try to get JSON response
            content = await self.page.content()
            
            # Look for JSON in script tags or pre tags
            json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
            if not json_match:
                json_match = re.search(r'<script[^>]*>.*?({.*?})</script>', content, re.DOTALL)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    users = data.get('users', [])
                    for user_info in users:
                        user = user_info.get('user', {})
                        if user:
                            results.append({
                                'username': user.get('username'),
                                'follower_count': user.get('follower_count', 0)
                            })
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"   API search error: {str(e)}")
        
        return results
    
    async def extract_from_posts(self, keyword: str, max_count: int) -> List[Dict]:
        """Extract accounts from posts"""
        accounts = []
        
        try:
            # Navigate to hashtag page
            hashtag_url = f"https://www.instagram.com/explore/tags/{keyword}/"
            await self.page.goto(hashtag_url, wait_until="domcontentloaded")
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
                    post_links.extend(links[:20])  # Limit to 20 posts
                    if post_links:
                        break
                except:
                    continue
            
            for post_link in post_links[:max_count * 2]:
                try:
                    href = await post_link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Navigate to post
                    post_url = f"https://www.instagram.com{href}"
                    await self.page.goto(post_url, wait_until="domcontentloaded")
                    await asyncio.sleep(3)
                    
                    # Extract username from post
                    username = await self.extract_username_from_post()
                    if username and username not in [acc.get('username') for acc in accounts]:
                        account_data = await self.get_account_info(username)
                        if account_data:
                            accounts.append(account_data)
                            if len(accounts) >= max_count:
                                break
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"   Error extracting from posts: {str(e)}")
        
        return accounts
    
    async def extract_username_from_post(self) -> Optional[str]:
        """Extract username from a post page"""
        try:
            # Method 1: Look for profile link in header
            header_selectors = [
                'header a[href^="/"]',
                'article header a[href^="/"]',
                'a[href^="/"][href*="/"]'
            ]
            
            for selector in header_selectors:
                try:
                    link = await self.page.query_selector(selector)
                    if link:
                        href = await link.get_attribute('href')
                        if href:
                            match = re.match(r'^/([a-zA-Z0-9._]+)/?$', href)
                            if match:
                                username = match.group(1)
                                if username not in ['explore', 'accounts', 'direct', 'reels', 'stories', 'p']:
                                    return username
                except:
                    continue
            
            # Method 2: Parse from page source
            page_content = await self.page.content()
            username_match = re.search(r'"owner":\{"username":"([^"]+)"', page_content)
            if username_match:
                return username_match.group(1)
            
            # Method 3: Look in meta tags
            meta_tags = await self.page.query_selector_all('meta[property*="username"]')
            for tag in meta_tags:
                content = await tag.get_attribute('content')
                if content:
                    return content
                    
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
                
                # Look for GraphQL data
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
                    # Look for follower count in various elements
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
            print(f"   ⚠️  Error getting info for @{username}: {str(e)}")
            return None


async def scrape_instagram_working(
    keyword: str,
    max_results: int = 50,
    username: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = False
) -> List[Dict]:
    """
    Working Instagram scraper with multiple fallback methods
    
    Args:
        keyword: Domain/keyword to search for
        max_results: Maximum number of accounts to return
        username: Instagram username (optional)
        password: Instagram password (optional)
        headless: Run browser in headless mode (False recommended for debugging)
    
    Returns:
        List of dicts with username, link, and followers
    """
    scraper = WorkingInstagramScraper(username, password, headless)
    
    try:
        await scraper.start()
        await scraper.login()
        accounts = await scraper.search_accounts_by_keyword(keyword, max_results)
        
        return accounts
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python instagram_scraper_working.py <keyword> [max_results] [headless]")
        print("Example: python instagram_scraper_working.py skinkare 50")
        print("\nNote: Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD env vars for login")
        sys.exit(1)
    
    keyword = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    headless = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    print(f"\n🚀 Starting Working Instagram Scraper")
    print(f"📝 Keyword: {keyword}")
    print(f"🎯 Follower range: 10K - 50K")
    print(f"📊 Max results: {max_results}")
    print(f"👁️  Headless mode: {headless}\n")
    
    results = asyncio.run(scrape_instagram_working(keyword, max_results, headless=headless))
    
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
        print("💡 Tips:")
        print("   - Try running with headless=False to see what's happening")
        print("   - Add Instagram credentials for better results")
        print("   - Check if the keyword exists on Instagram")
