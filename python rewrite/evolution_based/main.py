import parser
import human_readable_stat_names_and_indices as names_and_indices

import itertools
import numpy as np
from numba import njit
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import heapq
import time
import random as rd
import math



BENCHMARK = True  # Set to False to use interactive input
SINGLE_THREADED = True  # Set to True to disable multiprocessing

MAX_SKILL_POINTS: int = 595
MAX_STRREQ: int = 320
MAX_DEXREQ: int = 317
MAX_INTREQ: int = 283
MAX_DEFREQ: int = 284
MAX_AGIREQ: int = 333

ORNATE_SHADOW_ITEMS = [
    'Ornate Shadow Cowl',
    'Ornate Shadow Garb',
    'Ornate Shadow Cover',
    'Ornate Shadow Cloud']
FIRE_HIVE_ITEMS = []
WATER_HIVE_ITEMS = []
EARTH_HIVE_ITEMS = []
THUNDER_HIVE_ITEMS = []
AIR_HIVE_ITEMS = []
MASTER_HIVE_ITEMS = []




min_optimised_stat_req = 0




def get_stat_to_optimise():
    if BENCHMARK:
        return names_and_indices.STAT_INDICES['hp']
    else:
        new_input = input('Give stat to optimize: ')
        new_input.strip().lower()
        return names_and_indices.STAT_INDICES[new_input]

def get_max_best_length():
    if BENCHMARK:
        return 10  # small for quick benchmarks
    else:
        new_input = input('Give the max amount of best results to give (lower = faster): ')
        numerical_input = int(new_input.strip().lower())
        return numerical_input

@njit
def skill_point_fast_check(stats: np.ndarray, required_stats: tuple[int, int, int, int, int]) -> bool:
    str_req = stats[required_stats[0]]
    dex_req = stats[required_stats[1]]
    int_req = stats[required_stats[2]]
    def_req = stats[required_stats[3]]
    agi_req = stats[required_stats[4]]
    if str_req + dex_req + int_req + def_req + agi_req > MAX_SKILL_POINTS:
        return False
    if str_req > MAX_STRREQ:
        return False
    if dex_req > MAX_DEXREQ:
        return False
    if int_req > MAX_INTREQ:
        return False
    if def_req > MAX_DEFREQ:
        return False
    if agi_req > MAX_AGIREQ:
        return False
    return True

@njit
def skill_point_check(stats: np.ndarray, required_stats: tuple[int, int, int, int, int], extra_stats: tuple[int, int, int, int, int], weapon_stats) -> bool:
    str_req = stats[required_stats[0]]
    dex_req = stats[required_stats[1]]
    int_req = stats[required_stats[2]]
    def_req = stats[required_stats[3]]
    agi_req = stats[required_stats[4]]
    added_str = stats[extra_stats[0]] - weapon_stats[extra_stats[0]]
    added_dex = stats[extra_stats[1]] - weapon_stats[extra_stats[1]]
    added_int = stats[extra_stats[2]] - weapon_stats[extra_stats[2]]
    added_def = stats[extra_stats[3]] - weapon_stats[extra_stats[3]]
    added_agi = stats[extra_stats[4]] - weapon_stats[extra_stats[4]]
    if str_req > added_str + 100:
        return False
    if dex_req > added_dex + 100:
        return False
    if int_req > added_int + 100:
        return False
    if def_req > added_def + 100:
        return False
    if agi_req > added_agi + 100:
        return False
    str_req_left = str_req - added_str
    dex_req_left = dex_req - added_dex
    int_req_left = int_req - added_int
    def_req_left = def_req - added_def
    agi_req_left = agi_req - added_agi
    
    return True


def legal_item_combinations(build: list[tuple[str, np.ndarray]]) -> bool:
    ornate_shadow = False
    master_hive = False
    fire_hive = False
    water_hive = False
    earth_hive = False
    thunder_hive = False
    air_hive = False
    for item in build:
        if item[0] in ORNATE_SHADOW_ITEMS:
            if ornate_shadow:
                return False
            ornate_shadow = True
        elif item[0] in MASTER_HIVE_ITEMS:
            if master_hive:
                return False
            master_hive = True
        elif item[0] in FIRE_HIVE_ITEMS:
            if fire_hive:
                return False
            fire_hive = True
        elif item[0] in WATER_HIVE_ITEMS:
            if water_hive:
                return False
            water_hive = True
        elif item[0] in EARTH_HIVE_ITEMS:
            if earth_hive:
                return False
            earth_hive = True
        elif item[0] in THUNDER_HIVE_ITEMS:
            if thunder_hive:
                return False
            thunder_hive = True
        elif item[0] in AIR_HIVE_ITEMS:
            if air_hive:
                return False
            air_hive = True
    return True






@njit
def combine(combo1: tuple[str, np.ndarray], combo2: tuple[str, np.ndarray]):
    combo1_values = combo1[1]
    combo2_values = combo2[1]
    resulting_stats = np.add(combo1_values, combo2_values)
    return resulting_stats

@njit
def combine_build_stats(build1: list[tuple[str, np.ndarray]]) -> np.ndarray:
    combined_stats = np.zeros_like(build1[0][1])
    for item in build1:
        combined_stats = np.add(combined_stats, item[1])
    return combined_stats




def precompute(items1: list[tuple[str, np.ndarray]], items2: list[tuple[str, np.ndarray]], skill_points_req_array_pos: tuple):
    combinations = itertools.product(items1, items2)
    for i, combination in enumerate(combinations):
        name_1, name_2 = combination[0][0], combination[1][0]
        combination_values_1, combination_values_2 = combination[0][1], combination[1][1]
        resulting_stats = np.add(combination_values_1, combination_values_2)
        resulting_name = f'{name_1}, {name_2}'
        if not skill_point_fast_check(resulting_stats, skill_points_req_array_pos):
            continue
        yield (resulting_name, resulting_stats)



def dict_from_map_object(to_convert) -> dict[str, dict[str, int]]:
    converted = {}
    for dictionary in to_convert:
        converted.update(dictionary)
    return converted


def initialise_starting_builds(helmets: list[tuple[str, np.ndarray]], chestplates: list[tuple[str, np.ndarray]], leggings: list[tuple[str, np.ndarray]], boots: list[tuple[str, np.ndarray]], rings: list[tuple[str, np.ndarray]], bracelets: list[tuple[str, np.ndarray]], necklaces: list[tuple[str, np.ndarray]], weapons: list[tuple[str, np.ndarray]], keep_per_step: int):
    starting_builds = []
    
    def initialise_build(helmets: list[tuple[str, np.ndarray]], chestplates: list[tuple[str, np.ndarray]], leggings: list[tuple[str, np.ndarray]], boots: list[tuple[str, np.ndarray]], rings: list[tuple[str, np.ndarray]], bracelets: list[tuple[str, np.ndarray]], necklaces: list[tuple[str, np.ndarray]], weapons: list[tuple[str, np.ndarray]], step: int):
        helmet = helmets[rd.randint(0, len(helmets) - 1)]
        chestplate = chestplates[rd.randint(0, len(chestplates) - 1)]
        legging = leggings[rd.randint(0, len(leggings) - 1)]
        boot = boots[rd.randint(0, len(boots) - 1)]
        ring1 = rings[rd.randint(0, len(rings) - 1)]
        ring2 = rings[rd.randint(0, len(rings) - 1)]
        bracelet = bracelets[rd.randint(0, len(bracelets) - 1)]
        necklace = necklaces[rd.randint(0, len(necklaces) - 1)]
        weapon = weapons[rd.randint(0, len(weapons) - 1)]
        starting_build = [helmet, chestplate, legging, boot, ring1, ring2, bracelet, necklace, weapon]
        return starting_build
    
    starting_builds = [initialise_build(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, 0) for _ in range(keep_per_step)]
    return starting_builds


def gen_new_build_mutations(existing_build: list[tuple[str, np.ndarray]], helmets: list[tuple[str, np.ndarray]], chestplates: list[tuple[str, np.ndarray]], leggings: list[tuple[str, np.ndarray]], boots: list[tuple[str, np.ndarray]], rings: list[tuple[str, np.ndarray]], bracelets: list[tuple[str, np.ndarray]], necklaces: list[tuple[str, np.ndarray]], weapons: list[tuple[str, np.ndarray]]):
    helmet_changed = existing_build.copy()
    helmet_changed[0] = helmets[rd.randint(0, len(helmets) - 1)]
    chestplate_changed = existing_build.copy()
    chestplate_changed[1] = chestplates[rd.randint(0, len(chestplates) - 1)]
    legging_changed = existing_build.copy()
    legging_changed[2] = leggings[rd.randint(0, len(leggings) - 1)]
    boot_changed = existing_build.copy()
    boot_changed[3] = boots[rd.randint(0, len(boots) - 1)]
    ring1_changed = existing_build.copy()
    ring1_changed[4] = rings[rd.randint(0, len(rings) - 1)]
    ring2_changed = existing_build.copy()
    ring2_changed[5] = rings[rd.randint(0, len(rings) - 1)]
    bracelet_changed = existing_build.copy()
    bracelet_changed[6] = bracelets[rd.randint(0, len(bracelets) - 1)]
    necklace_changed = existing_build.copy()
    necklace_changed[7] = necklaces[rd.randint(0, len(necklaces) - 1)]
    weapon_changed = existing_build.copy()
    weapon_changed[8] = weapons[rd.randint(0, len(weapons) - 1)]
    return [helmet_changed, chestplate_changed, legging_changed, boot_changed, ring1_changed, ring2_changed, bracelet_changed, necklace_changed, weapon_changed, existing_build]


def evaluate_builds(max_builds_list_length: int, stat_to_optimise: int, builds_to_evaluate: list[list[tuple[str, np.ndarray]]], skill_points_req_array_pos, min_optimised_stat_req) -> list[list[tuple[str, np.ndarray]]]:
    valid_builds = []
    valid_build_set = set()
    for build in builds_to_evaluate:
        combined_stats = combine_build_stats(build)
        if combined_stats[stat_to_optimise] < min_optimised_stat_req:
            continue
        if not skill_point_fast_check(combined_stats, skill_points_req_array_pos):
            continue
        weapon_stats = build[8][1]
        if not skill_point_check(combined_stats, skill_points_req_array_pos, (names_and_indices.STAT_INDICES['strength'], names_and_indices.STAT_INDICES['dexterity'], names_and_indices.STAT_INDICES['intelligence'], names_and_indices.STAT_INDICES['defense'], names_and_indices.STAT_INDICES['agility']), weapon_stats):
            continue
        if not legal_item_combinations(build):
            continue
        if not f'{[item[0] for item in build]}' in valid_build_set:
            valid_build_set.add(f'{[item[0] for item in build]}')
            valid_builds.append(build)
    valid_builds = heapq.nlargest(max_builds_list_length, valid_builds, key=lambda build: combine_build_stats(build)[stat_to_optimise])
    return valid_builds






def evolution_steps(keep_per_step: int, steps_to_go: int, current_builds: list[list[tuple[str, np.ndarray]]], helmets: list[tuple[str, np.ndarray]], chestplates: list[tuple[str, np.ndarray]], leggings: list[tuple[str, np.ndarray]], boots: list[tuple[str, np.ndarray]], rings: list[tuple[str, np.ndarray]], bracelets: list[tuple[str, np.ndarray]], necklaces: list[tuple[str, np.ndarray]], weapons: list[tuple[str, np.ndarray]], stat_to_optimise: int, skill_point_array_pos: tuple, min_optimised_stat_req):
    print(f'Steps to go: {steps_to_go}')
    new_build_mutations = [build for current_build in current_builds for build in gen_new_build_mutations(current_build, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons) ]
    
    next_builds = evaluate_builds(keep_per_step, stat_to_optimise, new_build_mutations, skill_point_array_pos, min_optimised_stat_req)
    
    if steps_to_go >= 1:
        steps_to_go -= 1
        print(f'The next generation there wil be: {len(next_builds)} builds.')
        return evolution_steps(keep_per_step, steps_to_go, next_builds, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, stat_to_optimise, skill_point_array_pos, min_optimised_stat_req)
    else:
        return next_builds









def main():
    items = parser.parse_items('data\\items.json')
    helmets, chestplates, leggings, boots, rings, bracelets, necklaces, spears, bows, daggers, wands, reliks = items
    weapons = spears + bows + daggers + wands + reliks
    weapons = [item for item in spears if item[0] == 'Guardian']

    resulting_builds = evolution_steps(keep_per_step=100, steps_to_go=50, current_builds=initialise_starting_builds(
        helmets=helmets,
        chestplates=chestplates,
        leggings=leggings,
        boots=boots,
        rings=rings,
        bracelets=bracelets,
        necklaces=necklaces,
        weapons=weapons,
        keep_per_step=1000
    ), helmets=helmets,
        chestplates=chestplates,
        leggings=leggings,
        boots=boots,
        rings=rings,
        bracelets=bracelets,
        necklaces=necklaces,
        weapons=weapons,
        stat_to_optimise=get_stat_to_optimise(),
        skill_point_array_pos=(
            names_and_indices.STAT_INDICES['strength_requirement'],
            names_and_indices.STAT_INDICES['dexterity_requirement'],
            names_and_indices.STAT_INDICES['intelligence_requirement'],
            names_and_indices.STAT_INDICES['defense_requirement'],
            names_and_indices.STAT_INDICES['agility_requirement'],
        ),
        min_optimised_stat_req=min_optimised_stat_req
    )





    for i, build in enumerate(resulting_builds):
        combined_stats = combine_build_stats(build)
        item_names = [item[0] for item in build]
        print(f'Build: {item_names}')
        print(f'Stats: {combined_stats}')
        if i > 9:
            break





if __name__ == "__main__":
    main()
