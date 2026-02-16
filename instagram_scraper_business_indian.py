"""
Instagram Scraper for Business Accounts - Indian Brands Only
Filters for:
- Business/Professional accounts (not personal)
- Indian brands/location
- 10K-50K followers
"""

import asyncio
import re
import json
from typing import List, Dict, Optional, Callable
from playwright.async_api import async_playwright, Page, Browser
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BusinessIndianScraper:
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, 
                 cookies_file: Optional[str] = None, headless: bool = False):
        self.headless = headless
        # Load from .env file, fallback to environment variables or provided values
        self.username = username or os.getenv('INSTAGRAM_USERNAME') or os.getenv('INSTAGRAM_USER')
        self.password = password or os.getenv('INSTAGRAM_PASSWORD') or os.getenv('INSTAGRAM_PASS')
        self.cookies_file = cookies_file or os.getenv('INSTAGRAM_COOKIES_FILE', 'instagram_cookies.json')
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logged_in = False
        self.cookies_loaded = False
        
        # Indian location indicators
        self.indian_keywords = [
            'india', 'indian', 'mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad',
            'pune', 'kolkata', 'ahmedabad', 'jaipur', 'surat', 'lucknow', 'kanpur',
            'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam', 'patna', 'vadodara',
            'ghaziabad', 'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut', 'rajkot',
            'varanasi', 'srinagar', 'amritsar', 'ranchi', 'jabalpur', 'gwalior', 'jodhpur',
            'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur', 'hubli', 'tiruchirappalli',
            'made in india', 'swadeshi', 'desi', 'bharat', 'hindustan', '+91'
        ]
        
    async def load_cookies(self) -> bool:
        """Load cookies from file if it exists (handles both string and JSON formats)"""
        if not os.path.exists(self.cookies_file):
            return False
        
        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            cookies = None
            
            # Try to parse as JSON first
            try:
                cookies = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, treat as cookie string format
                cookies = self._convert_cookie_string_to_json(content)
            
            # Ensure cookies is a list
            if isinstance(cookies, dict):
                cookies = [cookies]
            elif not isinstance(cookies, list):
                print(f"⚠️  Invalid cookies format in {self.cookies_file}")
                return False
            
            # Add cookies to context
            await self.page.context.add_cookies(cookies)
            self.cookies_loaded = True
            print(f"✅ Loaded {len(cookies)} cookies from {self.cookies_file}")
            return True
        except Exception as e:
            print(f"⚠️  Error loading cookies: {str(e)}")
            return False
    
    def _convert_cookie_string_to_json(self, cookie_string: str, domain: str = ".instagram.com") -> list:
        """Convert cookie string (from browser) to Playwright JSON format"""
        from datetime import datetime, timedelta
        
        cookies = []
        cookie_pairs = cookie_string.split(';')
        
        for pair in cookie_pairs:
            pair = pair.strip()
            if not pair or '=' not in pair:
                continue
            
            name, value = pair.split('=', 1)
            name = name.strip()
            value = value.strip()
            
            # Remove quotes from value if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            
            # Create cookie object
            cookie = {
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/",
                "expires": int((datetime.now() + timedelta(days=30)).timestamp()),
                "httpOnly": name.lower() in ["sessionid", "csrftoken"],
                "secure": True,
                "sameSite": "None" if name.lower() == "sessionid" else "Lax"
            }
            
            cookies.append(cookie)
        
        return cookies
    
    async def save_cookies(self):
        """Save current cookies to file"""
        try:
            cookies = await self.page.context.cookies()
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved cookies to {self.cookies_file}")
        except Exception as e:
            print(f"⚠️  Error saving cookies: {str(e)}")
    
    async def check_if_logged_in(self) -> bool:
        """Check if already logged in using cookies"""
        try:
            await self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(3)
            
            current_url = self.page.url
            page_content = await self.page.content()
            
            # Check if we're logged in (not on login page, no login prompts)
            if "accounts/login" in current_url.lower():
                return False
            
            # Check for login indicators
            login_indicators = [
                'input[name="username"]',
                'input[name="password"]',
                'Log in' in page_content,
                'Sign up' in page_content
            ]
            
            # If we see login fields, we're not logged in
            for indicator in login_indicators[:2]:  # Check selectors
                try:
                    element = await self.page.query_selector(indicator)
                    if element:
                        return False
                except:
                    continue
            
            # Check for logged-in indicators
            logged_in_indicators = [
                'Home' in page_content,
                'Explore' in page_content,
                'Reels' in page_content,
                'Profile' in page_content
            ]
            
            if any(logged_in_indicators):
                self.logged_in = True
                return True
            
            return False
        except Exception as e:
            return False
    
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
            locale='en-IN',  # Indian locale
            timezone_id='Asia/Kolkata'  # Indian timezone
        )
        
        self.page = await context.new_page()
        
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Try to load cookies if file exists
        if await self.load_cookies():
            # Check if cookies work (we're logged in)
            if await self.check_if_logged_in():
                print("✅ Successfully logged in using cookies!")
                await self.handle_prompts()
                return
        
    async def login(self) -> bool:
        """Login to Instagram (only if cookies didn't work)"""
        # If already logged in via cookies, skip
        if self.logged_in:
            return True
        
        if not self.username or not self.password:
            if not self.cookies_loaded:
                print("⚠️  No credentials or cookies provided. Login recommended for business account detection.")
            return False
            
        try:
            print("🔐 Logging into Instagram...")
            await self.page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
            await asyncio.sleep(3)
            
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
            
            # Try multiple methods to find and click login button
            login_button = None
            
            # Method 1: Try common selectors
            login_selectors = [
                'button[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Log In")',
                'button:has-text("Log")',
                'button._acan._acap._acas._aj1-',
                'button[class*="Log"]',
                'form button',
                'div[role="button"]:has-text("Log")'
            ]
            
            for selector in login_selectors:
                try:
                    login_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if login_button:
                        break
                except:
                    continue
            
            # Method 2: Try to find by text content
            if not login_button:
                try:
                    buttons = await self.page.query_selector_all('button')
                    for button in buttons:
                        text = await button.inner_text()
                        if 'log' in text.lower() and 'in' in text.lower():
                            login_button = button
                            break
                except:
                    pass
            
            # Method 3: Try pressing Enter on password field
            if not login_button:
                try:
                    await password_input.press('Enter')
                    await asyncio.sleep(5)
                    
                    # Check for OTP after Enter press
                    current_url = self.page.url
                    page_content = await self.page.content()
                    
                    otp_indicators = [
                        "challenge" in current_url.lower(),
                        "two_factor" in current_url.lower(),
                        "verify" in current_url.lower(),
                    ]
                    
                    if any(otp_indicators) or await self.check_for_otp_input():
                        print("\n🔐 Instagram requires verification (OTP/2FA)")
                        print("   Please enter the verification code in the browser window")
                        print("   Waiting for you to complete verification...\n")
                        
                        success = await self.wait_for_otp_completion()
                        if success:
                            self.logged_in = True
                            print("✅ Successfully logged in after verification!")
                            await self.handle_prompts()
                            return True
                        else:
                            return False
                    
                    if "accounts/login" not in current_url:
                        self.logged_in = True
                        print("✅ Successfully logged in!")
                        await self.handle_prompts()
                        return True
                except:
                    pass
            
            if login_button:
                await login_button.click()
                await asyncio.sleep(5)
                
                # Always check for OTP after login attempt - wait a bit more for page to load
                await asyncio.sleep(3)
                
                # Check if OTP/challenge is required - check multiple times
                for check_attempt in range(3):
                    current_url = self.page.url
                    page_content = await self.page.content()
                    
                    # Check for OTP/challenge indicators (including email verification)
                    otp_indicators = [
                        "challenge" in current_url.lower(),
                        "two_factor" in current_url.lower(),
                        "verify" in current_url.lower(),
                        "security" in current_url.lower(),
                        "accounts/challenge" in current_url.lower(),
                        "code" in page_content.lower() and ("verification" in page_content.lower() or "security" in page_content.lower() or "enter" in page_content.lower()),
                        # Email verification indicators
                        "check your email" in page_content.lower(),
                        "enter the code that we sent" in page_content.lower(),
                        "sent to" in page_content.lower() and "@" in page_content.lower() and "code" in page_content.lower(),
                        "get a new code" in page_content.lower()
                    ]
                    
                    has_otp_input = await self.check_for_otp_input()
                    
                    if any(otp_indicators) or has_otp_input:
                        print("\n" + "="*60)
                        print("🔐 Instagram requires verification")
                        print("="*60)
                        print("   This could be:")
                        print("   - Email verification code (Check your email)")
                        print("   - SMS verification code")
                        print("   - 2FA code")
                        print("")
                        print("   Please enter the verification code in the browser window")
                        print("   The scraper will wait for you to complete verification...")
                        print("   The scraper will auto-detect when you're done")
                        print("="*60 + "\n")
                        
                        # Wait for user to enter OTP and submit
                        success = await self.wait_for_otp_completion()
                        
                        if success:
                            self.logged_in = True
                            print("\n✅ Successfully logged in after verification!")
                            await self.save_cookies()  # Save cookies for next time
                            await self.handle_prompts()
                            return True
                        else:
                            print("\n❌ Verification failed or timeout")
                            return False
                    
                    # If not OTP page yet, wait a bit more and check again
                    if check_attempt < 2:
                        await asyncio.sleep(2)
                
                # Final check - wait a bit more and check again for OTP (sometimes it loads slowly)
                await asyncio.sleep(5)
                current_url = self.page.url
                page_content = await self.page.content()
                has_otp_input = await self.check_for_otp_input()
                
                # Check one more time for OTP (including email verification)
                otp_indicators_final = [
                    "challenge" in current_url.lower(),
                    "two_factor" in current_url.lower(),
                    "verify" in current_url.lower(),
                    "security" in current_url.lower(),
                    "accounts/challenge" in current_url.lower(),
                    # Email verification
                    "check your email" in page_content.lower(),
                    "enter the code that we sent" in page_content.lower(),
                ]
                
                if any(otp_indicators_final) or has_otp_input:
                    print("\n" + "="*60)
                    print("🔐 Instagram requires verification - Detected!")
                    print("="*60)
                    print("   This could be:")
                    print("   - Email verification code (Check your email)")
                    print("   - SMS verification code")
                    print("   - 2FA code")
                    print("")
                    print("   Please enter the verification code in the browser window")
                    print("   The scraper will wait for you to complete verification...")
                    print("="*60 + "\n")
                    
                    success = await self.wait_for_otp_completion()
                    if success:
                        self.logged_in = True
                        print("\n✅ Successfully logged in after verification!")
                        await self.handle_prompts()
                        return True
                    else:
                        return False
                
                # Normal login flow - check if we're logged in
                if "accounts/login" not in current_url and "challenge" not in current_url.lower():
                    self.logged_in = True
                    print("✅ Successfully logged in!")
                    await self.save_cookies()  # Save cookies for next time
                    await self.handle_prompts()
                    return True
                else:
                    # Still on login or challenge page
                    if "challenge" in current_url.lower() or "verify" in current_url.lower() or "check your email" in page_content.lower():
                        # OTP/Email verification page but detection might have failed - try waiting anyway
                        if not self.headless:
                            print("\n" + "="*60)
                            print("⚠️  Detected verification page (OTP or Email Code)")
                            print("="*60)
                            print("   If you see a code input in the browser, enter it now")
                            print("   This could be:")
                            print("   - Email verification code")
                            print("   - SMS verification code")
                            print("   - 2FA code")
                            print("   Waiting 30 seconds for manual verification...")
                            print("="*60 + "\n")
                            await asyncio.sleep(30)
                            
                            # Check again
                            current_url = self.page.url
                            if "accounts/login" not in current_url and "challenge" not in current_url.lower():
                                self.logged_in = True
                                print("✅ Successfully logged in!")
                                await self.handle_prompts()
                                return True
                    
                    print("❌ Login failed - still on login/challenge/verification page")
                    if not self.headless:
                        print("   💡 Check if credentials are correct")
                        print("   💡 If verification code is shown (email/SMS/2FA), enter it in the browser window")
                        print("   💡 The scraper will detect completion automatically")
                        print("   💡 Look for 'Check your email' or code input fields")
                    return False
            else:
                print("❌ Could not find login button")
                if not self.headless:
                    print("   💡 Try logging in manually in the browser window")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    async def check_for_otp_input(self) -> bool:
        """Check if OTP input field is present (including email verification)"""
        try:
            otp_selectors = [
                'input[name="verificationCode"]',
                'input[name="security_code"]',
                'input[name="code"]',
                'input[aria-label*="code"]',
                'input[aria-label*="Code"]',
                'input[aria-label*="verification"]',
                'input[type="text"][maxlength="6"]',
                'input[type="text"][maxlength="8"]',
                'input[type="tel"][maxlength="6"]',
                'input[type="tel"][maxlength="8"]',
                'input[placeholder*="code"]',
                'input[placeholder*="Code"]',
                'input[id*="code"]',
                'input[id*="Code"]',
                # Email verification specific
                'label:has-text("Code") + input',
                'input[aria-label="Code"]',
                'input[placeholder="Code"]'
            ]
            
            for selector in otp_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        # Verify it's visible
                        is_visible = await element.is_visible()
                        if is_visible:
                            return True
                except:
                    continue
            
            # Also check page content for OTP-related text (including email verification)
            try:
                page_text = await self.page.inner_text('body')
                otp_keywords = [
                    'verification code', 
                    'security code', 
                    'enter code', 
                    '6-digit code',
                    'confirmation code',
                    'two-factor',
                    'two factor',
                    # Email verification keywords
                    'check your email',
                    'enter the code that we sent',
                    'sent to',
                    'get a new code'
                ]
                if any(keyword in page_text.lower() for keyword in otp_keywords):
                    # Additional check: if it mentions email, make sure there's a code input
                    if 'check your email' in page_text.lower() or 'sent to' in page_text.lower():
                        # Look for any input field that could be for code
                        inputs = await self.page.query_selector_all('input[type="text"], input[type="tel"]')
                        if inputs:
                            return True
                    else:
                        return True
            except:
                pass
                
        except Exception as e:
            if not self.headless:
                pass  # Silently fail in headless mode
        
        return False
    
    async def wait_for_otp_completion(self, timeout: int = 600) -> bool:
        """
        Wait for user to manually enter OTP and complete verification
        Checks every 2 seconds for up to timeout seconds (default 10 minutes)
        """
        if self.headless:
            print("   ⚠️  OTP entry requires non-headless mode!")
            print("   Please run with headless=False to enter OTP")
            return False
        
        print(f"   ⏳ Waiting up to {timeout} seconds for OTP entry...")
        print(f"   💡 Enter the code in the browser window and click Submit")
        print(f"   💡 The scraper will automatically detect when verification is complete\n")
        
        start_time = asyncio.get_event_loop().time()
        last_url = self.page.url
        consecutive_same_url = 0
        
        while True:
            await asyncio.sleep(2)  # Check every 2 seconds
            
            try:
                current_url = self.page.url
                page_content = await self.page.content()
                
                # Check if URL changed (might indicate navigation after OTP)
                if current_url != last_url:
                    last_url = current_url
                    consecutive_same_url = 0
                else:
                    consecutive_same_url += 1
                
                # Check if we've successfully logged in (left the challenge/verification page)
                challenge_indicators = [
                    "challenge" in current_url.lower(),
                    "two_factor" in current_url.lower(),
                    "verify" in current_url.lower(),
                    "accounts/challenge" in current_url.lower(),
                    # Email verification page indicators
                    "check your email" in page_content.lower(),
                    "enter the code that we sent" in page_content.lower(),
                ]
                
                if not any(challenge_indicators):
                    if "accounts/login" not in current_url.lower():
                        # Successfully logged in - not on login or challenge page
                        elapsed = int(asyncio.get_event_loop().time() - start_time)
                        print(f"\n   ✅ Verification completed in {elapsed} seconds!")
                        await asyncio.sleep(2)  # Give it a moment to fully load
                        return True
                
                # Check for error messages
                error_indicators = [
                    "try again" in page_content.lower(),
                    "incorrect" in page_content.lower(),
                    "wrong code" in page_content.lower(),
                    "invalid" in page_content.lower()
                ]
                
                if any(error_indicators):
                    print("   ⚠️  Verification code may be incorrect. Please try again.")
                    await asyncio.sleep(3)  # Wait a bit before checking again
                
                # Check if OTP input field is gone (might mean submitted)
                has_otp_field = await self.check_for_otp_input()
                if not has_otp_field and any(challenge_indicators):
                    # OTP field gone but still on challenge page - might be processing
                    await asyncio.sleep(3)
                    # Check again
                    current_url = self.page.url
                    if "challenge" not in current_url.lower() and "accounts/login" not in current_url.lower():
                        elapsed = int(asyncio.get_event_loop().time() - start_time)
                        print(f"\n   ✅ Verification completed in {elapsed} seconds!")
                        return True
                
                # Timeout check
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    print(f"\n   ❌ Timeout after {timeout} seconds")
                    print(f"   💡 You can still complete verification manually in the browser")
                    print(f"   💡 The scraper will continue once you're logged in")
                    return False
                
                # Show progress every 20 seconds
                if int(elapsed) % 20 == 0 and elapsed > 0 and elapsed < timeout:
                    print(f"   ⏳ Still waiting... ({int(elapsed)}s / {timeout}s) - Enter code in browser window")
                    
            except Exception as e:
                # If there's an error checking, continue waiting
                if not self.headless:
                    print(f"   ⚠️  Error checking status: {str(e)}")
                await asyncio.sleep(2)
    
    async def handle_prompts(self):
        """Handle Instagram prompts after login"""
        prompts = ['button:has-text("Not Now")', 'button:has-text("Not now")']
        for _ in range(3):
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
    
    def is_business_account(self, page_content: str, bio: str = "") -> bool:
        """
        Detect if account is a business/professional account
        Business accounts have indicators like:
        - "is_business_account": true
        - "category" field
        - "business_contact_method"
        - "business_email"
        - "business_phone_number"
        - Contact button
        """
        # Method 1: Check JSON data for business account indicators
        business_indicators = [
            r'"is_business_account":\s*true',
            r'"is_professional_account":\s*true',
            r'"account_type":\s*[123]',  # 1=Personal, 2=Business, 3=Creator
            r'"category":\s*"([^"]+)"',
            r'"business_contact_method"',
            r'"business_email"',
            r'"business_phone_number"',
            r'"contact_phone_number"',
            r'"public_phone_country_code"',
        ]
        
        for pattern in business_indicators:
            if re.search(pattern, page_content, re.IGNORECASE):
                return True
        
        # Method 2: Check for business category in text
        if re.search(r'"category":\s*"([^"]+)"', page_content):
            return True
        
        # Method 3: Check bio for business indicators (less reliable)
        business_bio_keywords = [
            'brand', 'official', 'store', 'shop', 'business', 'company',
            'contact', 'email', 'call', 'whatsapp', 'website', 'www.'
        ]
        bio_lower = bio.lower()
        if any(keyword in bio_lower for keyword in business_bio_keywords):
            # Additional check: if it has contact info, likely business
            if re.search(r'\+91|email|contact|call|whatsapp', bio_lower):
                return True
        
        return False
    
    def is_indian_brand(self, page_content: str, bio: str = "") -> bool:
        """
        Detect if account is Indian brand
        Checks for:
        - Indian location keywords
        - Indian phone numbers (+91)
        - Indian cities
        - Location data indicating India
        """
        combined_text = (page_content + " " + bio).lower()
        
        # Check for Indian phone numbers
        if re.search(r'\+91[\s-]?\d', combined_text):
            return True
        
        # Check for Indian location keywords
        for keyword in self.indian_keywords:
            if keyword.lower() in combined_text:
                return True
        
        # Check for location data in JSON
        location_patterns = [
            r'"location":\s*"([^"]*india[^"]*)"',
            r'"country_code":\s*"IN"',
            r'"country":\s*"India"',
            r'"city_name":\s*"([^"]*)"',  # Indian cities
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                match_text = matches[0].lower()
                if any(indian_kw in match_text for indian_kw in ['india', 'indian', 'mumbai', 'delhi', 'bangalore']):
                    return True
        
        return False
    
    async def search_accounts_by_keyword(
        self,
        keyword: str,
        max_results: int = 50,
        seen_usernames: Optional[set] = None,
        stop_requested: Optional[Callable[[], bool]] = None,
    ) -> List[Dict]:
        """Search for business accounts matching keyword using Instagram search.
        If max_results is 0, no limit (used by infinite mode).
        """
        if not self.page:
            raise Exception("Browser not started. Call start() first.")
        
        if seen_usernames is None:
            seen_usernames = set()
        
        print(f"🔍 Searching for Indian business accounts matching: '{keyword}'")
        print(f"📋 Filters: Business account + Indian brand + 10K-50K followers\n")
        
        accounts = []
        
        # Method 1: Use Instagram's search API directly
        try:
            print("📱 Searching Instagram accounts...")
            
            # Use Instagram's search API endpoint
            search_url = f"https://www.instagram.com/web/search/topsearch/?query={keyword}"
            await self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            # Extract accounts from search API response
            usernames = await self.extract_accounts_from_search_api()
            
            if not usernames:
                # Fallback: Try using search page with input
                print("   Trying search page method...")
                await self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)
                
                # Find search input
                search_selectors = [
                    'input[placeholder*="Search"]',
                    'input[aria-label*="Search"]',
                    'input[type="text"]'
                ]
                
                search_input = None
                for selector in search_selectors:
                    try:
                        search_input = await self.page.wait_for_selector(selector, timeout=5000)
                        if search_input:
                            break
                    except:
                        continue
                
                if search_input:
                    await search_input.fill(keyword)
                    await asyncio.sleep(3)
                    usernames = await self.extract_accounts_from_search_results()
            
            if usernames:
                print(f"   Found {len(usernames)} accounts in search results")
            
            # Get MORE accounts: also run hashtag search and combine (don't navigate yet)
            more_usernames = await self.get_more_candidates_via_hashtag(keyword, limit=100)
            for u in more_usernames:
                if u not in usernames:
                    usernames.append(u)
            if more_usernames:
                print(f"   Added {len(more_usernames)} more from hashtag search (total: {len(usernames)} candidates)")
            
            # Optional: search with keyword variations for even more
            cap = (max_results * 5) if max_results > 0 else 500
            for variation in self._keyword_variations(keyword):
                if len(usernames) >= cap:  # Enough candidates
                    break
                await asyncio.sleep(1)
                await self.page.goto(f"https://www.instagram.com/web/search/topsearch/?query={variation}", wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(2)
                extra = await self.extract_accounts_from_search_api()
                for u in extra:
                    if u not in usernames:
                        usernames.append(u)
            if len(usernames) > 0:
                print(f"   Total unique candidates to check: {len(usernames)}\n")
            
            # Process found accounts
            check_limit = (max_results * 5) if max_results > 0 else len(usernames)
            if usernames:
                print(f"   Processing up to {min(check_limit, len(usernames))} accounts...\n")
                for username in usernames[:check_limit]:
                    if stop_requested and stop_requested():
                        return accounts
                    if username in seen_usernames:
                        continue
                    seen_usernames.add(username)
                    
                    account_data = await self.get_account_info(username)
                    
                    if account_data:
                        # Check if it's a business account
                        if not account_data.get('is_business', False):
                            if not self.headless:
                                print(f"   ⏭️  @{username}: Not a business account (skipping)")
                            continue
                        
                        # Check if it's Indian
                        if not account_data.get('is_indian', False):
                            if not self.headless:
                                print(f"   ⏭️  @{username}: Not an Indian brand (skipping)")
                            continue
                        
                        # Check follower count
                        followers = account_data.get('followers')
                        if followers and self.is_valid_follower_count(followers):
                            accounts.append(account_data)
                            n = len(accounts)
                            label = f"{n}" if max_results <= 0 else f"{n}/{max_results}"
                            print(f"✅ [{label}] @{username}: {followers:,} followers | {account_data.get('category', 'Business')}")
                            
                            if max_results > 0 and len(accounts) >= max_results:
                                return accounts
                        else:
                            if not self.headless:
                                print(f"   ⏭️  @{username}: {followers or 'Unknown'} followers (not in range)")
                    
                    await asyncio.sleep(2)  # Rate limiting
            
            # If no accounts found from search, fallback to hashtag method
            if not usernames:
                print("   No accounts found in search, trying hashtag method...")
                return await self.search_via_hashtags(keyword, max_results if max_results > 0 else 999999, seen_usernames)
        
        except Exception as e:
            print(f"❌ Error in account search: {str(e)}")
            if not self.headless:
                import traceback
                print(f"   Full error: {traceback.format_exc()}")
            
            # Fallback to hashtag method
            print("   Falling back to hashtag search method...")
            return await self.search_via_hashtags(keyword, max_results, seen_usernames)
        
        return accounts
    
    def _keyword_variations(self, keyword: str) -> List[str]:
        """Return related search terms to get more candidates."""
        k = keyword.strip().lower()
        variations = []
        # For skincare/beauty: add common related terms
        if "skin" in k or "care" in k or "beauty" in k or "skincare" in k:
            for term in ["skincare", "skin care", "beauty", "cosmetics"]:
                if term != k and term not in variations:
                    variations.append(term)
        # For fashion/apparel
        if "fashion" in k or "apparel" in k or "clothing" in k:
            for term in ["fashion", "apparel", "clothing", "style"]:
                if term != k and term not in variations:
                    variations.append(term)
        return variations[:4]  # Max 4 extra searches
    
    async def get_more_candidates_via_hashtag(self, keyword: str, limit: int = 100) -> List[str]:
        """Get usernames from hashtag page without full post navigation (quick extract)."""
        usernames = []
        try:
            url = f"https://www.instagram.com/explore/tags/{keyword}/"
            await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(4)
            for _ in range(2):
                try:
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                except:
                    break
            content = await self.page.content()
            # Extract /username/ from links to posts (owner often in same block)
            owner_matches = re.findall(r'"username"\s*:\s*"([^"]+)"', content)
            for u in owner_matches:
                if u not in usernames and u not in ['explore', 'accounts', 'direct', 'reels', 'stories', 'p', 'reel']:
                    usernames.append(u)
            # Also profile links
            for m in re.findall(r'href="/([a-zA-Z0-9._]+)/"', content):
                if m not in usernames and m not in ['explore', 'accounts', 'direct', 'reels', 'stories', 'p', 'reel']:
                    usernames.append(m)
        except Exception as e:
            if not self.headless:
                print(f"   ⚠️  Hashtag candidates: {str(e)}")
        return usernames[:limit]
    
    async def extract_accounts_from_search_results(self) -> List[str]:
        """Extract account usernames from search results dropdown"""
        usernames = []
        
        try:
            # Wait for search results
            await asyncio.sleep(2)
            
            # Look for account links in search dropdown
            account_selectors = [
                'a[href^="/"][href*="/"]',  # Profile links
                'div[role="link"] a[href^="/"]',
                'a[href*="/"]'
            ]
            
            seen_hrefs = set()
            for selector in account_selectors:
                try:
                    links = await self.page.query_selector_all(selector)
                    for link in links:
                        try:
                            href = await link.get_attribute('href')
                            if href:
                                # Extract username from href like /username/ or /username
                                match = re.match(r'^/([a-zA-Z0-9._]+)/?$', href)
                                if match:
                                    username = match.group(1)
                                    # Filter out non-account paths
                                    if username not in ['explore', 'accounts', 'direct', 'reels', 'stories', 'p', 'reel', '']:
                                        if username not in usernames:
                                            usernames.append(username)
                        except:
                            continue
                    
                    if usernames:
                        break
                except:
                    continue
            
            # Also extract from page content
            try:
                page_content = await self.page.content()
                # Look for usernames in JSON data
                username_patterns = [
                    r'"username":"([^"]+)"',
                    r'"profile_pic_url":"https://instagram\.com/([^/]+)/',
                    r'href="/([a-zA-Z0-9._]+)/"',
                ]
                
                for pattern in username_patterns:
                    matches = re.findall(pattern, page_content)
                    for match in matches:
                        username = match if isinstance(match, str) else match[0] if isinstance(match, tuple) else str(match)
                        if username and username not in usernames:
                            if username not in ['explore', 'accounts', 'direct', 'reels', 'stories', 'p', 'reel']:
                                usernames.append(username)
            except:
                pass
                
        except Exception as e:
            if not self.headless:
                print(f"   ⚠️  Error extracting from search results: {str(e)}")
        
        return usernames[:200]  # Get more candidates
    
    async def extract_accounts_from_search_api(self) -> List[str]:
        """Extract accounts from Instagram search API response"""
        usernames = []
        
        try:
            page_content = await self.page.content()
            
            # Try to parse JSON response
            json_match = re.search(r'<pre[^>]*>(.*?)</pre>', page_content, re.DOTALL)
            if not json_match:
                # Try script tag
                json_match = re.search(r'<script[^>]*>(.*?\{.*?\}.*?)</script>', page_content, re.DOTALL)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    users = data.get('users', [])
                    
                    for user_info in users:
                        user = user_info.get('user', {})
                        username = user.get('username')
                        if username:
                            usernames.append(username)
                except json.JSONDecodeError:
                    # Try to extract usernames directly from text
                    username_matches = re.findall(r'"username":"([^"]+)"', page_content)
                    for username in username_matches:
                        if username not in usernames:
                            usernames.append(username)
            
            # Fallback: Extract from any JSON-like structure
            if not usernames:
                username_matches = re.findall(r'"username"\s*:\s*"([^"]+)"', page_content)
                for username in username_matches:
                    if username not in usernames and len(username) > 2:
                        usernames.append(username)
                        
        except Exception as e:
            if not self.headless:
                print(f"   ⚠️  Error extracting from API: {str(e)}")
        
        return usernames[:200]  # Get more from API
    
    async def search_via_hashtags(self, keyword: str, max_results: int, seen_usernames: set) -> List[Dict]:
        """Fallback method: Search via hashtags and extract from posts"""
        accounts = []
        
        try:
            print("📱 Searching via hashtags (fallback method)...")
            search_url = f"https://www.instagram.com/explore/tags/{keyword}/"
            await self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)
            
            # Scroll to load posts
            for _ in range(3):
                try:
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                except:
                    break
            
            await asyncio.sleep(3)
            
            # Extract post hrefs from page source
            post_hrefs = []
            try:
                page_content = await self.page.content()
                post_urls = re.findall(r'href="(/p/[^"]+)"', page_content)
                post_urls.extend(re.findall(r'href="(/reel/[^"]+)"', page_content))
                
                seen_hrefs = set()
                for url in post_urls:
                    if url not in seen_hrefs and url.startswith('/'):
                        seen_hrefs.add(url)
                        post_hrefs.append(url)
            except:
                pass
            
            post_hrefs = post_hrefs[:max_results * 5]
            print(f"   Found {len(post_hrefs)} posts to check")
            
            # Process posts
            for i, href in enumerate(post_hrefs):
                try:
                    post_url = f"https://www.instagram.com{href}"
                    await self.page.goto(post_url, wait_until="domcontentloaded", timeout=20000)
                    await asyncio.sleep(3)
                    
                    username = await self.extract_username_from_post()
                    
                    if username and username not in seen_usernames:
                        seen_usernames.add(username)
                        account_data = await self.get_account_info(username)
                        
                        if account_data:
                            if not account_data.get('is_business', False):
                                continue
                            if not account_data.get('is_indian', False):
                                continue
                            
                            followers = account_data.get('followers')
                            if followers and self.is_valid_follower_count(followers):
                                accounts.append(account_data)
                                print(f"✅ [{len(accounts)}/{max_results}] @{username}: {followers:,} followers")
                                
                                if len(accounts) >= max_results:
                                    return accounts
                    
                    await asyncio.sleep(2)
                except:
                    continue
                    
        except Exception as e:
            if not self.headless:
                print(f"   ⚠️  Hashtag search error: {str(e)}")
        
        return accounts
    
    async def extract_username_from_post(self) -> Optional[str]:
        """Extract username from a post page"""
        try:
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
            
            # Parse from page source
            page_content = await self.page.content()
            username_patterns = [
                r'"owner":\{"username":"([^"]+)"',
                r'"username":"([^"]+)"',
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
        """Get account information with business and Indian checks"""
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            await self.page.goto(profile_url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(3)
            
            page_content = await self.page.content()
            
            # Extract bio
            bio = ""
            try:
                bio_elements = await self.page.query_selector_all('span:has-text("")')
                # Try to get bio from page content
                bio_match = re.search(r'"biography":"([^"]*)"', page_content)
                if bio_match:
                    bio = bio_match.group(1)
            except:
                pass
            
            # Check if business account
            is_business = self.is_business_account(page_content, bio)
            
            # Check if Indian
            is_indian = self.is_indian_brand(page_content, bio)
            
            # Extract follower count
            followers = None
            patterns = [
                r'"edge_followed_by":\{"count":(\d+)\}',
                r'"follower_count":(\d+)',
                r'"followers":\{"count":(\d+)\}',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    try:
                        followers = int(matches[0])
                        break
                    except:
                        continue
            
            if not followers:
                text_patterns = [
                    r'(\d+[.,]?\d*[KMB]?)\s*followers',
                ]
                for pattern in text_patterns:
                    matches = re.findall(pattern, page_content, re.IGNORECASE)
                    if matches:
                        followers = self.parse_followers(matches[0])
                        if followers:
                            break
            
            # Extract category if business account
            category = None
            if is_business:
                category_match = re.search(r'"category":\s*"([^"]+)"', page_content)
                if category_match:
                    category = category_match.group(1)
                else:
                    category = "Business"
            
            return {
                'username': username,
                'link': profile_url,
                'followers': followers,
                'is_business': is_business,
                'is_indian': is_indian,
                'category': category,
                'bio': bio[:200] if bio else ""  # First 200 chars
            }
            
        except Exception as e:
            if not self.headless:
                print(f"   ⚠️  Error getting info for @{username}: {str(e)}")
            return None


# Used by infinite mode: set to True on Ctrl+C
_stop_infinite = False


async def scrape_indian_business_accounts(
    keyword: str,
    max_results: int = 50,
    username: Optional[str] = None,
    password: Optional[str] = None,
    cookies_file: Optional[str] = None,
    headless: bool = False,
    infinite: bool = False,
    save_every: int = 10,
) -> List[Dict]:
    """
    Scrape Indian business accounts
    
    Args:
        keyword: Domain/keyword to search for
        max_results: Maximum number of accounts to return (ignored if infinite=True)
        username: Instagram username (optional if using cookies)
        password: Instagram password (optional if using cookies)
        cookies_file: Path to cookies JSON file (optional)
        headless: Run browser in headless mode
        infinite: If True, run until stopped (Ctrl+C); always within same domain/keyword
        save_every: When infinite, save results to file every N new accounts
    
    Returns:
        List of dicts with username, link, followers, is_business, is_indian, category
    """
    global _stop_infinite
    _stop_infinite = False
    
    scraper = BusinessIndianScraper(username, password, cookies_file, headless)
    
    try:
        await scraper.start()
        await scraper.login()
        
        if infinite:
            return await _run_infinite(scraper, keyword, save_every)
        
        accounts = await scraper.search_accounts_by_keyword(keyword, max_results)
        return accounts
        
    finally:
        await scraper.close()


async def _run_infinite(scraper: BusinessIndianScraper, keyword: str, save_every: int) -> List[Dict]:
    """Run scraper until stopped. Same domain/keyword only. Saves periodically."""
    global _stop_infinite
    all_accounts: List[Dict] = []
    seen_usernames: set = set()
    save_path = f"indian_business_accounts_{keyword}_infinite.json"
    
    def stop_check() -> bool:
        return _stop_infinite
    
    while not _stop_infinite:
        batch = await scraper.search_accounts_by_keyword(
            keyword,
            max_results=0,
            seen_usernames=seen_usernames,
            stop_requested=stop_check,
        )
        
        if batch:
            for acc in batch:
                if acc["username"] not in {a["username"] for a in all_accounts}:
                    all_accounts.append(acc)
            print(f"\n   📊 Total so far: {len(all_accounts)} accounts (domain: {keyword})")
            
            if len(all_accounts) % save_every == 0 or batch:
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(all_accounts, f, indent=2, ensure_ascii=False)
                print(f"   💾 Saved to {save_path}")
        
        if _stop_infinite:
            break
        
        # Brief pause before next round of search (same keyword)
        print("\n   🔄 Next round of search (same domain)... Press Ctrl+C to stop.\n")
        await asyncio.sleep(5)
    
    # Final save
    if all_accounts:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(all_accounts, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Final save: {save_path} ({len(all_accounts)} accounts)")
    
    return all_accounts


if __name__ == "__main__":
    import sys
    import signal
    
    if len(sys.argv) < 2:
        print("Usage: python instagram_scraper_business_indian.py <keyword> [max_results|infinite] [headless] [cookies_file]")
        print("Example: python instagram_scraper_business_indian.py skinkare 50 false")
        print("Example: python instagram_scraper_business_indian.py skinkare infinite false   # Run until you press Ctrl+C")
        print("\nFilters:")
        print("  ✅ Business/Professional accounts only")
        print("  ✅ Indian brands/location")
        print("  ✅ 10K-50K followers")
        print("\nInfinite mode: Use 'infinite' as max_results to run until you stop (Ctrl+C). Same domain only.")
        print("\nAuthentication options:")
        print("  1. Use cookies file (recommended): Set INSTAGRAM_COOKIES_FILE in .env or pass as argument")
        print("  2. Use login: Add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD to .env file")
        print("\nCookies will be automatically saved after successful login!")
        sys.exit(1)
    
    keyword = sys.argv[1]
    max_arg = sys.argv[2] if len(sys.argv) > 2 else "50"
    infinite_mode = max_arg.lower() == "infinite" or max_arg == "0"
    max_results = 0 if infinite_mode else int(max_arg)
    headless = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    cookies_file = sys.argv[4] if len(sys.argv) > 4 else None
    
    if infinite_mode:
        # Set global stop flag on Ctrl+C
        def _on_sigint(*args):
            global _stop_infinite
            _stop_infinite = True
            print("\n\n⏹️  Stop requested (Ctrl+C). Finishing current check and saving...")
        signal.signal(signal.SIGINT, _on_sigint)
    
    print(f"\n🚀 Starting Indian Business Account Scraper")
    print(f"📝 Keyword/domain: {keyword}")
    print(f"🎯 Filters: Business Account + Indian Brand + 10K-50K followers")
    if infinite_mode:
        print(f"📊 Mode: INFINITE (same domain only) — Press Ctrl+C to stop")
        print(f"💾 Saving to: indian_business_accounts_{keyword}_infinite.json (updated periodically)")
    else:
        print(f"📊 Max results: {max_results}")
    print(f"👁️  Headless mode: {headless}")
    
    if headless:
        print("⚠️  Note: If Instagram requires OTP/2FA, you'll need to run with headless=False")
    
    print()
    
    try:
        results = asyncio.run(scrape_indian_business_accounts(
            keyword,
            max_results,
            cookies_file=cookies_file,
            headless=headless,
            infinite=infinite_mode,
            save_every=10,
        ))
    except KeyboardInterrupt:
        results = []  # Already saved by _run_infinite if infinite mode
    
    if results:
        print(f"\n✨ Found {len(results)} Indian business accounts:")
        for acc in results[:20]:  # Show first 20
            print(f"\n  @{acc['username']}")
            print(f"    Followers: {acc['followers']:,}")
            print(f"    Category: {acc.get('category', 'N/A')}")
            print(f"    Link: {acc['link']}")
        if len(results) > 20:
            print(f"\n  ... and {len(results) - 20} more")
        
        if not infinite_mode:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"indian_business_accounts_{keyword}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {filename}")
        else:
            print(f"\n💾 Results saved to: indian_business_accounts_{keyword}_infinite.json")
    else:
        print("\n❌ No Indian business accounts found matching the criteria")
        print("💡 Tips:")
        print("   - Try different keywords")
        print("   - Make sure to login for better detection")
        print("   - Run with headless=False to see filtering process")
