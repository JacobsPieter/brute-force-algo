import sort
import filtering
import numpy as np
from numba import njit


#test data for different item types
helmets = {
    'Iron Helmet': {'defense': 5, 'weight': 10, 'durability': 50},
    'Steel Helmet': {'defense': 8, 'weight': 12, 'durability': 70},
    'Golden Helmet': {'defense': 6, 'weight': 9, 'magic_resistance': 5},
    'Diamond Helmet': {'defense': 12, 'weight': 15, 'durability': 100},
}
armors = {
    'Leather Armor': {'defense': 15, 'weight': 25, 'agility': 5},
    'Chainmail Armor': {'defense': 25, 'weight': 40, 'knockback_resistance': 5},
    'Plate Armor': {'defense': 40, 'weight': 60, 'strength': 10},
}
leggings = {
    'Cloth Leggings': {'defense': 3, 'weight': 5, 'flexibility': 7},
    'Leather Leggings': {'defense': 7, 'weight': 15, 'agility': 4},
    'Iron Leggings': {'defense': 12, 'weight': 30, 'durability': 40},
}
boots = {
    'Cloth Boots': {'defense': 2, 'weight': 4, 'speed': 5},
    'Leather Boots': {'defense': 5, 'weight': 10, 'agility': 3},
    'Iron Boots': {'defense': 10, 'weight': 20, 'durability': 30},
}
rings = {
    'Silver Ring': {'magic': 5, 'weight': 1, 'mana_regeneration': 2},
    'Gold Ring': {'magic': 10, 'weight': 2, 'mana_regeneration': 5},
    'Platinum Ring': {'magic': 15, 'weight': 3, 'main_attack_boost': 3},
}
bracelets = {
    'Silver Bracelet': {'magic': 3, 'weight': 1, 'durability': 5},
    'Gold Bracelet': {'magic': 7, 'weight': 2, 'strength': 4},
    'Platinum Bracelet': {'magic': 12, 'weight': 3, 'defense': 6},
}
necklaces = {
    'Silver Necklace': {'magic': 4, 'weight': 1, 'health_regeneration': 3},
    'Gold Necklace': {'magic': 9, 'weight': 2, 'health_boost': 5},
    'Platinum Necklace': {'magic': 14, 'weight': 3, 'resistance': 4},
}

def get_stat_to_optimize() -> str:
    stat = input('Enter the stat to optimize: ').strip().lower()
    return stat

def get_required_stats(stat_to_optimise: str) -> list[str]:
    stats_input = input('Enter the required stats (comma-separated): ').strip().lower()
    if stats_input == '':
        return [stat_to_optimise]
    required_stats = [stat.strip() for stat in stats_input.split(',')]
    required_stats.append(stat_to_optimise)
    return required_stats


def combine_stats(item_1: dict[str, int], item_2: dict[str, int]) -> dict[str, int]:
    combined: dict[str, int] = {}
    for stat in set(item_1.keys()).union(item_2.keys()):
        combined[stat] = item_1.get(stat, 0) + item_2.get(stat, 0)
    return combined


def get_stats_for_item_groups(items_type_1: dict[str, dict[str, int]], items_type_2: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    combinations: dict[str, dict[str, int]] = {}
    for item_type_1 in items_type_1:
        for item_type_2 in items_type_2:
            combination: dict[str, int] = combine_stats(items_type_1[item_type_1], items_type_2[item_type_2])
            combinations[f'{item_type_1} + {item_type_2}'] = combination
    return combinations


def get_all_combinations() -> dict[str, dict[str, int]]:
    top_parts = get_stats_for_item_groups(helmets, armors)
    bottom_parts = get_stats_for_item_groups(leggings, boots)
    rings_combinations = get_stats_for_item_groups(rings, rings)
    big_jewels = get_stats_for_item_groups(bracelets, necklaces)
    jewelry_combinations = get_stats_for_item_groups(rings_combinations, big_jewels)
    protections = get_stats_for_item_groups(top_parts, bottom_parts)
    all_combinations = get_stats_for_item_groups(protections, jewelry_combinations)
    return all_combinations



def sort_combinations_by_stat(combinations: dict[str, dict[str, int]], stat: str) -> list[str]:
    stat_values: dict[str, int] = {}
    for combo_name, stats in combinations.items():
        stat_values[combo_name] = stats.get(stat, 0)
    sorted_combinations = sort.sort_dict(stat_values)
    return sorted_combinations[0]


def main():
    stat_to_optimize = get_stat_to_optimize()
    required_stats = get_required_stats(stat_to_optimize)
    all_combinations = get_all_combinations()
    filtered_combinations = filtering.filter(all_combinations, required_stats)
    sorted_names = sort_combinations_by_stat(filtered_combinations, stat_to_optimize)
    for name in sorted_names:
        stats = filtered_combinations[name]
        print(f'{name}: {stats}')



if __name__ == '__main__':
    main()