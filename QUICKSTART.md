# Quick Start Guide

## 🚀 Best Approach for Your Use Case

**Recommended: Playwright-based scraper** (already implemented)

### Why Playwright?
- ✅ Handles Instagram's dynamic JavaScript content
- ✅ Can simulate real browser behavior
- ✅ Supports login for better results
- ✅ Good balance of reliability and ease of use
- ✅ Works well for your scale (searching by keyword, filtering 10K-50K followers)

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

## Usage

### Option 1: Basic Scraper (No Login Required)
```bash
python instagram_scraper.py skinkare 50
```

### Option 2: Advanced Scraper (With Login - Better Results)
```bash
# Set credentials (optional, but recommended)
export INSTAGRAM_USERNAME='your_username'
export INSTAGRAM_PASSWORD='your_password'

python instagram_scraper_advanced.py skinkare 50
```

### Option 3: Use as Python Module
```python
import asyncio
from instagram_scraper import scrape_instagram

async def main():
    results = await scrape_instagram("skinkare", max_results=50)
    for acc in results:
        print(f"@{acc['username']}: {acc['followers']:,} followers")

asyncio.run(main())
```

## Output Format

Results are saved as JSON:
```json
[
  {
    "username": "example_account",
    "link": "https://www.instagram.com/example_account/",
    "followers": 25000
  }
]
```

## Important Notes

⚠️ **Instagram's Terms of Service:**
- Instagram prohibits scraping in their ToS
- Use responsibly and for research/educational purposes
- Consider Instagram Graph API for production use

⚠️ **Rate Limiting:**
- The scraper includes delays to avoid being blocked
- If you get blocked, wait 1-2 hours before trying again
- Using login helps reduce blocking

⚠️ **Accuracy:**
- Follower counts are parsed from page content
- Instagram's structure changes frequently
- May need updates if Instagram changes their HTML

## Troubleshooting

**Problem:** No results found
- **Solution:** Try running with `headless=False` to see what's happening
- **Solution:** Add login credentials for better results
- **Solution:** Check if Instagram is blocking your IP

**Problem:** Rate limited / Blocked
- **Solution:** Wait 1-2 hours
- **Solution:** Use a VPN/proxy
- **Solution:** Reduce `max_results` and add longer delays

**Problem:** Login fails
- **Solution:** Check credentials are correct
- **Solution:** Instagram may require 2FA - handle manually
- **Solution:** Try running in non-headless mode to see the issue

## Alternative Approaches (If Playwright Doesn't Work)

### 1. Instagram Graph API (Most Legitimate)
- Requires Facebook Business account
- Apply for access at: https://developers.facebook.com/docs/instagram-api
- Best for production use

### 2. Third-Party APIs
- **RapidAPI**: Search "Instagram API" - costs ~$10-50/month
- **Apify**: Instagram Scraper actors - pay per use
- Easiest but costs money

### 3. Manual Export
- Use Instagram's native search
- Export results manually
- Most reliable but not automated

## Next Steps

1. **Test the basic scraper** first
2. **Add login** if you need better results
3. **Adjust delays** if you're getting blocked
4. **Consider alternatives** if Playwright doesn't work for your needs
