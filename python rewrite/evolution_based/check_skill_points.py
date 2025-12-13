import itertools
from numba import njit
import numpy as np

import human_readable_stat_names_and_indices as stat_indices
from classes import *



def check_skillpoints(build: Build):
    weapon_item = build.weapon
    equipment_items = build.get_all_items()[:-1]
    
    weapon_item_sp = (weapon_item.name, (weapon_item.get_skillpoints(), weapon_item.get_skillpoints_requirements()))
    equipment_items_sp = [(item.name, (item.get_skillpoints(), item.get_skillpoints_requirements())) for item in equipment_items]

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
        total_reqs = build.get_combined_skill_point_requirements()
        needed_extra_sp = [0, 0, 0, 0, 0]
        for i, sp in enumerate(current_sp):
            if sp < total_reqs[i] and total_reqs[i] > 0:
                needed_extra_sp[i] += total_reqs[i] - current_sp[i]
                total_applied += needed_extra_sp[i]
                current_sp[i] += needed_extra_sp[i]
                applied_sp[i] += needed_extra_sp[i]
        if not all(sp_applied <= 100 for sp_applied in applied_sp) or sum(sp_applied for sp_applied in applied_sp) > 200:
            continue
        else:
            return True
    return False


