# Environment Variables Setup

## Quick Setup

The scraper now reads Instagram credentials from the `.env` file automatically.

### Step 1: Edit `.env` file

Open the `.env` file in the project root and add your Instagram credentials:

```env
INSTAGRAM_USERNAME="your_instagram_username"
INSTAGRAM_PASSWORD="your_instagram_password"
```

### Step 2: Save and Run

That's it! The scraper will automatically load credentials from `.env` when you run:

```bash
python instagram_scraper_business_indian.py skinkare 50
```

## Example .env File

```env
//if limit excessed, regenerate key and you are good to go!
GEMINI_API_KEY=""
// Optional: Set a custom URL for the default landing page
DEFAULT_URL="https://tootler.ai/"

// Instagram credentials for scraper
INSTAGRAM_USERNAME="your_instagram_username"
INSTAGRAM_PASSWORD="your_instagram_password"
```

## Important Notes

⚠️ **Security:**
- The `.env` file is already in `.gitignore` - your credentials won't be committed
- Never share your `.env` file or commit it to version control
- Keep your credentials secure

⚠️ **Optional:**
- If you don't add credentials, the scraper will still work but with limited functionality
- Login is recommended for better business account detection

## Alternative: Environment Variables

You can also set environment variables directly (but `.env` is easier):

```bash
export INSTAGRAM_USERNAME="your_username"
export INSTAGRAM_PASSWORD="your_password"
```

## Verification

To verify credentials are loaded:

```bash
python test_business_indian.py
```

If credentials are found, you'll see:
```
✅ Using Instagram account: your_username
```

If not found:
```
⚠️  No Instagram credentials found!
   Add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD to .env file
```
