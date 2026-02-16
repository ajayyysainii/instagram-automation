# Using Cookies with Instagram Scraper

## Why Use Cookies?

✅ **Skip Login/OTP**: No need to enter credentials or verification codes  
✅ **Faster**: Instant authentication  
✅ **More Reliable**: Avoids login detection issues  
✅ **Persistent**: Cookies work until they expire  

## Quick Start

### Option 1: Export Cookies (Recommended)

1. **Run the cookie exporter:**
   ```bash
   python export_cookies.py false
   ```

2. **Log in manually:**
   - Browser window will open
   - Log into Instagram (including OTP if needed)
   - Wait until you see your Instagram feed
   - Press Enter in the terminal

3. **Cookies are saved:**
   - Cookies saved to `instagram_cookies.json`
   - Use them automatically next time!

### Option 2: Provide Your Own Cookies File

If you already have cookies from another tool:

1. **Save cookies as JSON:**
   ```json
   [
     {
       "name": "sessionid",
       "value": "your_session_id_value",
       "domain": ".instagram.com",
       "path": "/",
       "expires": 1234567890,
       "httpOnly": true,
       "secure": true,
       "sameSite": "None"
     }
   ]
   ```

2. **Use with scraper:**
   ```bash
   python instagram_scraper_business_indian.py skinkare 50 false cookies.json
   ```

## Usage

### Automatic (from .env)

Add to `.env` file:
```env
INSTAGRAM_COOKIES_FILE="instagram_cookies.json"
```

Then run normally:
```bash
python instagram_scraper_business_indian.py skinkare 50
```

### Manual (command line)

```bash
python instagram_scraper_business_indian.py skinkare 50 false cookies.json
```

## How It Works

1. **Scraper starts** → Checks for cookies file
2. **Loads cookies** → If file exists, loads cookies into browser
3. **Checks login** → Verifies if cookies work (you're logged in)
4. **If cookies work** → Skips login, starts scraping immediately!
5. **If cookies don't work** → Falls back to login with credentials
6. **After login** → Automatically saves cookies for next time

## Cookie File Format

Cookies should be a JSON array:

```json
[
  {
    "name": "sessionid",
    "value": "abc123...",
    "domain": ".instagram.com",
    "path": "/",
    "expires": 1735689600,
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  },
  {
    "name": "csrftoken",
    "value": "xyz789...",
    "domain": ".instagram.com",
    "path": "/",
    "expires": 1735689600,
    "httpOnly": false,
    "secure": true,
    "sameSite": "Lax"
  }
]
```

## Getting Cookies from Browser

### Chrome/Edge:

1. Open Instagram and log in
2. Press F12 (Developer Tools)
3. Go to Application tab → Cookies → https://www.instagram.com
4. Copy relevant cookies (sessionid, csrftoken, etc.)
5. Format as JSON array

### Firefox:

1. Open Instagram and log in
2. Press F12 (Developer Tools)
3. Go to Storage tab → Cookies → https://www.instagram.com
4. Copy relevant cookies
5. Format as JSON array

### Using Browser Extension:

Use extensions like:
- "Cookie-Editor" (Chrome/Firefox)
- "EditThisCookie" (Chrome)
- Export cookies as JSON

## Important Notes

⚠️ **Security:**
- Cookies contain your session - keep them secure!
- Don't share cookies files
- Cookies are in `.gitignore` by default

⚠️ **Expiration:**
- Cookies expire after some time
- If cookies stop working, re-export them
- The scraper will auto-fallback to login if cookies fail

⚠️ **File Location:**
- Default: `instagram_cookies.json` in project root
- Can specify custom path in `.env` or command line

## Troubleshooting

### Problem: Cookies not working

**Solution:**
1. Re-export cookies: `python export_cookies.py false`
2. Make sure you're fully logged in before exporting
3. Check cookie file format (must be valid JSON array)

### Problem: "No cookies found"

**Solution:**
- Make sure cookie file exists
- Check file path in `.env` or command line
- Verify JSON format is correct

### Problem: Cookies expired

**Solution:**
- Re-export cookies
- Cookies typically last days/weeks
- Scraper will auto-fallback to login if expired

## Example Workflow

```bash
# Step 1: Export cookies (one time, or when expired)
python export_cookies.py false
# [Log in manually, press Enter]

# Step 2: Use scraper with cookies (automatic)
python instagram_scraper_business_indian.py skinkare 50
# ✅ Uses cookies automatically, no login needed!

# Step 3: Cookies auto-saved after login (if you use login method)
# Next time, cookies will be used automatically
```

## Benefits

- 🚀 **Faster**: No login delay
- 🔒 **More Secure**: No credentials needed after initial setup
- ✅ **Reliable**: Avoids OTP/verification issues
- 💾 **Persistent**: Works until cookies expire
