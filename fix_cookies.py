import json
import os

INPUT_PATH = "data/cookies.json"
OUTPUT_PATH = "data/cookies.json"

def fix_cookies():
    if not os.path.exists(INPUT_PATH):
        print("cookies.json not found.")
        return

    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        try:
            cookies = json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON in cookies.json")
            return

    # Check if it's a list of dicts (EditThisCookie format)
    if isinstance(cookies, list):
        print("Detected list of cookies. converting...")
        # Twikit load_cookies expects a dictionary where keys are cookie names and values are cookie values
        # OR it handles the list internally?
        # Let's look at the error: "too many values to unpack (expected 2)"
        # This usually happens if the library does `for k, v in cookies.items()` but `cookies` is a list.
        # So we should convert the list to a dictionary {name: value}
        
        cookie_dict = {}
        for cookie in cookies:
            if 'name' in cookie and 'value' in cookie:
                cookie_dict[cookie['name']] = cookie['value']
        
        # Save as dictionary
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(cookie_dict, f, indent=4)
        
        print(f"Converted {len(cookies)} cookies to dictionary format.")
    else:
        print("Cookies already in dictionary format or valid structure.")
        cookie_dict = cookies

    # Always generate and print Base64 if we have a dictionary
    if 'auth_token' in cookie_dict and 'ct0' in cookie_dict and 'twid' in cookie_dict:
        import base64
        # Save to ensure it's on disk in the correct format before encoding
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(cookie_dict, f, indent=4)
            
        with open(OUTPUT_PATH, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            print("\n" + "="*50)
            print("COPIE A STRING ABAIXO PARA O GITHUB SECRET 'COOKIES_JSON_BASE64':")
            print("="*50)
            print(encoded)
            print("="*50 + "\n")
    else:
        print("❌ Error: Missing auth_token or ct0 in cookies.")

if __name__ == "__main__":
    fix_cookies()
