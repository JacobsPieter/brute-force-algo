import numpy as np
from classes import *
import abilities


def apply_attack_speed(build: Build):
    return np.multiply(build.weapon.attackspeed, build.weapon.damages)

#TODO: Fix
def apply_conversions(damage: np.ndarray, spell: abilities.Ability):
    conversions = spell.conversions
    total = sum(damage)
    neutral_damage_mult = np.multiply(damage, conversions[0])
    elemental_damage_mult = np.multiply(total, conversions)
    elemental_damage_mult[0] = 0 #this shouldn't have been multiplied, but the shape has to be the same
    end_damage = np.add(neutral_damage_mult, elemental_damage_mult)


    return end_damage

def apply_additive_damage(damage: np.ndarray, additive: np.ndarray):
    pass


def apply_percent_boosts(damage: np.ndarray, percent_mults: np.ndarray):
    percent_mults = np.add(percent_mults, np.array([1]*6))
    damage = np.multiply(damage, percent_mults[0])
    damage[1:] = np.multiply(damage[1:], percent_mults[1:])
    return damage

def apply_raw_damage(damage: np.ndarray, raw: np.ndarray, spell: abilities.Ability):
    scaled_damage = np.multiply()
    damage = np.add(damage, np.multiply(raw[1:], spell.total_convert))
    return damage


#TODO: fix
def apply_final_multipliers(damage: np.ndarray, strength_mult: float, other_mult: float, crit_bonus: float):
    base_mult = strength_mult * other_mult
    crit_mult = (strength_mult + crit_bonus) * other_mult

    normal = damage * base_mult
    crit = damage * crit_mult

    return np.maximum(normal, 0), np.maximum(crit, 0)

def calculate_spell_damages(build: Build, ability: abilities.Ability):
    damage = apply_attack_speed(build)
    damage = apply_conversions(damage, ability)
    #TODO: When adding ability tree: add additive damage
    #damage = apply_additive_damage(damage, additive=np.array([]))
    damage = apply_percent_boosts(damage, percent_mults=np.array([]))
    damage = apply_raw_damage(damage, np.array([]), ability)
    #TODO: When adding ability tree: add the final multipliers
    #damage = apply_final_multipliers(damage, strength_mult=0.5, other_mult=0.5, crit_bonus=0.5)
    return damage

def calculate_melee_damages(build: Build, ability: abilities.Ability):
    damage = build.weapon.damages
    damage = apply_conversions(damage, ability)
    #TODO: add when ability tree
    #damage = apply_additive_damage(damage, additive=np.array([]))
    damage = apply_percent_boosts(damage, percent_mults=np.array([]))
    raw_damage = np.array([])
    damage = apply_raw_damage(damage, np.array([]), ability)
    #TODO: add when ability tree
    #damage = apply_final_multipliers(damage, strength_mult, other_mult, crit_bonus)
    return damage


def calculate_damage(build, ability: abilities.Ability):
    if ability.scaling == 'melee':
        return calculate_melee_damages(build, ability)
    else:
        return calculate_spell_damages(build, ability)








if __name__ == '__main__':
    damage = np.array([20, 10, 60, 0, 0, 0]) * 2.05
    ability = abilities.warrior_abilities['bash']
    damage = apply_conversions(damage, ability)
    damage = apply_percent_boosts(damage, np.array([0, 0, 0, 0, 0, 0]))
    damage = apply_raw_damage(damage, np.array([10, 0, 0, 0, 0, 0]), ability)
    print(sum(damage))
    print(damage)
