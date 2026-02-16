# OTP/2FA Support Guide

## Overview

The scraper now supports Instagram's OTP (One-Time Password) and 2FA (Two-Factor Authentication) verification. When Instagram requires verification, the scraper will pause and wait for you to manually enter the code.

## How It Works

1. **Automatic Detection**: The scraper detects when Instagram shows an OTP/challenge page
2. **Pause & Wait**: It pauses execution and waits for you to enter the OTP
3. **Manual Entry**: You enter the OTP in the browser window (must run with `headless=False`)
4. **Auto-Continue**: Once verification is complete, the scraper automatically continues

## Usage

### Step 1: Run with Non-Headless Mode

**Important**: OTP entry requires the browser window to be visible:

```bash
# Run with headless=False (or omit it, defaults to False)
python instagram_scraper_business_indian.py skinkare 50 false
```

### Step 2: Enter Credentials

The scraper will automatically fill in your username and password from `.env` file.

### Step 3: Wait for OTP Prompt

When Instagram requires verification, you'll see:

```
🔐 Instagram requires verification (OTP/2FA)
   Please enter the verification code in the browser window
   Waiting for you to complete verification...

   ⏳ Waiting up to 300 seconds for OTP entry...
```

### Step 4: Enter OTP

1. Look at the browser window that opened
2. Enter the 6-digit code you received (via SMS, email, or authenticator app)
3. Click "Confirm" or "Submit" in Instagram
4. The scraper will automatically detect completion and continue

### Step 5: Automatic Continuation

Once verification is successful:

```
   ✅ Verification completed in 45 seconds!
✅ Successfully logged in after verification!
```

## Features

✅ **Automatic Detection**: Detects OTP/challenge pages automatically  
✅ **Smart Waiting**: Waits up to 5 minutes (300 seconds) for OTP entry  
✅ **Progress Updates**: Shows waiting status every 30 seconds  
✅ **Error Handling**: Detects incorrect codes and prompts retry  
✅ **Timeout Protection**: Stops waiting after timeout to prevent hanging  

## Important Notes

⚠️ **Headless Mode**: 
- OTP entry **requires** `headless=False`
- If you run in headless mode and OTP is required, you'll see a warning
- The scraper will fail gracefully with a helpful message

⚠️ **Timeout**:
- Default timeout is 300 seconds (5 minutes)
- You can modify this in the code if needed
- The scraper checks every 2 seconds for completion

⚠️ **Multiple Verification Methods**:
- Works with SMS codes
- Works with email codes  
- Works with authenticator app codes
- Works with backup codes

## Troubleshooting

### Problem: "OTP entry requires non-headless mode!"

**Solution**: Run with `headless=False`:
```bash
python instagram_scraper_business_indian.py skinkare 50 false
```

### Problem: Scraper times out waiting for OTP

**Solution**: 
- Make sure you're entering the code in the browser window
- Check that you clicked "Submit" after entering the code
- Increase timeout in code if needed (default is 300 seconds)

### Problem: "Verification code may be incorrect"

**Solution**:
- Double-check the code you entered
- Request a new code if needed
- Make sure you're entering it in the correct field

## Example Flow

```
🔐 Logging into Instagram...
✅ Username and password filled
🔐 Instagram requires verification (OTP/2FA)
   Please enter the verification code in the browser window
   Waiting for you to complete verification...

   ⏳ Waiting up to 300 seconds for OTP entry...
   [You enter code: 123456]
   ✅ Verification completed in 23 seconds!
✅ Successfully logged in after verification!
🔍 Searching for Indian business accounts...
```

## Code Location

The OTP handling functions are in `instagram_scraper_business_indian.py`:
- `check_for_otp_input()` - Detects OTP input fields
- `wait_for_otp_completion()` - Waits for manual OTP entry
