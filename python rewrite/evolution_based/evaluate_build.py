import check_skill_points
import human_readable_stat_names_and_indices as stat_indices

from numba import njit
import numpy as np
import heapq



ORNATE_SHADOW_ITEMS = {
    'Ornate Shadow Cowl',
    'Ornate Shadow Garb',
    'Ornate Shadow Cover',
    'Ornate Shadow Cloud'}
FIRE_HIVE_ITEMS = {
    "Sparkweaver",
    "Soulflare",
    "Cinderchain",
    "Mantlewalkers",
    "Clockwork",
    "Dupliblaze"}
WATER_HIVE_ITEMS = {
    "Whitecap Crown",
    "Stillwater Blue",
    "Trench Scourer",
    "Silt of the Seafloor",
    "Coral Ring",
    "Moon Pool Circlet"}
EARTH_HIVE_ITEMS = {
    "Ambertoise Shell",
    "Beetle Aegis",
    "Elder Oak Roots",
    "Humbark Moccasins",
    "Subur Clip",
    "Golemlus Core"}
THUNDER_HIVE_ITEMS = {
    "Sparkling Visor",
    "Insulated Plate Mail",
    "Static-Charged Leggings",
    "Thunderous Step",
    "Bottled Thunderstorm",
    "Lightning Flash"}
AIR_HIVE_ITEMS = {
    "Pride of the Aerie",
    "Gale's Freedom",
    "Turbine Greaves",
    "Flashstep",
    "Breezehands",
    "Vortex Bracer"}
MASTER_HIVE_ITEMS = {
    "Abyss-Imbued Leggings",
    "Boreal-Patterned Crown",
    "Anima-Infused Cuirass",
    "Chaos-Woven Greaves",
    "Elysium-Engraved Aegis",
    "Eden-Blessed Guards",
    "Gaea-Hewn Boots",
    "Hephaestus-Forged Sabatons",
    "Obsidian-Framed Helmet",
    "Twilight-Gilded Cloak",
    "Infused Hive Relik",
    "Infused Hive Wand",
    "Infused Hive Spear",
    "Infused Hive Dagger",
    "Infused Hive Bow",
    "Contrast",
    "Prowess",
    "Intensity"}
GROOKWARTS = {
    "Dragon's Eye Bracelet",
    "Draoi Fair",
    "Renda Langit"}


MAX_SP_TO_INVEST = 200
MAX_SP_TO_ADD_WITH_TOMES = MAX_SP_TO_INVEST + 5
MAX_SP_TO_INVEST_PER_STAT = 100
MAX_SKILL_POINTS: int = 595
MAX_STRREQ: int = 320
MAX_DEXREQ: int = 317
MAX_INTREQ: int = 283
MAX_DEFREQ: int = 284
MAX_AGIREQ: int = 333


LARGE_NEG = -1000000000000
LARGE_POS = 1000000000000





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
    grookwarts = False
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
        elif item[0] in GROOKWARTS:
            if grookwarts:
                return False
            air_hive = True
    return True


def calculate_fitness_wrapper(build, config):
    stat_stuff = config["required_stats"]
    required_stats_names = stat_stuff["required_stats_names"]
    required_stats_minimums: dict = stat_stuff["required_stats_minimums"]
    required_stats_maximums: dict = stat_stuff["required_stats_maximums"]
    required_stats_weights: dict = stat_stuff["required_stats_weights"]
    required_stats_minimums_list = [required_stats_minimums.get(stat,LARGE_NEG) for stat in required_stats_names]
    required_stats_maximums_list = [required_stats_maximums.get(stat,LARGE_POS) for stat in required_stats_names]
    required_stats_weights_list = [required_stats_weights[stat] for stat in required_stats_names]
    pos_in_build_stats = stat_indices.get_stats_pos_list(required_stats_names)
    fitness = calculate_fitness(build, required_stats_names, required_stats_minimums_list, required_stats_maximums_list, required_stats_weights_list, pos_in_build_stats)
    return fitness  




def calculate_fitness(build, required_stats_names: list[str], required_stats_minimums: list[float], required_stats_maximums: list[float], required_stats_weights: list[int], pos_in_build_stats: list[int]) -> float:
    make_value_zero_no_more: float = 0.01
    build_stats = combine_build_stats(build)
    fitness: float = 0
    new_minimums = required_stats_minimums
    new_maximums = required_stats_maximums
    for i, minimum in enumerate(required_stats_minimums):
        if minimum == 0:
            minimum += make_value_zero_no_more
            new_minimums[i] = minimum
    for i, maximum in enumerate(required_stats_maximums):
        if maximum == 0:
            maximum += make_value_zero_no_more
            new_maximums[i] = maximum

    total_weigth = sum(required_stats_weights)
    if total_weigth == 0:
        return 0
    stats_fitnesses: list[float] = []
    for stat, stat_name in enumerate(required_stats_names):

        stat_fitness: float = 0
        value = build_stats[pos_in_build_stats[stat]]
        
        weight: float = required_stats_weights[stat]
        minimum: float = required_stats_minimums[stat]
        maximum: float = required_stats_maximums[stat]

        if value < 0.1 or value > -0.1:
            value = value + make_value_zero_no_more

        if minimum > LARGE_NEG and maximum < LARGE_POS:
            if minimum > maximum:
                continue
            if minimum <= value and value <= maximum:
                stat_fitness = 1
            elif value > maximum:
                stat_fitness = maximum / value
            elif value < minimum:
                stat_fitness = value / minimum
            stats_fitnesses.append(stat_fitness * weight / total_weigth)
            continue
        if maximum < LARGE_POS and minimum <= LARGE_NEG:
            stat_fitness = maximum / value
            stats_fitnesses.append(stat_fitness * weight / total_weigth)
            continue
        if minimum > LARGE_NEG and maximum >= LARGE_POS:
            stat_fitness = value / minimum
            stats_fitnesses.append(stat_fitness * weight / total_weigth)
            continue
        if minimum <= LARGE_NEG and maximum >= LARGE_POS:
            stats_fitnesses.append(value * weight / total_weigth)
            continue
    
    fitness = sum(stats_fitnesses)
    return fitness







def evaluate_builds(max_builds_list_length: int, stat_to_optimise: int, builds_to_evaluate: list[list[tuple[str, np.ndarray]]], skill_points_req_array_pos, min_optimised_stat_req, config) -> list[list[tuple[str, np.ndarray]]]:
    valid_builds = []
    valid_build_set = set()
    skill_indices = [stat_indices.get_stat_pos('strength'),
                     stat_indices.get_stat_pos('dexterity'),
                     stat_indices.get_stat_pos('intelligence'),
                     stat_indices.get_stat_pos('defense'),
                     stat_indices.get_stat_pos('agility')]
    req_indices = [stat_indices.get_stat_pos('strength_requirement'),
                   stat_indices.get_stat_pos('dexterity_requirement'),
                   stat_indices.get_stat_pos('intelligence_requirement'),
                   stat_indices.get_stat_pos('defense_requirement'),
                   stat_indices.get_stat_pos('agility_requirement')]
    for build in builds_to_evaluate:
        combined_stats = combine_build_stats(build)
        skill_point_reqs = combine_skill_point_requirements(build, skill_points_req_array_pos)
        if not check_skill_points.check_skillpoints(build):
            continue
        if not legal_item_combinations(build):
            continue
        fitness = calculate_fitness_wrapper(build, config)
        if not f'{[item[0] for item in build]}' in valid_build_set:
            valid_build_set.add(f'{[item[0] for item in build]}')
            valid_builds.append((build, fitness))
    valid_builds = heapq.nlargest(max_builds_list_length, valid_builds, key=lambda build: build[1])
    valid_builds = [build[0] for build in valid_builds]
    return valid_builds



