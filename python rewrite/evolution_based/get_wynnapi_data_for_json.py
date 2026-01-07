import requests, json
import time



def get_items():
    url = "https://api.wynncraft.com/v3/item/database?fullResult"
    items = requests.get(url, timeout=30).json()
    with open("wynn_items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def get_at(character_class):
    url = f'https://api.wynncraft.com/v3/ability/tree/{character_class}'
    items = requests.get(url, timeout=30).json()
    with open(f'wynn_{character_class}_ability_tree.json', "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)



if __name__ == '__main__':
    for character_class in ['warrior', 'archer', 'mage', 'shaman', 'assassin']:
        get_at(character_class)
        time.sleep(2)