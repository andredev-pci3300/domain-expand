import json

def strict_clean():
    try:
        with open('data/cookies.json', 'r') as f:
            cookies = json.load(f)
        
        new_cookies = {}
        target_keys = ['auth_token', 'ct0', 'twid']
        
        if isinstance(cookies, list):
             for c in cookies:
                if c['name'] in target_keys:
                    new_cookies[c['name']] = c['value']
        elif isinstance(cookies, dict):
             for k, v in cookies.items():
                if k in target_keys:
                    new_cookies[k] = v
                    
        # Verify valid structure
        if not new_cookies.get('auth_token') or not new_cookies.get('ct0'):
            print("WARNING: Missing auth_token or ct0 in cookies.json!")
        else:
            print("Found valid auth_token and ct0.")
            
        with open('data/cookies.json', 'w') as f:
            json.dump(new_cookies, f, indent=4)
        print("Cookies strictly cleaned.")
        
    except Exception as e:
        print(f"Error cleaning cookies: {e}")

if __name__ == "__main__":
    strict_clean()
