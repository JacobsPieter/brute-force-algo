import parse_items
import sort
import numba.typed
from numba import njit


MAX_SKILL_POINTS: int = 595
MAX_STRREQ: int = 320
MAX_DEXREQ: int = 317
MAX_INTREQ: int = 283
MAX_DEFREQ: int = 284
MAX_AGIREQ: int = 333



def get_stat_to_optimize() -> str:
    stat = input('Enter the stat to optimize: ').strip().lower()
    return stat

def get_required_stats() -> list[str]:
    stats_input = input('Enter the required stats (comma-separated): ').strip().lower()
    required_stats = [stat.strip() for stat in stats_input.split(',')]
    return required_stats

def get_min_value_for_stat(required_stats: list[str]) -> list[int]:
    min_value_input = input('Enter the minimum value for the required stats (comma-seperated, same order as required stats): ').strip()
    min_values = [int(value.strip()) for value in min_value_input.split(',')]
    return min_values

def get_required_stats_dict(stat_to_optimise: str) -> dict:
    required_stats = get_required_stats()
    required_stats_dict: dict = {}
    if required_stats != ['']:
        min_values = get_min_value_for_stat(required_stats)
        for i, stat in enumerate(required_stats):
            if stat == stat_to_optimise:
                continue
            required_stats_dict[stat] = min_values[i]
    required_stats_dict[stat_to_optimise] = None
    return required_stats_dict


def combine_stats(item1_stats: dict[str, int], item2_stats: dict[str, int]) -> dict[str, int]:
    combined_stats: dict[str, int] = {}
    for stat in set(item1_stats.keys()).union(item2_stats.keys()):
        if item1_stats.get(stat) is None:
            combined_stats[stat] = item2_stats.get(stat, 0)
            continue
        if item2_stats.get(stat) is None:
            combined_stats[stat] = item1_stats.get(stat, 0)
            continue
        combined_stats[stat] = item1_stats.get(stat, 0) + item2_stats.get(stat, 0)
    return combined_stats

    



def get_all_combinations(helmets: dict, chestplates: dict, leggings: dict, boots: dict, rings: dict, bracelets: dict, necklaces: dict, weapons: dict, required_stats: dict, best_amount):
    best_combinations: dict[str, dict[str, int]] = {}
    for weapon in weapons:
        for helmet in helmets:
            wh_stats: dict[str, int] = combine_stats(weapons[weapon], helmets[helmet])
            if wh_stats.get('strReq', 0) + wh_stats.get('dexReq',0) + wh_stats.get('intReq', 0) + wh_stats.get('defReq',0) + wh_stats.get('agiReq',0) > MAX_SKILL_POINTS:
                continue
            for chestplate in chestplates:
                whc_stats: dict[str, int] = combine_stats(wh_stats, chestplates[chestplate])
                if whc_stats.get('strReq', 0) + whc_stats.get('dexReq',0) + whc_stats.get('intReq', 0) + whc_stats.get('defReq',0) + whc_stats.get('agiReq',0) > MAX_SKILL_POINTS:
                    continue
                for legging in leggings:
                    whcl_stats: dict[str, int] = combine_stats(whc_stats, leggings[legging])
                    if whcl_stats.get('strReq', 0) + whcl_stats.get('dexReq',0) + whcl_stats.get('intReq', 0) + whcl_stats.get('defReq',0) + whcl_stats.get('agiReq',0) > MAX_SKILL_POINTS:
                        continue
                    for boot in boots:
                        whclb_stats: dict[str, int] = combine_stats(whcl_stats, boots[boot])
                        if whclb_stats.get('strReq', 0) + whclb_stats.get('dexReq',0) + whclb_stats.get('intReq', 0) + whclb_stats.get('defReq',0) + whclb_stats.get('agiReq',0) > MAX_SKILL_POINTS:
                            continue
                        for ring1 in rings:
                            whclbr_stats: dict[str, int] = combine_stats(whclb_stats, rings[ring1])
                            if whclbr_stats.get('strReq', 0) + whclbr_stats.get('dexReq',0) + whclbr_stats.get('intReq', 0) + whclbr_stats.get('defReq',0) + whclbr_stats.get('agiReq',0) > MAX_SKILL_POINTS:
                                continue
                            for ring2 in rings:
                                whclbrr_stats: dict[str, int] = combine_stats(whclbr_stats, rings[ring2])
                                if whclbrr_stats.get('strReq', 0) + whclbrr_stats.get('dexReq',0) + whclbrr_stats.get('intReq', 0) + whclbrr_stats.get('defReq',0) + whclbrr_stats.get('agiReq',0) > MAX_SKILL_POINTS:
                                    continue
                                for bracelet in bracelets:
                                    whclbrrba_stats: dict[str, int] = combine_stats(whclbrr_stats, bracelets[bracelet])
                                    if whclbrrba_stats.get('strReq', 0) + whclbrrba_stats.get('dexReq',0) + whclbrrba_stats.get('intReq', 0) + whclbrrba_stats.get('defReq',0) + whclbrrba_stats.get('agiReq',0) > MAX_SKILL_POINTS:
                                        continue
                                    for necklace in necklaces:
                                        whclbrrban_stats: dict[str, int] = combine_stats(whclbrrba_stats, necklaces[necklace])
                                        final_stats: dict[str, int] = whclbrrban_stats
                                        possible = True
                                        sort_by_stat: str = ''
                                        total_skill_req = final_stats.get('strReq', 0) + final_stats.get('dexReq',0) + final_stats.get('intReq', 0) + final_stats.get('defReq',0) + final_stats.get('agiReq',0)
                                        if total_skill_req > MAX_SKILL_POINTS:
                                            continue
                                        for counter, stat in enumerate(required_stats):
                                            if whclbrrban_stats.get(stat) is None:
                                                possible = False
                                                break
                                            stat_value = whclbrrban_stats[stat]
                                            if required_stats[stat] is not None:
                                                if stat_value < required_stats[stat]:
                                                    possible = False
                                                    break
                                            else:
                                                sort_by_stat = stat
                                        if possible:
                                            combination_name = f'{weapon} + {helmet} + {chestplate} + {legging} + {boot} + {ring1} + {ring2} + {bracelet} + {necklace}'
                                            best_combinations[combination_name] = whclbrrban_stats
                                            if len(best_combinations)>best_amount:
                                                names, stats = sort.sort_dict_by_value(best_combinations, sort_by_stat)
                                                names.reverse()
                                                stats.reverse()
                                                names, stats = names[:best_amount], stats[:best_amount]
                                                best_combinations.fromkeys(names, [stat for stat in stats])
                                            #comment to add a breakpoint
    try:
        return best_combinations
    except:
        print('something went wrong')
                                        
                                        


def listify_items(item_type: dict) -> tuple[list, list[tuple[list[str], list[int]]]]:
    parsed_data: tuple[list[str], list[dict]] = parse_items.make_lists_from_dicts(item_type)
    names = parsed_data[0]
    item_data = parsed_data[1]
    data_names: list = []
    data_values: list = []
    items_data: list[tuple[list[str], list[int]]] = [([], [])]
    for item in item_data:
        new_data_name, new_data_value = parse_items.make_lists_from_dicts(item)
        data_names.extend(new_data_name)
        data_values.extend(new_data_value)
        new_item_data: tuple[list[str], list[int]] = data_names, data_values
        data_names, data_values = [], []
        items_data.append(new_item_data)
    try:
        items_data.remove(([],[]))
    except:
        pass
    return names, items_data


def get_all_combinations_wrapper(inputs):
    output_list = []
    counter = 0
    for list in inputs:
        item_group = numba.typed.typedlist.List()
        for element in list:
            item_group.append(element)
        output_list[counter] = item_group
        counter += 1
    output = (output_list[0], output_list[1], output_list[2], output_list[3], output_list[4], output_list[5], output_list[6], output_list[7], output_list[8], output_list[9], output_list[10], output_list[11], output_list[12], output_list[13], output_list[14], output_list[15])
    return output


def main():
    item_lists = parse_items.parse_items()
    helmets, chestplates, leggings, boots, rings, bracelets, necklaces, spears, bows, daggers, wands, reliks = item_lists[0], item_lists[1], item_lists[2], item_lists[3], item_lists[4], item_lists[5], item_lists[6], item_lists[7], item_lists[8], item_lists[9], item_lists[10], item_lists[11]
    weapons = {**spears, **bows, **daggers, **wands, **reliks}
    weapons = reliks['Olympic']
    required_stats = get_required_stats_dict(get_stat_to_optimize())
    #required_stats = parse_items.make_lists_from_dicts(get_required_stats_dict(get_stat_to_optimize()))
    #weapon_names, helmet_names, chestplate_names , legging_names, boot_names, ring_names, bracelet_names, necklace_names, weapon_data, helmet_data, chestplate_data, legging_data, boot_data, ring_data, bracelet_data, necklace_data = get_all_combinations_wrapper((weapon_names, helmet_names, chestplate_names, legging_names, boot_names, ring_names, bracelet_names, necklace_names, weapon_data, helmet_data, chestplate_data, legging_data, boot_data, ring_data, bracelet_data, necklace_data))
    combinations = get_all_combinations(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, required_stats, best_amount=10)

if __name__ == "__main__":
    main()