# Instagram Scraper

A Python scraper that searches Instagram for accounts based on keywords/domains and filters accounts with followers between 10K to 50K.

## 🆕 Indian Business Account Scraper

**NEW:** `instagram_scraper_business_indian.py` - Specifically filters for:
- ✅ Business/Professional accounts only (not personal)
- ✅ Indian brands/location
- ✅ 10K-50K followers

See [BUSINESS_INDIAN_GUIDE.md](BUSINESS_INDIAN_GUIDE.md) for details.

## Features

- 🔍 Search Instagram accounts by keyword/domain
- 📊 Filter accounts by follower count (10K - 50K)
- 💾 Export results to JSON
- 🚀 Async/await for better performance
- 🛡️ Rate limiting and error handling

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Set up Instagram credentials (recommended):
   - Edit `.env` file and add:
   ```env
   INSTAGRAM_USERNAME="your_instagram_username"
   INSTAGRAM_PASSWORD="your_instagram_password"
   ```
   - See [ENV_SETUP.md](ENV_SETUP.md) for details

## Usage

### Basic Usage

```bash
python instagram_scraper.py <keyword> [max_results]
```

**Examples:**
```bash
# Search for "skinkare" accounts
python instagram_scraper.py skinkare 50

# Search for "apparel" accounts
python instagram_scraper.py apparel 100
```

### Programmatic Usage

```python
from instagram_scraper import scrape_instagram

# Scrape accounts
accounts = await scrape_instagram("skinkare", max_results=50)

# Results format:
# [
#     {
#         "username": "example_user",
#         "link": "https://www.instagram.com/example_user/",
#         "followers": 25000
#     },
#     ...
# ]
```

## Output

Results are saved to a JSON file with timestamp:
- Format: `instagram_results_{keyword}_{timestamp}.json`
- Contains: username, link, followers

## Important Notes

⚠️ **Legal & Ethical Considerations:**
- Instagram's Terms of Service prohibit scraping
- Use responsibly and respect rate limits
- Consider using Instagram's official API for production use
- This tool is for educational/research purposes

⚠️ **Technical Limitations:**
- Instagram has anti-scraping measures
- May require login for better results
- Rate limiting may affect performance
- Instagram's HTML structure changes frequently

## Approach Comparison

### ✅ **Playwright (Current Implementation) - RECOMMENDED**
- **Pros:** 
  - Handles JavaScript and dynamic content
  - Reliable and modern
  - Can handle login flows
  - Good for personal use and research
- **Cons:** 
  - Slower than direct API calls
  - Requires browser installation
  - Can be detected by Instagram
- **Best for:** Personal use, research, small to medium-scale scraping

### Alternative Approaches:

1. **Instagram Graph API (Official) - BEST FOR PRODUCTION**
   - ✅ Legal and legitimate
   - ✅ Reliable and maintained
   - ❌ Requires business account and approval
   - ❌ Limited access and features
   - ❌ Doesn't support keyword search easily
   - **Best for:** Production applications, businesses

2. **Third-party APIs (EASIEST)**
   - ✅ Simple to use
   - ✅ Well-maintained
   - ✅ Handles rate limiting
   - ❌ Costs money (usually $10-50/month)
   - ❌ Rate limits
   - **Best for:** Quick implementation, production use
   - **Examples:** RapidAPI Instagram APIs, Apify

3. **Selenium (ALTERNATIVE TO PLAYWRIGHT)**
   - ✅ Similar to Playwright
   - ✅ More established ecosystem
   - ❌ Slower than Playwright
   - ❌ More resource-intensive
   - **Best for:** If you prefer Selenium ecosystem

4. **Direct HTTP Requests (ADVANCED)**
   - ✅ Fastest method
   - ✅ No browser overhead
   - ❌ Requires reverse engineering Instagram's API
   - ❌ High risk of being blocked
   - ❌ Breaks frequently when Instagram updates
   - **Best for:** Advanced users, high-volume scraping

## Recommendation

**For your use case (scraping by keyword, filtering 10K-50K followers):**

1. **Start with Playwright** (current implementation) - Good balance of ease and functionality
2. **If you need production reliability** - Use Instagram Graph API or third-party APIs
3. **If you need high volume** - Consider third-party APIs or direct HTTP with proper proxy rotation

## Troubleshooting

- **No results found:** Instagram may have blocked the request. Try:
  - Running in non-headless mode (`headless=False`)
  - Adding delays between requests
  - Using a VPN/proxy
  
- **Rate limiting:** Add longer delays between requests in the code

- **Login required:** You may need to add login functionality for better results

## Future Improvements

- [ ] Add Instagram login support
- [ ] Implement proxy rotation
- [ ] Add retry logic for failed requests
- [ ] Support CSV export
- [ ] Add progress bar
- [ ] Implement caching to avoid duplicate requests
