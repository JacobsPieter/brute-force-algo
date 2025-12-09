import itertools
from collections import defaultdict
import human_readable_stat_names_and_indices
import numpy as np


def combine_skill_point_requirements(build: list[tuple[str, np.ndarray]], skill_points_req_array_pos: tuple) -> tuple:
    str_req, dex_req, int_req, def_req, agi_req = 0, 0, 0, 0, 0
    for item in build:
        str_req = max([item[1][skill_points_req_array_pos[0]], str_req])
        dex_req = max([item[1][skill_points_req_array_pos[1]], dex_req])
        int_req = max([item[1][skill_points_req_array_pos[2]], int_req])
        def_req = max([item[1][skill_points_req_array_pos[3]], def_req])
        agi_req = max([item[1][skill_points_req_array_pos[4]], agi_req])
    return (str_req, dex_req, int_req, def_req, agi_req)




def check_skillpoints(build):
    weapon_item = build[-1]
    equipment_items = build[:-1]

    skill_indices = [human_readable_stat_names_and_indices.STAT_INDICES['strength'],
                     human_readable_stat_names_and_indices.STAT_INDICES['dexterity'],
                     human_readable_stat_names_and_indices.STAT_INDICES['intelligence'],
                     human_readable_stat_names_and_indices.STAT_INDICES['defense'],
                     human_readable_stat_names_and_indices.STAT_INDICES['agility']]
    req_indices = [human_readable_stat_names_and_indices.STAT_INDICES['strength_requirement'],
                   human_readable_stat_names_and_indices.STAT_INDICES['dexterity_requirement'],
                   human_readable_stat_names_and_indices.STAT_INDICES['intelligence_requirement'],
                   human_readable_stat_names_and_indices.STAT_INDICES['defense_requirement'],
                   human_readable_stat_names_and_indices.STAT_INDICES['agility_requirement']]
    
    weapon_item_sp = (weapon_item[0], ([int(weapon_item[1][i]) for i in skill_indices], [int(weapon_item[1][i]) for i in req_indices]))
    equipment_items_sp = [(name, ([int(stats[i]) for i in skill_indices], [int(stats[i]) for i in req_indices])) for name, stats in equipment_items]

    fixed = []
    consider = []
    noboost = []
    for name, (skillpoints, reqs) in equipment_items_sp:
        if all(x==0 for x in reqs):
            fixed.append((name, (skillpoints, reqs)))
        elif all(x <= 0 for x in skillpoints):
            noboost.append((name, (skillpoints, reqs)))
        else:
            consider.append((name, (skillpoints, reqs)))
    
    sp_base = [0, 0, 0, 0, 0]
    for name, (skillpoints, reqs) in fixed:
        for i in range(5):
            sp_base[i] += skillpoints[i]
    
    permutations = itertools.permutations(consider)
    for perm in permutations:
        current_sp = sp_base.copy()
        feasible = True
        applied_sp = [0, 0, 0, 0, 0]
        total_applied = 0
        for name, (skillpoints, reqs) in perm:
            needed_sp = [0, 0, 0, 0, 0]
            for i in range(5):
                if current_sp[i] < reqs[i] and reqs[i] > 0:
                    needed_sp[i] += reqs[i] - current_sp[i]
                    total_applied += needed_sp[i]
                    current_sp[i] += needed_sp[i]
                    applied_sp[i] += needed_sp[i]
            if not all(sp_applied <= 100 for sp_applied in applied_sp) or total_applied > 200:
                feasible = False
                break
            else:
                for i in range(5):
                    current_sp[i] += skillpoints[i]
        if not feasible:
            continue
        else:
            for name, (skillpoints, reqs) in noboost + [weapon_item_sp]:
                needed_sp = [0, 0, 0, 0, 0]
                for i in range(5):
                    if current_sp[i] < reqs[i]:
                        needed_sp[i] += reqs[i] - current_sp[i]
                        total_applied += needed_sp[i]
                        current_sp[i] += needed_sp[i]
                        applied_sp[i] += needed_sp[i]
                if not all(sp_applied <= 100 for sp_applied in applied_sp) or total_applied > 200:
                    feasible = False
                    break
                else:
                    for i in range(5):
                        current_sp[i] += skillpoints[i]
            if not feasible:
                continue
            else:
                total_reqs = combine_skill_point_requirements(build, tuple(req_indices))
                needed_extra_sp = [0, 0, 0, 0, 0]
                for i, sp in enumerate(current_sp):
                    if sp < total_reqs[i]:
                        needed_extra_sp[i] += total_reqs[i] - current_sp[i]
                        total_applied += needed_extra_sp[i]
                        current_sp[i] += needed_extra_sp[i]
                        applied_sp[i] += needed_extra_sp[i]
                if not all(sp_applied <= 100 for sp_applied in applied_sp) or sum(sp_applied for sp_applied in applied_sp) > 200:
                    continue
                else:
                    return True
    return False











def apply_skillpoints(skillpoints, item, activeSetCounts):
    for i in range(5):
        skillpoints[i] += item['skillpoints'][i]
    if item['set']:
        activeSetCounts[item['set']] += 1
    return skillpoints, activeSetCounts

def apply_to_fit(skillpoints, item, has_skillpoint, activeSetCounts):
    needed = [0] * 5
    for i in range(5):
        req = item['reqs'][i]
        current = skillpoints[i]
        if current < req:
            needed[i] = req - current
    return needed

def construct_scc_graph(consider):
    nodes = []
    terminal_node = {
        'item': None,
        'children': [],
        'parents': nodes
    }
    root_node = {
        'item': None,
        'children': nodes,
        'parents': []
    }
    skp_order = ['strength', 'dexterity', 'intelligence', 'defense', 'agility']
    for item in consider:
        set_neg = [False] * 5
        set_pos = [False] * 5
        # Assuming no sets for now
        nodes.append({
            'item': item,
            'children': [terminal_node],
            'parents': [root_node],
            'set_pos': set_pos,
            'set_neg': set_neg
        })
    # Dependency graph construction.
    for node_a in nodes:
        a = node_a['item']
        a_children = node_a['children']
        a_set_pos = node_a['set_pos']
        for node_b in nodes:
            b = node_b['item']
            b_parents = node_b['parents']
            b_set_neg = node_b['set_neg']
            for i in range(5):
                if (a['skillpoints'][i] > 0 or a_set_pos[i]) and (a['reqs'][i] < b['reqs'][i] or b['skillpoints'][i] < 0 or b_set_neg[i]):
                    if node_b not in a_children:
                        a_children.append(node_b)
                    if node_a not in b_parents:
                        b_parents.append(node_a)
                    break
    # Placeholder for SCC computation: assume no cycles, each node is its own SCC
    sccs = [{'nodes': [node], 'children': []} for node in nodes]
    root = root_node
    terminal = terminal_node
    return root, terminal, sccs

# Note: This is a direct translation, but construct_scc_graph and perm are placeholders.
# The original JS likely has more complex logic for SCC.
