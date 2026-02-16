"""
Convert cookies from browser string format to Playwright JSON format
"""

import json
import re
from datetime import datetime, timedelta


def convert_cookie_string_to_json(cookie_string: str, domain: str = ".instagram.com") -> list:
    """
    Convert cookie string (from browser) to Playwright JSON format
    
    Example input:
    "sessionid=abc123; csrftoken=xyz789; domain=.instagram.com"
    
    Example output:
    [
      {"name": "sessionid", "value": "abc123", "domain": ".instagram.com", ...},
      {"name": "csrftoken", "value": "xyz789", "domain": ".instagram.com", ...}
    ]
    """
    cookies = []
    
    # Split by semicolon
    cookie_pairs = cookie_string.split(';')
    
    for pair in cookie_pairs:
        pair = pair.strip()
        if not pair:
            continue
        
        # Split name and value
        if '=' in pair:
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
                "expires": int((datetime.now() + timedelta(days=30)).timestamp()),  # 30 days from now
                "httpOnly": name.lower() in ["sessionid", "csrftoken"],
                "secure": True,
                "sameSite": "None" if name.lower() == "sessionid" else "Lax"
            }
            
            cookies.append(cookie)
    
    return cookies


def convert_file(input_file: str, output_file: str = None):
    """Convert cookie file from string format to JSON format"""
    if output_file is None:
        output_file = input_file.replace('.json', '_converted.json')
        if output_file == input_file:
            output_file = input_file.replace('.txt', '_converted.json')
    
    try:
        # Read cookie string
        with open(input_file, 'r', encoding='utf-8') as f:
            cookie_string = f.read().strip()
        
        # Convert to JSON format
        cookies = convert_cookie_string_to_json(cookie_string)
        
        # Save as JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Converted {len(cookies)} cookies")
        print(f"💾 Saved to: {output_file}")
        print(f"\n📋 Cookies found:")
        for cookie in cookies:
            print(f"   - {cookie['name']}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error converting cookies: {str(e)}")
        return None


if __name__ == "__main__":
    import sys
    
    input_file = "instagram_cookies.json"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    output_file = None
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print("="*60)
    print("Cookie Format Converter")
    print("="*60)
    print(f"\nConverting: {input_file}\n")
    
    result = convert_file(input_file, output_file)
    
    if result:
        print(f"\n✅ Conversion complete!")
        print(f"💡 Use the converted file: {result}")
        print(f"💡 Or update instagram_scraper_business_indian.py to auto-convert")
