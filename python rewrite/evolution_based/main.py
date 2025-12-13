import parser
import human_readable_stat_names_and_indices as stat_indices
import encoder
import evaluate_build as evaluate
import progressbar
from classes import *


import numpy as np
from numba import njit
import random as rd
import json
import itertools


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


def initialise_build(
        helmets: list[Armour], chestplates: list[Armour], leggings: list[Armour], boots: list[Armour],
        rings: list[Accessory], bracelets: list[Accessory], necklaces: list[Accessory],
        weapons: list[Weapon]):

    helmet = rd.choice(helmets)
    chestplate = rd.choice(chestplates)
    legging = rd.choice(leggings)
    boot = rd.choice(boots)
    
    ring1 = rd.choice(rings)
    ring2 = rd.choice(rings)
    bracelet = rd.choice(bracelets)
    necklace = rd.choice(necklaces)
    
    weapon = rd.choice(weapons)
    
    
    armour = [helmet, chestplate, legging, boot]
    accessories = [ring1, ring2, bracelet, necklace]
    starting_build = Build(armour, accessories, weapon, [])
    return starting_build


def initialise_starting_builds(
        helmets: list[Armour],
        chestplates: list[Armour],
        leggings: list[Armour],
        boots: list[Armour],
        rings: list[Accessory],
        bracelets: list[Accessory],
        necklaces: list[Accessory],
        weapons: list[Weapon],
        generate_per_iteration: int):
    
    
    starting_builds = [initialise_build(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons) for _ in range(generate_per_iteration)]
    return starting_builds


def gen_new_build_mutations(
        existing_build: Build,
        helmets: list[Armour],
        chestplates: list[Armour],
        leggings: list[Armour],
        boots: list[Armour],
        rings: list[Accessory],
        bracelets: list[Accessory],
        necklaces: list[Accessory],
        weapons: list[Weapon]):
    helmet_changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
    helmet_changed.helmet = rd.choice(helmets)
    chestplate_changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
    chestplate_changed.chestplate = rd.choice(chestplates)
    legging_changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
    legging_changed.leggings = rd.choice(leggings)
    boot_changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
    boot_changed.boots = rd.choice(boots)
    ring1_changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
    ring1_changed.ring1 = rd.choice(rings)
    ring2_changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
    ring2_changed.ring2 = rd.choice(rings)
    bracelet_changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
    bracelet_changed.bracelet = rd.choice(bracelets)
    necklace_changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
    necklace_changed.necklace = rd.choice(necklaces)
    weapon_changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
    weapon_changed.weapon = rd.choice(weapons)
    return [helmet_changed, chestplate_changed, legging_changed, boot_changed, ring1_changed, ring2_changed, bracelet_changed, necklace_changed, weapon_changed, existing_build]



def evolution_step(
        keep_per_step: int,
        current_builds: list[Build],
        helmets: list[Armour],
        chestplates: list[Armour],
        leggings: list[Armour],
        boots: list[Armour],
        rings: list[Accessory],
        bracelets: list[Accessory],
        necklaces: list[Accessory],
        weapons: list[Weapon]):
    
    new_build_mutations = []
    new_build_mutations = list(itertools.chain.from_iterable([gen_new_build_mutations(build, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons) for build in current_builds]))
    
    next_builds: list[Build] = evaluate.evaluate_builds(keep_per_step, new_build_mutations, config)
    
    return next_builds









def main():
    items = parser.parse_items('data\\items.json')
    tomes = parser.parse_tomes('data\\tomes.json')
    
    helmets, chestplates, leggings, boots, rings, bracelets, necklaces, spears, bows, daggers, wands, reliks = items
    weapons = list(itertools.chain(spears, bows, daggers, wands, reliks))




    weapons = [item for item in weapons if item.name == "Guardian"]

    generations = config["algorithm"]["generations"]
    max_best_length = config["algorithm"]["subjects"]
    return_amount = config["return_length"]
    

    starting_builds: list[Build] = []
    progressbar.printProgressBar(0, max_best_length, prefix='Generating starting builds: ', suffix='Complete')
    while len(starting_builds) < max_best_length:
        starting_builds.extend(initialise_starting_builds(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, 10))
        starting_builds = evaluate.evaluate_builds(max_best_length, starting_builds, config)
        progressbar.printProgressBar(len(starting_builds), max_best_length, prefix='Generating starting builds: ', suffix='Complete')
    starting_builds = starting_builds[:max_best_length]


    progressbar.printProgressBar(0, generations, prefix='Generating progress: ', suffix='Complete')
    current_builds = starting_builds
    resulting_builds = current_builds
    for i in range(generations):
        resulting_builds = evolution_step(max_best_length, current_builds, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons)
        current_builds = resulting_builds
        progressbar.printProgressBar(i+1, generations, prefix='Generating progress: ', suffix='Complete')





    for i, build in enumerate(resulting_builds):
        combined_stats = build.get_combined_build_stats()
        item_names = [item.name for item in build.get_all_items()]
        #print(f'Build: {item_names}')
        print(f'https://wynnbuilder.github.io/builder/#{encoder.encode_build(build)}')
        #print(f'Stats: {combined_stats}')
        if i > return_amount:
            break
    input()





if __name__ == "__main__":
    main()
