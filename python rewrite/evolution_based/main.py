import parser
import human_readable_stat_names_and_indices as names_and_indices
import check_skill_points

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

MAX_SP_TO_INVEST = 200
MAX_SP_TO_ADD_WITH_TOMES = MAX_SP_TO_INVEST + 5
MAX_SP_TO_INVEST_PER_STAT = 100
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

def get_max_generations():
    if BENCHMARK:
        return 50  # small for quick benchmarks
    else:
        new_input = input('Give the max amount of generations to do (lower = faster): ')
        numerical_input = int(new_input.strip().lower())
        return numerical_input


def get_max_best_length():
    if BENCHMARK:
        return 50  # small for quick benchmarks
    else:
        new_input = input('Give the max amount of best results to give (lower = faster): ')
        numerical_input = int(new_input.strip().lower())
        return numerical_input


def skill_point_fast_check(skill_points: tuple[int, int, int, int, int]) -> bool:
    str_req = skill_points[0]
    dex_req = skill_points[1]
    int_req = skill_points[2]
    def_req = skill_points[3]
    agi_req = skill_points[4]
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


def combine_skill_point_requirements(build: list[tuple[str, np.ndarray]], skill_points_req_array_pos: tuple) -> tuple:
    str_req, dex_req, int_req, def_req, agi_req = 0, 0, 0, 0, 0
    for item in build:
        str_req = max([item[1][skill_points_req_array_pos[0]], str_req])
        dex_req = max([item[1][skill_points_req_array_pos[1]], dex_req])
        int_req = max([item[1][skill_points_req_array_pos[2]], int_req])
        def_req = max([item[1][skill_points_req_array_pos[3]], def_req])
        agi_req = max([item[1][skill_points_req_array_pos[4]], agi_req])
    return (str_req, dex_req, int_req, def_req, agi_req)


def combine_skill_points_added(build: list[tuple[str, np.ndarray]], skill_points_added_array_pos: tuple) -> tuple:
    str_added, dex_added, int_added, def_added, agi_added = 0, 0, 0, 0, 0
    for item in build:
        str_added += item[1][skill_points_added_array_pos[0]]
        dex_added += item[1][skill_points_added_array_pos[1]]
        int_added += item[1][skill_points_added_array_pos[2]]
        def_added += item[1][skill_points_added_array_pos[3]]
        agi_added += item[1][skill_points_added_array_pos[4]]
    return (str_added, dex_added, int_added, def_added, agi_added)






def precompute(items1: list[tuple[str, np.ndarray]], items2: list[tuple[str, np.ndarray]], skill_points_req_array_pos: tuple):
    combinations = itertools.product(items1, items2)
    for i, combination in enumerate(combinations):
        name_1, name_2 = combination[0][0], combination[1][0]
        combination_values_1, combination_values_2 = combination[0][1], combination[1][1]
        resulting_stats = np.add(combination_values_1, combination_values_2)
        resulting_name = f'{name_1}, {name_2}'
        
        if not skill_point_fast_check(combine_skill_point_requirements(build=[combination[0], combination[1]], skill_points_req_array_pos=skill_points_req_array_pos)):
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


def evaluate_builds(max_builds_list_length: int, stat_to_optimise: int, builds_to_evaluate: list[list[tuple[str, np.ndarray]]], skill_points_req_array_pos, added_skill_points_pos, min_optimised_stat_req) -> list[list[tuple[str, np.ndarray]]]:
    valid_builds = []
    valid_build_set = set()
    for build in builds_to_evaluate:
        combined_stats = combine_build_stats(build)
        if combined_stats[stat_to_optimise] < min_optimised_stat_req:
            continue
        skill_point_reqs = combine_skill_point_requirements(build, skill_points_req_array_pos)
        if not skill_point_fast_check(skill_point_reqs):
            continue
        if not check_skill_points.check_skillpoints(build):
            continue
        if not legal_item_combinations(build):
            continue
        if not f'{[item[0] for item in build]}' in valid_build_set:
            valid_build_set.add(f'{[item[0] for item in build]}')
            valid_builds.append(build)
    valid_builds = heapq.nlargest(max_builds_list_length, valid_builds, key=lambda build: combine_build_stats(build)[stat_to_optimise])
    return valid_builds






def evolution_steps(keep_per_step: int, steps_to_go: int, current_builds: list[list[tuple[str, np.ndarray]]], helmets: list[tuple[str, np.ndarray]], chestplates: list[tuple[str, np.ndarray]], leggings: list[tuple[str, np.ndarray]], boots: list[tuple[str, np.ndarray]], rings: list[tuple[str, np.ndarray]], bracelets: list[tuple[str, np.ndarray]], necklaces: list[tuple[str, np.ndarray]], weapons: list[tuple[str, np.ndarray]], stat_to_optimise: int, skill_point_array_pos: tuple, added_skill_points_pos, min_optimised_stat_req):
    print(f'Steps to go: {steps_to_go}')
    new_build_mutations = [build for current_build in current_builds for build in gen_new_build_mutations(current_build, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons) ]
    
    next_builds = evaluate_builds(keep_per_step, stat_to_optimise, new_build_mutations, skill_point_array_pos, added_skill_points_pos, min_optimised_stat_req)
    
    if steps_to_go >= 1:
        steps_to_go -= 1
        print(f'The next generation there wil be {len(next_builds)} builds.')
        return evolution_steps(keep_per_step, steps_to_go, next_builds, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, stat_to_optimise, skill_point_array_pos, added_skill_points_pos, min_optimised_stat_req)
    else:
        return next_builds









def main():
    items = parser.parse_items('data\\items.json')
    helmets, chestplates, leggings, boots, rings, bracelets, necklaces, spears, bows, daggers, wands, reliks = items
    weapons = spears + bows + daggers + wands + reliks
    weapons = [item for item in spears if item[0] == 'Guardian']

    skill_points_req_array_pos = (names_and_indices.STAT_INDICES['strength_requirement'], names_and_indices.STAT_INDICES['dexterity_requirement'], names_and_indices.STAT_INDICES['intelligence_requirement'], names_and_indices.STAT_INDICES['defense_requirement'], names_and_indices.STAT_INDICES['agility_requirement'])
    added_skill_points_pos = (names_and_indices.STAT_INDICES['strength'], names_and_indices.STAT_INDICES['dexterity'], names_and_indices.STAT_INDICES['intelligence'], names_and_indices.STAT_INDICES['defense'], names_and_indices.STAT_INDICES['agility'])
    
    stat_to_optimise = get_stat_to_optimise()
    generations = get_max_generations()
    max_best_length = get_max_best_length()


    starting_builds: list[list[tuple[str, np.ndarray]]] = []
    print('Generating starting builds...')
    while len(starting_builds) < max_best_length:
        starting_builds.extend(initialise_starting_builds(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, max_best_length*25))
        starting_builds = evaluate_builds(max_best_length, stat_to_optimise, starting_builds, skill_points_req_array_pos, added_skill_points_pos, min_optimised_stat_req)
        print(f'There currently have {len(starting_builds)} starting builds been generated.')
    starting_builds = starting_builds[:max_best_length]

    resulting_builds = evolution_steps(max_best_length, generations, starting_builds, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, stat_to_optimise, skill_points_req_array_pos, added_skill_points_pos, min_optimised_stat_req)





    for i, build in enumerate(resulting_builds):
        combined_stats = combine_build_stats(build)
        item_names = [item[0] for item in build]
        print(f'Build: {item_names}')
        #print(f'Stats: {combined_stats}')
        if i > 9:
            break





if __name__ == "__main__":
    main()
