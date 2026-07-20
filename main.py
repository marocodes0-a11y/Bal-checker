import os
import time
from bs4 import BeautifulSoup
import requests

USERNAME = "vaxuux"  # Your Donut SMP username
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")


def fetch_balance(username):
    url = f"https://donutsearch.xyz/player/{username}"
    proxy_url = f"https://api.allorigins.win/raw?url={url}"

    response = requests.get(proxy_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        raise Exception(f"Failed to fetch profile: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    money_label = None
    for el in soup.find_all(text=True):
        if el.strip() == "Money":
            money_label = el.parent
            break

    if not money_label:
        raise Exception("Money field not found")

    card = money_label
    while card and "rounded-2xl" not in card.get("class", []):
        card = card.parent

    precise = card.find("p", class_=lambda c: c and "font-mono" in c)
    if not precise:
        raise Exception("Balance element not found")

    return precise.text.strip()


def send_to_discord(username, balance):
    if not WEBHOOK_URL:
        print("[!] Missing Discord Webhook URL secret.")
        return
    payload = {
        "content": f"💰 **{username}**'s Donut SMP balance: **{balance}**"
    }
    res = requests.post(WEBHOOK_URL, json=payload)
    if res.status_code in (200, 204):
        print("[+] Sent successfully to Discord.")
    else:
        print(f"[!] Discord Error: {res.status_code}")


def main():
    try:
        balance = fetch_balance(USERNAME)
        print(f"[+] Balance for {USERNAME}: {balance}")
        send_to_discord(USERNAME, balance)
    except Exception as e:
        print(f"[!] Error: {e}")


if __name__ == "__main__":
    main()
