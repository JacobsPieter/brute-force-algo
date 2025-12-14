import human_readable_stat_names_and_indices as stat_indices
from classes import *

import json
import csv

def get_skillpoints_data(data_file: str):
    with open(data_file, mode ='r') as file:    
        csvFile = list(csv.reader(file))
        return csvFile







def get_bad_data(file_path):
    with open(file_path, 'rb') as file:
        file.seek(1691308)
        problematic_bytes = file.read(200)
        print(f"Bytes at position 1691308: {problematic_bytes}")

def get_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data



def get_data_keys(item: dict, lookup=False) -> dict:
    if not lookup:
        valid_keys = [key for key in item.keys() if isinstance(item[key], (int, float))]
        return dict(zip(valid_keys, [int(item[key]) for key in valid_keys]))
    else:
        return dict(zip([key for key in item.keys() if key != 'name'], [value for (key, value) in item.items() if key != 'name']))


def make_numpy_arrays_stat_keys(category: dict[str, dict[str, int]]):
    all_keys = set()
    for stats in category.values():
        all_keys |= set(stats.keys())
    return all_keys




def get_items_and_sets(data_file):
    data = get_data(data_file)
    items: list[dict] = data['items']
    sets: dict[str, dict] = data['sets']
    return items, sets


def parse_items(data_file):
    items, sets = get_items_and_sets(data_file)
    helmets: list[Armour] = []
    chestplates: list[Armour] = []
    leggings: list[Armour] = []
    boots: list[Armour] = []
    rings: list[Accessory] = []
    bracelets: list[Accessory] = []
    necklaces: list[Accessory] = []
    spears: list[Weapon] = []
    bows: list[Weapon] = []
    daggers: list[Weapon] = []
    wands: list[Weapon] = []
    reliks: list[Weapon] = []
    for item in items:
        match item['type']:
            case 'helmet':
                helmets.append(Armour(item))
            case 'chestplate':
                chestplates.append(Armour(item))
            case 'leggings':
                leggings.append(Armour(item))
            case 'boots':
                boots.append(Armour(item))
            case 'ring':
                rings.append(Accessory(item))
            case 'bracelet':
                bracelets.append(Accessory(item))
            case 'necklace':
                necklaces.append(Accessory(item))
            case 'spear':
                spears.append(Weapon(item))
            case 'bow':
                bows.append(Weapon(item))
            case 'dagger':
                daggers.append(Weapon(item))
            case 'wand':
                wands.append(Weapon(item))
            case 'relik':
                reliks.append(Weapon(item))
            case _:
                print(f"Unknown item type: {item['type']}")
    return helmets, chestplates, leggings, boots, rings, bracelets, necklaces, spears, bows, daggers, wands, reliks





def parse_tomes(data_file):
    tomes = get_data(data_file)
    armour = []
    weapon = []
    marathon = []
    expertise = []
    mysticism = []
    lootrunning = []
    guild = []
    for tome in tomes["tomes"]:
        match tome['type']:
            case 'armour':
                armour.append(Tome(tome))
            case 'weapon':
                weapon.append(Tome(tome))
            case 'marathon':
                marathon.append(Tome(tome))
            case 'expertise':
                expertise.append(Tome(tome))
            case 'mysticism':
                mysticism.append(Tome(tome))
            case 'lootrun':
                lootrunning.append(Tome(tome))
            case 'guild':
                guild.append(Tome(tome))
            case _:
                print(f"Unknown tome type: {tome['type']}")
    return armour, weapon, marathon, expertise, mysticism, lootrunning, guild





if __name__ == "__main__":
    parse_items('data\\items.json')