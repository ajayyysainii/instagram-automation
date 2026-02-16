# How to Use the Instagram Scraper

## Quick Start

### Option 1: Use the Working Scraper (Recommended)

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the scraper (non-headless to see what's happening)
python instagram_scraper_working.py skinkare 50

# Or run in headless mode
python instagram_scraper_working.py skinkare 50 true
```

### Option 2: Test First

```bash
# Run the test script to verify everything works
python test_scraper.py
```

## What the Scraper Does

1. **Searches Instagram** for accounts related to your keyword
2. **Extracts account information** (username, link, followers)
3. **Filters accounts** with 10K-50K followers
4. **Saves results** to a JSON file

## Methods Used

The scraper uses **3 different methods** to find accounts:

1. **Hashtag Search** - Searches Instagram hashtags
2. **API Search** - Uses Instagram's internal search API
3. **Post Extraction** - Extracts accounts from posts

If one method fails, it automatically tries the next one.

## Troubleshooting

### Problem: No results found

**Solutions:**
1. **Run with headless=False** to see what's happening:
   ```bash
   python instagram_scraper_working.py skinkare 50 false
   ```

2. **Add Instagram login** (recommended for better results):
   - Edit `.env` file and add:
   ```env
   INSTAGRAM_USERNAME="your_username"
   INSTAGRAM_PASSWORD="your_password"
   ```
   - Then run: `python instagram_scraper_working.py skinkare 50`

3. **Check your keyword** - Make sure it exists on Instagram
   - Try common keywords like "skincare", "fashion", "fitness"

4. **Check internet connection** - Make sure you're online

### Problem: Getting blocked

**Solutions:**
1. **Wait 1-2 hours** before trying again
2. **Use login credentials** - Logged-in users get better access
3. **Reduce max_results** - Try with smaller numbers first
4. **Add delays** - The scraper already includes delays, but you can increase them

### Problem: Can't find follower count

**Solutions:**
1. **Login is required** - Instagram hides follower counts for non-logged-in users
2. **Run with headless=False** - See if the page is loading correctly
3. **Check if account is private** - Private accounts won't show follower counts

## Example Usage

```python
import asyncio
from instagram_scraper_working import scrape_instagram_working

async def main():
    results = await scrape_instagram_working(
        keyword="skinkare",
        max_results=50,
        username="your_username",  # Optional but recommended
        password="your_password",  # Optional but recommended
        headless=False  # Set to True to run in background
    )
    
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

## Tips for Best Results

1. ✅ **Use login credentials** - Much better results
2. ✅ **Start with small max_results** - Test with 5-10 first
3. ✅ **Use specific keywords** - "skincare" is better than "sk"
4. ✅ **Run with headless=False first** - See what's happening
5. ✅ **Be patient** - Instagram has rate limits

## Files

- `instagram_scraper_working.py` - **Main working scraper** (use this one!)
- `instagram_scraper_advanced.py` - Advanced version with login
- `instagram_scraper.py` - Basic version
- `test_scraper.py` - Test script to verify setup

## Need Help?

If the scraper still doesn't work:

1. Check the error messages when running with `headless=False`
2. Make sure Playwright browsers are installed: `playwright install chromium`
3. Try the test script: `python test_scraper.py`
4. Check Instagram is accessible in your browser
