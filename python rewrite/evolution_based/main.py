import parser
import encoder
import evaluate_build as evaluate
import progressbar
from classes import *



import random as rd
import json
import itertools




with open('python rewrite\\evolution_based\\config.json', 'r') as config_file:
    config = json.load(config_file)




min_optimised_stat_req = 0




def initialise_build(
        helmets: list[Armour], chestplates: list[Armour], leggings: list[Armour], boots: list[Armour],
        rings: list[Accessory], bracelets: list[Accessory], necklaces: list[Accessory],
        weapons: list[Weapon],
        armour_tomes: list[Tome], weapon_tomes: list[Tome], marathon_tomes: list[Tome], expertise_tomes: list[Tome], 
        mysticism_tomes: list[Tome], lootrunning_tomes: list[Tome], guild_tomes: list[Tome]):

    helmet = rd.choice(helmets)
    chestplate = rd.choice(chestplates)
    legging = rd.choice(leggings)
    boot = rd.choice(boots)
    
    ring1 = rd.choice(rings)
    ring2 = rd.choice(rings)
    bracelet = rd.choice(bracelets)
    necklace = rd.choice(necklaces)
    
    weapon = rd.choice(weapons)

    armour_tomes_list = [rd.choice(armour_tomes) for _ in range(4)]
    weapon_tomes_list = [rd.choice(weapon_tomes) for _ in range(2)]
    marathon_tomes_list = [rd.choice(marathon_tomes) for _ in range(2)]
    expertise_tomes_list = [rd.choice(expertise_tomes) for _ in range(2)]
    mysticism_tomes_list = [rd.choice(mysticism_tomes) for _ in range(2)]
    lootrunning_tomes_list = [rd.choice(lootrunning_tomes)]
    guild_tomes_list = [rd.choice(guild_tomes)]
    
    
    armour = [helmet, chestplate, legging, boot]
    accessories = [ring1, ring2, bracelet, necklace]
    tomes = [armour_tomes_list, weapon_tomes_list, marathon_tomes_list, expertise_tomes_list, mysticism_tomes_list, lootrunning_tomes_list, guild_tomes_list]
    starting_build = Build(armour, accessories, weapon, tomes)
    return starting_build


def initialise_starting_builds(
        helmets: list[Armour], chestplates: list[Armour], leggings: list[Armour], boots: list[Armour],
        rings: list[Accessory], bracelets: list[Accessory], necklaces: list[Accessory],
        weapons: list[Weapon],
        armour_tomes: list[Tome], weapon_tomes: list[Tome], marathon_tomes: list[Tome], expertise_tomes: list[Tome], 
        mysticism_tomes: list[Tome], lootrunning_tomes: list[Tome], guild_tomes: list[Tome],
        generate_per_iteration: int):
    
    
    starting_builds = [initialise_build(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes) for _ in range(generate_per_iteration)]
    return starting_builds


def gen_new_build_mutations(
        change_per_generation: int,
        existing_build: Build,
        helmets: list[Armour], chestplates: list[Armour], leggings: list[Armour], boots: list[Armour],
        rings: list[Accessory], bracelets: list[Accessory], necklaces: list[Accessory],
        weapons: list[Weapon],
        armour_tomes: list[Tome], weapon_tomes: list[Tome], marathon_tomes: list[Tome], expertise_tomes: list[Tome], 
        mysticism_tomes: list[Tome], lootrunning_tomes: list[Tome], guild_tomes: list[Tome]):
    
    changed_builds: list[Build] = [existing_build]
    for _ in range(change_per_generation):
        changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
        list_to_choose_item_from = rd.choice([helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes])
        if isinstance(list_to_choose_item_from[0], Tome):
            check_by_item = list_to_choose_item_from[0]
            match check_by_item.type:
                case 'armour':
                    changed.set_item(rd.choice(list_to_choose_item_from), rd.randint(0,3))
                case 'guild':
                    changed.set_item(rd.choice(list_to_choose_item_from), 0)
                case 'lootrun':
                    changed.set_item(rd.choice(list_to_choose_item_from), 0)
                case _:
                    changed.set_item(rd.choice(list_to_choose_item_from), rd.randint(0,1))
        if list_to_choose_item_from[0].type == 'ring':
            changed.set_item(rd.choice(list_to_choose_item_from), rd.randint(0,1))
        else:
            changed.set_item(rd.choice(list_to_choose_item_from))

        changed_builds.append(changed)
    return changed_builds



def evolution_step(
        keep_per_step: int,
        change_per_generation: int,
        current_builds: list[Build],
        helmets: list[Armour], chestplates: list[Armour], leggings: list[Armour], boots: list[Armour],
        rings: list[Accessory], bracelets: list[Accessory], necklaces: list[Accessory],
        weapons: list[Weapon],
        armour_tomes: list[Tome], weapon_tomes: list[Tome], marathon_tomes: list[Tome], expertise_tomes: list[Tome], 
        mysticism_tomes: list[Tome], lootrunning_tomes: list[Tome], guild_tomes: list[Tome]):
    
    new_build_mutations = list(itertools.chain.from_iterable([gen_new_build_mutations(change_per_generation, build, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes) for build in current_builds]))
    
    next_builds: list[Build] = evaluate.evaluate_builds(keep_per_step, new_build_mutations, config)
    
    return next_builds









def main():
    items = parser.parse_items('data\\items.json')
    
    helmets, chestplates, leggings, boots, rings, bracelets, necklaces, spears, bows, daggers, wands, reliks, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes, mysticism_tomes, lootrunning_tomes, guild_tomes = items
    weapons = list(itertools.chain(spears, bows, daggers, wands, reliks))




    weapons = [item for item in weapons if item.name == "Guardian"]

    generations = config["algorithm"]["generations"]
    max_best_length = config["algorithm"]["subjects"]
    change_per_generation = config["algorithm"]["change_per_generation"]
    return_amount = config["return_length"]
    

    starting_builds: list[Build] = []
    progressbar.printProgressBar(0, max_best_length, prefix='Generating starting builds: ', suffix='Complete')
    while len(starting_builds) < max_best_length:
        starting_builds.extend(initialise_starting_builds(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes, 10))
        starting_builds = evaluate.evaluate_builds(max_best_length, starting_builds, config)
        progressbar.printProgressBar(len(starting_builds), max_best_length, prefix='Generating starting builds: ', suffix='Complete')
    starting_builds = starting_builds[:max_best_length]


    progressbar.printProgressBar(0, generations, prefix='Generating progress: ', suffix='Complete')
    current_builds = starting_builds
    resulting_builds = current_builds
    for i in range(generations):
        resulting_builds = evolution_step(max_best_length, change_per_generation, current_builds, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes)
        current_builds = resulting_builds
        progressbar.printProgressBar(i+1, generations, prefix='Generating progress: ', suffix='Complete')





    for i, build in enumerate(resulting_builds):
        print(f'https://wynnbuilder.github.io/builder/#{encoder.encode_build(build)}')
        if i > return_amount:
            break
    input()





if __name__ == "__main__":
    main()
