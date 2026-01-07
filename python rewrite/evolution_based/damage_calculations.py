import numpy as np

from classes import *

class Spell:
    def __init__(self) -> None:
        self.conversions: np.ndarray

def apply_attack_speed(build: Build):
    return np.multiply(build.weapon.attackspeed, build.weapon.damages)

#TODO: Fix
def apply_conversions(damage: np.ndarray, spell: Spell):

    total = damage.sum(axis=0)  # (2,)
    conversions = spell.conversions

    # neutral scaling
    out = damage * conversions[:, None]

    # elemental copy from total (no neutral)
    out[1:, :] += total * conversions[1:, None]

    return out

def apply_additive_damage(damage: np.ndarray, additive: np.ndarray):
    mask = (damage.sum(axis=1) > 0)[:, None]
    return damage + additive * mask


def apply_percent_boosts(damage: np.ndarray, percent_mults: np.ndarray):
    return damage * percent_mults[:, None]

def apply_raw_damage(damage: np.ndarray, raw: float, rainbow_raw: float, conversion_sum: float):
    totals = damage.sum(axis=0)  # (2,)

    # avoid division by zero
    ratios = np.divide(
        damage,
        totals,
        out=np.zeros_like(damage),
        where=totals > 0
    )

    raw_matrix = ratios * raw

    # rainbow raw applies only to elements
    raw_matrix[1:, :] += ratios[1:, :] * rainbow_raw

    return damage + raw_matrix * conversion_sum

def apply_final_multipliers(damage: np.ndarray, strength_mult: float, other_mult: float, crit_bonus: float):
    base_mult = strength_mult * other_mult
    crit_mult = (strength_mult + crit_bonus) * other_mult

    normal = damage * base_mult
    crit = damage * crit_mult

    return np.maximum(normal, 0), np.maximum(crit, 0)

def calculate_spell_damages(build: Build, spell: Spell):
    damage = apply_attack_speed(build)
    damage = apply_conversions(damage, spell)
    damage = apply_additive_damage(damage, additive=np.array([]))
    damage = apply_percent_boosts(damage, percent_mults=np.array([]))
    damage = apply_raw_damage(damage, .5, .5, .5)
    return apply_final_multipliers(damage, strength_mult=0.5, other_mult=0.5, crit_bonus=0.5)

def calculate_attack_damage(build: Build, attack_type: str):
    if attack_type == 'melee':
        pass
    else:
        spell = Spell()
        damages = calculate_spell_damages(build, spell)



