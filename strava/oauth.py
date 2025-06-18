import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
REDIRECT_URI = "http://localhost"  # Or the one you set in Strava app settings

def get_authorization_url():
    base_url = "https://www.strava.com/oauth/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "activity:read_all",
        "approval_prompt": "force",
    }
    return f"{base_url}?{urlencode(params)}"

def exchange_code_for_tokens(code):
    response = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    })
    response.raise_for_status()
    return response.json()

def refresh_access_token():
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
        },
    )

    if not response.ok:
        print("Token refresh failed:", response.text)
        response.raise_for_status()

    return response.json()["access_token"]

def main():
    print("🔗 Visit this URL to authorize:")
    print(get_authorization_url())

    code = input("\nPaste the `code` from the redirect URL here: ").strip()
    tokens = exchange_code_for_tokens(code)

    print("\n✅ Access Token:", tokens['access_token'])
    print("🔁 Refresh Token:", tokens['refresh_token'])
    print("\n📌 Add this line to your `.env` file:")
    print(f"STRAVA_REFRESH_TOKEN={tokens['refresh_token']}")

if __name__ == "__main__":
    main()





