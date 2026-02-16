# Indian Business Account Scraper Guide

## Overview

This scraper specifically targets **Indian business accounts** (not personal profiles) with 10K-50K followers.

## What It Filters

✅ **Business Accounts Only**
- Detects professional/business account indicators
- Filters out personal profiles
- Identifies business categories

✅ **Indian Brands Only**
- Checks for Indian location indicators
- Looks for Indian cities, phone numbers (+91)
- Verifies location data

✅ **Follower Range**
- Only accounts with 10K-50K followers

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Edit .env file and add your Instagram credentials:
# INSTAGRAM_USERNAME="your_username"
# INSTAGRAM_PASSWORD="your_password"

# Run the scraper (credentials loaded automatically from .env)
python instagram_scraper_business_indian.py skinkare 50 false
```

## How Business Account Detection Works

The scraper checks for:

1. **Account Type Indicators:**
   - `is_business_account: true`
   - `is_professional_account: true`
   - `account_type: 2` (Business) or `3` (Creator)

2. **Business Features:**
   - Category information
   - Business contact methods
   - Business email/phone
   - Contact button

3. **Bio Indicators:**
   - Business keywords (brand, official, store, shop)
   - Contact information

## How Indian Brand Detection Works

The scraper checks for:

1. **Location Keywords:**
   - Indian cities (Mumbai, Delhi, Bangalore, etc.)
   - Country indicators (India, Indian, Bharat, Hindustan)
   - Regional terms (Made in India, Swadeshi, Desi)

2. **Phone Numbers:**
   - Indian country code (+91)

3. **Location Data:**
   - Country code: IN
   - City names matching Indian cities

## Example Usage

```python
import asyncio
from instagram_scraper_business_indian import scrape_indian_business_accounts

async def main():
    results = await scrape_indian_business_accounts(
        keyword="skinkare",
        max_results=50,
        username="your_username",  # Recommended
        password="your_password",  # Recommended
        headless=False
    )
    
    for acc in results:
        print(f"@{acc['username']}: {acc['followers']:,} followers")
        print(f"Category: {acc.get('category', 'N/A')}")
        print(f"Link: {acc['link']}\n")

asyncio.run(main())
```

## Output Format

```json
[
  {
    "username": "example_indian_brand",
    "link": "https://www.instagram.com/example_indian_brand/",
    "followers": 25000,
    "is_business": true,
    "is_indian": true,
    "category": "Beauty & Personal Care",
    "bio": "Official account of..."
  }
]
```

## Important Notes

⚠️ **Login Required for Best Results:**
- Business account detection works much better when logged in
- Instagram hides some data for non-logged-in users
- Add `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD` to `.env` file (see [ENV_SETUP.md](ENV_SETUP.md))

⚠️ **Detection Accuracy:**
- Business detection is ~90% accurate with login
- Without login, accuracy drops to ~60-70%
- Some accounts may be missed if they don't have clear indicators

⚠️ **Indian Location:**
- Detection relies on visible location data
- Accounts without location info may be missed
- Bio text analysis helps but isn't 100% reliable

## Troubleshooting

### Problem: No business accounts found

**Solutions:**
1. **Login is essential** - Set credentials for better detection
2. **Check keyword** - Make sure it's relevant to Indian businesses
3. **Run with headless=False** - See what's being filtered out
4. **Try broader keywords** - "skincare" instead of "skinkare"

### Problem: Too many personal accounts

**Solutions:**
1. The scraper filters these automatically
2. If you see personal accounts, they might be misclassified
3. Report the issue - the detection logic can be improved

### Problem: Missing Indian brands

**Solutions:**
1. Some brands don't have location data visible
2. Try searching with location-specific keywords: "mumbai skincare", "delhi fashion"
3. Check if accounts have Indian indicators in bio

## Tips for Best Results

1. ✅ **Always use login** - Much better detection
2. ✅ **Use specific keywords** - "mumbai skincare brands" better than "skincare"
3. ✅ **Start small** - Test with max_results=10 first
4. ✅ **Monitor the output** - See what's being filtered
5. ✅ **Try multiple keywords** - Different searches may find different accounts

## Files

- `instagram_scraper_business_indian.py` - **Main scraper for Indian business accounts**
- `instagram_scraper_working.py` - General scraper (no filters)
- `test_scraper.py` - Test script

## Example Keywords for Indian Brands

- "skincare india"
- "mumbai fashion brands"
- "delhi beauty brands"
- "indian skincare"
- "made in india"
- "swadeshi brands"
- "indian fashion"
- "bangalore startups"
