import itertools
from collections import defaultdict
import human_readable_stat_names_and_indices as stat_indices
import numpy as np


#########################################################################################
#########################################################################################
#########################################################################################
#
# This file has been taken from wynnbuilder.github.io's codebase and adapted to python by AI.
# Later further adapted for this project by the autor of the project.
# Original code can be found at: https://github.com/wynnbuilder/wynnbuilder.github.io (please tell me I did this right)
# 
# First edited 2025-12-09
# Last edited 2025-12-10
#
#
#########################################################################################
#########################################################################################
#########################################################################################







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


