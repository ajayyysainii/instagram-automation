"""
Instagram Scraper
Scrapes Instagram accounts based on domain/keyword search
Filters accounts with followers between 10K to 50K
"""

import asyncio
import re
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
import json
from datetime import datetime


class InstagramScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def start(self):
        """Initialize browser and page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        
        # Set user agent to avoid detection
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            
    def parse_followers(self, followers_text: str) -> Optional[int]:
        """Parse follower count from text (e.g., '12.5K', '1.2M', '50K')"""
        if not followers_text:
            return None
            
        # Remove commas and spaces
        text = followers_text.replace(',', '').replace(' ', '').strip()
        
        # Match patterns like "12.5K", "1.2M", "50K", "123"
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
    
    async def search_accounts(self, keyword: str, max_results: int = 50) -> List[Dict]:
        """
        Search Instagram for accounts matching the keyword
        Returns list of accounts with username, link, and followers
        """
        if not self.page:
            raise Exception("Browser not started. Call start() first.")
            
        print(f"🔍 Searching Instagram for: {keyword}")
        
        # Navigate to Instagram search
        search_url = f"https://www.instagram.com/explore/tags/{keyword}/"
        # Alternative: search for accounts directly
        # search_url = f"https://www.instagram.com/web/search/topsearch/?query={keyword}"
        
        try:
            await self.page.goto(search_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)  # Wait for content to load
            
            # Try to find account links in search results
            # Instagram's structure varies, so we'll try multiple selectors
            accounts = []
            
            # Method 1: Look for account links in the page
            account_links = await self.page.query_selector_all('a[href*="/"]')
            
            seen_usernames = set()
            
            for link in account_links[:max_results * 3]:  # Check more links to find valid accounts
                try:
                    href = await link.get_attribute('href')
                    if not href or '/p/' in href or '/reel/' in href:
                        continue
                    
                    # Extract username from href (format: /username/)
                    username_match = re.search(r'/([^/]+)/$', href)
                    if not username_match:
                        continue
                    
                    username = username_match.group(1)
                    
                    # Skip if already processed or invalid
                    if username in seen_usernames or username in ['explore', 'accounts', '']:
                        continue
                    
                    seen_usernames.add(username)
                    
                    # Navigate to profile to get follower count
                    profile_url = f"https://www.instagram.com/{username}/"
                    account_data = await self.get_account_info(profile_url, username)
                    
                    if account_data and self.is_valid_follower_count(account_data.get('followers')):
                        accounts.append(account_data)
                        print(f"✅ Found: @{username} - {account_data.get('followers', 0):,} followers")
                        
                        if len(accounts) >= max_results:
                            break
                            
                    # Be respectful with rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"❌ Error during search: {str(e)}")
            # Fallback: Try direct account search
            return await self.search_accounts_direct(keyword, max_results)
            
        return accounts
    
    async def search_accounts_direct(self, keyword: str, max_results: int = 50) -> List[Dict]:
        """
        Alternative method: Search for accounts directly using Instagram's search API
        """
        if not self.page:
            raise Exception("Browser not started. Call start() first.")
            
        print(f"🔍 Using direct search method for: {keyword}")
        
        accounts = []
        
        # Try to access Instagram's search endpoint
        search_url = f"https://www.instagram.com/web/search/topsearch/?query={keyword}"
        
        try:
            await self.page.goto(search_url)
            await asyncio.sleep(2)
            
            # Get page content
            content = await self.page.content()
            
            # Try to parse JSON response
            json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    users = data.get('users', [])
                    
                    for user_info in users[:max_results * 2]:
                        try:
                            user = user_info.get('user', {})
                            username = user.get('username')
                            
                            if not username:
                                continue
                            
                            # Get detailed account info
                            profile_url = f"https://www.instagram.com/{username}/"
                            account_data = await self.get_account_info(profile_url, username)
                            
                            if account_data and self.is_valid_follower_count(account_data.get('followers')):
                                accounts.append(account_data)
                                print(f"✅ Found: @{username} - {account_data.get('followers', 0):,} followers")
                                
                                if len(accounts) >= max_results:
                                    break
                                    
                            await asyncio.sleep(2)
                            
                        except Exception as e:
                            continue
                            
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"❌ Error in direct search: {str(e)}")
            
        return accounts
    
    async def get_account_info(self, profile_url: str, username: str) -> Optional[Dict]:
        """
        Get account information from profile page
        Returns dict with username, link, and followers
        """
        try:
            await self.page.goto(profile_url, wait_until="networkidle", timeout=20000)
            await asyncio.sleep(2)  # Wait for content
            
            # Try multiple selectors to find follower count
            followers = None
            
            # Selector patterns Instagram uses
            selectors = [
                'a[href*="/followers/"] span',
                'a[href*="/followers/"]',
                'span:has-text("followers")',
                'li:has-text("followers")',
            ]
            
            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        text = await element.inner_text()
                        if 'followers' in text.lower():
                            # Extract number from text
                            parsed = self.parse_followers(text)
                            if parsed:
                                followers = parsed
                                break
                    if followers:
                        break
                except:
                    continue
            
            # Alternative: Look for meta tags or structured data
            if not followers:
                try:
                    # Check page content for follower patterns
                    content = await self.page.content()
                    follower_match = re.search(r'(\d+[.,]?\d*[KMB]?)\s*followers', content, re.IGNORECASE)
                    if follower_match:
                        followers = self.parse_followers(follower_match.group(1))
                except:
                    pass
            
            if followers is None:
                # Try to find in page text
                try:
                    page_text = await self.page.inner_text('body')
                    matches = re.findall(r'(\d+[.,]?\d*[KMB]?)\s*followers', page_text, re.IGNORECASE)
                    if matches:
                        followers = self.parse_followers(matches[0])
                except:
                    pass
            
            return {
                'username': username,
                'link': profile_url,
                'followers': followers
            }
            
        except Exception as e:
            print(f"⚠️  Error getting info for @{username}: {str(e)}")
            return None


async def scrape_instagram(keyword: str, max_results: int = 50, headless: bool = True) -> List[Dict]:
    """
    Main function to scrape Instagram accounts
    
    Args:
        keyword: Domain/keyword to search for (e.g., "skinkare", "apparel")
        max_results: Maximum number of accounts to return
        headless: Run browser in headless mode
    
    Returns:
        List of dicts with username, link, and followers
    """
    scraper = InstagramScraper(headless=headless)
    
    try:
        await scraper.start()
        accounts = await scraper.search_accounts(keyword, max_results)
        
        # Filter by follower count
        filtered_accounts = [
            acc for acc in accounts 
            if scraper.is_valid_follower_count(acc.get('followers'))
        ]
        
        return filtered_accounts
        
    finally:
        await scraper.close()


def save_results(accounts: List[Dict], keyword: str, filename: Optional[str] = None):
    """Save results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"instagram_results_{keyword}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {filename}")
    print(f"📊 Total accounts found: {len(accounts)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python instagram_scraper.py <keyword> [max_results]")
        print("Example: python instagram_scraper.py skinkare 50")
        sys.exit(1)
    
    keyword = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    print(f"\n🚀 Starting Instagram Scraper")
    print(f"📝 Keyword: {keyword}")
    print(f"🎯 Follower range: 10K - 50K")
    print(f"📊 Max results: {max_results}\n")
    
    results = asyncio.run(scrape_instagram(keyword, max_results, headless=True))
    
    if results:
        print(f"\n✨ Found {len(results)} accounts matching criteria:")
        for acc in results:
            print(f"  @{acc['username']}: {acc['followers']:,} followers - {acc['link']}")
        
        save_results(results, keyword)
    else:
        print("\n❌ No accounts found matching the criteria")
