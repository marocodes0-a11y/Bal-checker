from bs4 import BeautifulSoup
import requests
import time

# --- CONFIGURATION ---
USERNAME = "vaxuux"  # Replace with your Donut SMP username
WEBHOOK_URL = (
    "https://discord.com/api/webhooks/1528581249474498590/3VGIVESBGyQOx_Xi3kP1gd8csl7WekC0tdDiEViFLr__nhZOLmutiHcSkWMUic7c1Czu"  # Replace with your Discord Webhook URL
)
CHECK_INTERVAL = 20  # Check every 20 seconds


def fetch_balance(username):
    url = f"https://donutsearch.xyz/player/{username}"
    # Using AllOrigins proxy to mirror the browser logic
    proxy_url = f"https://api.allorigins.win/raw?url={url}"

    response = requests.get(proxy_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        raise Exception(f"Failed to fetch profile: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the Money label
    money_label = None
    for el in soup.find_all(text=True):
        if el.strip() == "Money":
            money_label = el.parent
            break

    if not money_label:
        raise Exception("Money field not found")

    # Navigate up to the card container
    card = money_label
    while card and "rounded-2xl" not in card.get("class", []):
        card = card.parent

    # Extract the balance string
    precise = card.find("p", class_=lambda c: c and "font-mono" in c)
    if not precise:
        raise Exception("Balance element not found")

    return precise.text.strip()


def send_to_discord(username, balance):
    payload = {
        "content": f"💰 **{username}**'s Donut SMP balance: **{balance}**"
    }
    res = requests.post(WEBHOOK_URL, json=payload)
    if res.status_code not in (200, 204):
        print(f"[!] Discord Error: {res.status_code}")


def main():
    print(f"[*] Starting 24/7 Donut SMP Watcher for {USERNAME}...")
    while True:
        try:
            balance = fetch_balance(USERNAME)
            print(f"[+] Balance: {balance}")
            send_to_discord(USERNAME, balance)
        except Exception as e:
            print(f"[!] Error: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
  
