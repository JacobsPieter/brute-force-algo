import parser
import human_readable_stat_names_and_indices as stat_indices
import encoder
import evaluate_build as evaluate
import progressbar



import numpy as np
from numba import njit
import random as rd
import json



BENCHMARK = True  # Set to False to use interactive input
SINGLE_THREADED = True  # Set to True to disable multiprocessing

with open('python rewrite\\evolution_based\\config.json', 'r') as config_file:
    config = json.load(config_file)




min_optimised_stat_req = 0




def get_stat_to_optimise():
    if BENCHMARK:
        return stat_indices.get_stat_pos('hp')
    else:
        new_input = input('Give stat to optimize: ')
        new_input.strip().lower()
        return stat_indices.get_stat_pos(new_input)

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









def combine(combo1: tuple[str, np.ndarray], combo2: tuple[str, np.ndarray]):
    combo1_values = combo1[1]
    combo2_values = combo2[1]
    resulting_stats = np.add(combo1_values, combo2_values)
    return resulting_stats







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



def evolution_steps(keep_per_step: int, current_builds: list[list[tuple[str, np.ndarray]]], helmets: list[tuple[str, np.ndarray]], chestplates: list[tuple[str, np.ndarray]], leggings: list[tuple[str, np.ndarray]], boots: list[tuple[str, np.ndarray]], rings: list[tuple[str, np.ndarray]], bracelets: list[tuple[str, np.ndarray]], necklaces: list[tuple[str, np.ndarray]], weapons: list[tuple[str, np.ndarray]], stat_to_optimise: int, skill_point_array_pos: tuple, added_skill_points_pos, min_optimised_stat_req):
    new_build_mutations = [build for current_build in current_builds for build in gen_new_build_mutations(current_build, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons) ]
    
    next_builds = evaluate.evaluate_builds(keep_per_step, stat_to_optimise, new_build_mutations, skill_point_array_pos, min_optimised_stat_req, config)
    
    return next_builds









def main():
    items= parser.parse_items('data\\items.json')

    helmets, chestplates, leggings, boots, rings, bracelets, necklaces, spears, bows, daggers, wands, reliks = items
    weapons = spears
    weapons.extend(bows)
    weapons.extend(daggers)
    weapons.extend(wands)
    weapons.extend(reliks)



    weapons = [item for item in weapons if item[0] == "Divzer"]

    sp_requirements_list = ['strength_requirement', 'dexterity_requirement', 'intelligence_requirement', 'defense_requirement', 'agility_requirement']
    sp_adding_list = ['strength', 'dexterity', 'intelligence', 'defense', 'agility']

    skill_points_req_array_pos = tuple(stat_indices.get_stats_pos_list(sp_requirements_list))
    added_skill_points_pos = tuple(stat_indices.get_stats_pos_list(sp_adding_list))
    
    stat_to_optimise = get_stat_to_optimise()
    generations = config["algorithm"]["generations"]
    max_best_length = config["algorithm"]["subjects"]
    return_amount = config["return_length"]
    

    starting_builds: list[list[tuple[str, np.ndarray]]] = []
    progressbar.printProgressBar(0, max_best_length, prefix='Generating starting builds: ', suffix='Complete')
    while len(starting_builds) < max_best_length:
        starting_builds.extend(initialise_starting_builds(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, 10))
        starting_builds = evaluate.evaluate_builds(max_best_length, stat_to_optimise, starting_builds, skill_points_req_array_pos, min_optimised_stat_req, config)
        progressbar.printProgressBar(len(starting_builds), max_best_length, prefix='Generating starting builds: ', suffix='Complete')
    starting_builds = starting_builds[:max_best_length]


    progressbar.printProgressBar(0, generations, prefix='Generating progress: ', suffix='Complete')
    current_builds = starting_builds
    resulting_builds = current_builds
    for i in range(generations):
        resulting_builds = evolution_steps(max_best_length, current_builds, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, stat_to_optimise, skill_points_req_array_pos, added_skill_points_pos, min_optimised_stat_req)
        current_builds = resulting_builds
        progressbar.printProgressBar(i+1, generations, prefix='Generating progress: ', suffix='Complete')





    for i, build in enumerate(resulting_builds):
        combined_stats = evaluate.combine_build_stats(build)
        item_names = [item[0] for item in build]
        #print(f'Build: {item_names}')
        print(f'https://wynnbuilder.github.io/builder/#{encoder.encode_build(build)}')
        #print(f'Stats: {combined_stats}')
        if i > return_amount:
            break
    input()





if __name__ == "__main__":
    main()
