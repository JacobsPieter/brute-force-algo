import requests, json

url = "https://api.wynncraft.com/v3/item/database?fullResult"
items = requests.get(url, timeout=30).json()

with open("wynn_items.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)
