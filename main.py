"""
Donut SMP -> Discord balance poster
------------------------------------
Fetches your balance from donutsearch.xyz and posts it to a Discord
webhook every INTERVAL_SECONDS.

SETUP:
  1. pip install requests beautifulsoup4 playwright
     playwright install chromium      (only needed if the fast method fails)
  2. Fill in USERNAME and WEBHOOK_URL below.
  3. Run:  python donut_balance_bot.py
     Leave the terminal window open (or run it on a server/VPS to keep
     it running 24/7).
"""

import re
import time
import requests
from bs4 import BeautifulSoup

# ---------------- CONFIG ----------------
USERNAME = "namehere"          # <-- your Minecraft username
WEBHOOK_URL = "https://discord.com/api/webhooks/XXXX/XXXX"  # <-- your webhook
INTERVAL_SECONDS = 20
PROFILE_URL = f"https://donutsearch.xyz/player/{USERNAME}"
MENTION_ID = "1121808241974837308"  # <-- tagged when balance hasn't changed
# -----------------------------------------


def _extract_from_soup(soup):
    """Find the stat card labeled exactly 'Money' and return its precise
    (font-mono) figure, e.g. '$315,172,963'."""
    for label in soup.find_all(string=lambda s: s and s.strip() == "Money"):
        card = label.find_parent(
            "div", class_=re.compile(r"rounded-2xl")
        )
        if card is None:
            continue
        precise = card.find("p", class_=re.compile(r"font-mono"))
        if precise and precise.get_text(strip=True):
            return precise.get_text(strip=True)
    return None


def get_balance_fast():
    """Try to grab the balance straight from the raw HTML (no JS)."""
    resp = requests.get(
        PROFILE_URL,
        headers={"User-Agent": "Mozilla/5.0 (balance-bot)"},
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return _extract_from_soup(soup)


def get_balance_rendered():
    """Slower fallback: render the page with a real (headless) browser."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(PROFILE_URL, wait_until="networkidle")
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    return _extract_from_soup(soup)


def get_balance():
    try:
        balance = get_balance_fast()
        if balance:
            return balance
    except Exception as e:
        print(f"[fast method failed] {e}")

    print("Falling back to rendered (Playwright) fetch...")
    try:
        return get_balance_rendered()
    except Exception as e:
        print(f"[rendered method failed] {e}")
        return None


def send_to_discord(balance: str, unchanged: bool):
    mention = f" <@{MENTION_ID}>" if unchanged else ""
    note = " (unchanged since last check)" if unchanged else ""
    payload = {
        "content": f"💰 **{USERNAME}**'s Donut SMP balance: **{balance}**{note}{mention}"
    }
    r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    if r.status_code >= 300:
        print(f"[discord error] {r.status_code}: {r.text}")


def main():
    print(f"Watching balance for '{USERNAME}', posting every {INTERVAL_SECONDS}s...")
    last_balance = None
    while True:
        balance = get_balance()
        if balance:
            unchanged = balance == last_balance
            print(f"Balance found: {balance}" + (" (unchanged)" if unchanged else ""))
            send_to_discord(balance, unchanged)
            last_balance = balance
        else:
            print("Could not find balance on the page this round.")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
