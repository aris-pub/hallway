"""
Post a Hallway Track edition to LinkedIn.

Setup (one-time):
    1. Create app at linkedin.com/developers
    2. Add "Share on LinkedIn" product
    3. Run: uv run --with httpx python agent/post_linkedin.py --auth
    4. Follow the browser flow, paste the redirect URL

Usage:
    uv run --with httpx python agent/post_linkedin.py 003 "Post text here"
"""

import argparse
import json
import os
import urllib.parse
import webbrowser
from pathlib import Path

import httpx

TOKEN_FILE = Path(__file__).parent.parent / ".linkedin-token.json"

REDIRECT_URI = "https://hallway.aris.pub/oauth/callback"


def do_auth():
    """One-time OAuth flow to get an access token."""
    client_id = os.environ.get("LINKEDIN_CLIENT_ID")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env")
        return

    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope=w_member_social%20openid%20profile"
        f"&state=hallwaytrack"
    )

    print("Opening browser for LinkedIn authorization...")
    webbrowser.open(auth_url)
    print()
    redirect_url = input("Paste the full redirect URL here: ").strip()

    parsed = urllib.parse.urlparse(redirect_url)
    params = urllib.parse.parse_qs(parsed.query)
    code = params.get("code", [None])[0]

    if not code:
        print("Error: No authorization code found in the URL")
        return

    resp = httpx.post("https://www.linkedin.com/oauth/v2/accessToken", data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
    })
    resp.raise_for_status()
    token_data = resp.json()

    # Get person URN
    me_resp = httpx.get("https://api.linkedin.com/v2/userinfo", headers={
        "Authorization": f"Bearer {token_data['access_token']}",
    })
    me_resp.raise_for_status()
    sub = me_resp.json()["sub"]

    token_data["person_urn"] = f"urn:li:person:{sub}"
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))
    print(f"Token saved to {TOKEN_FILE}")
    print(f"Expires in {token_data['expires_in'] // 86400} days")


def load_token() -> dict:
    """Load saved token."""
    if not TOKEN_FILE.exists():
        print("Error: No LinkedIn token found. Run with --auth first.")
        raise SystemExit(1)
    return json.loads(TOKEN_FILE.read_text())


def create_post(token_data: dict, text: str, url: str) -> dict:
    """Create a LinkedIn post with a link."""
    resp = httpx.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {token_data['access_token']}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        json={
            "author": token_data["person_urn"],
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "ARTICLE",
                    "media": [{
                        "status": "READY",
                        "originalUrl": url,
                    }],
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        },
    )
    resp.raise_for_status()
    return {"status": resp.status_code, "id": resp.headers.get("X-RestLi-Id", "")}


def main():
    parser = argparse.ArgumentParser(description="Post edition to LinkedIn")
    parser.add_argument("number", nargs="?", help="Edition number (e.g., 003)")
    parser.add_argument("text", nargs="?", help="Post text")
    parser.add_argument("--auth", action="store_true", help="Run one-time OAuth setup")
    args = parser.parse_args()

    if args.auth:
        do_auth()
        return

    if not args.number or not args.text:
        print("Usage: post_linkedin.py NUMBER TEXT")
        print("       post_linkedin.py --auth")
        return

    padded = args.number.zfill(3)
    url = f"https://hallway.aris.pub/no/{padded}/li/"

    token_data = load_token()
    print(f"Posting edition {padded} to LinkedIn...")
    result = create_post(token_data, args.text, url)
    print(f"Posted: {result}")


if __name__ == "__main__":
    main()
