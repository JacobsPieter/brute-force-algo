import numpy as np
from numba import njit, prange
from parse_items import (
    load_items_from_json,
    make_required_stats_array,
    reconstruct_combination_name
)

# ----------------------------
# Numba-compatibele validatie
# ----------------------------
@njit
def fast_valid(stats: np.ndarray, required: np.ndarray) -> bool:
    for i in range(len(stats)):
        if stats[i] < required[i]:
            return False
    return True

# ----------------------------
# Parallel & memory-efficient Numba-loop
# ----------------------------
@njit(parallel=True)
def find_best_combinations(
    weapon_stats, helmet_stats, chest_stats, legging_stats,
    boot_stats, ring_stats, bracelet_stats, necklace_stats,
    required_stats, best_amount
):
    # -- Fallback voor lege categorieën: altijd vaste arrays teruggeven --
    if (
        weapon_stats.shape[0] == 0 or helmet_stats.shape[0] == 0 or
        chest_stats.shape[0] == 0 or legging_stats.shape[0] == 0 or
        boot_stats.shape[0] == 0 or ring_stats.shape[0] == 0 or
        bracelet_stats.shape[0] == 0 or necklace_stats.shape[0] == 0
    ):
        empty_scores = np.full(1, -9223372036854775808, dtype=np.int64)
        empty_combs = np.zeros((1, 9), dtype=np.int64)
        return empty_scores, empty_combs

    n_weapons = weapon_stats.shape[0]
    n_helmets = helmet_stats.shape[0]
    n_chest = chest_stats.shape[0]
    n_legging = legging_stats.shape[0]
    n_boot = boot_stats.shape[0]
    n_ring = ring_stats.shape[0]
    n_bracelet = bracelet_stats.shape[0]
    n_necklace = necklace_stats.shape[0]

    # Top best_amount combinaties opslaan
    scores = np.full(best_amount, -9223372036854775808, dtype=np.int64)
    comb_indices = np.zeros((best_amount, 9), dtype=np.int64)

    for i in prange(n_weapons):
        ws = weapon_stats[i]
        for j in range(n_helmets):
            hs = helmet_stats[j]
            wh = ws + hs
            if not fast_valid(wh, required_stats):
                continue

            for k in range(n_chest):
                ch = chest_stats[k]
                whc = wh + ch
                if not fast_valid(whc, required_stats):
                    continue

                for l in range(n_legging):
                    lg = legging_stats[l]
                    whcl = whc + lg
                    if not fast_valid(whcl, required_stats):
                        continue

                    for m in range(n_boot):
                        bs = boot_stats[m]
                        whclb = whcl + bs
                        if not fast_valid(whclb, required_stats):
                            continue

                        for n_idx in range(n_ring):
                            r1 = ring_stats[n_idx]
                            whclbr = whclb + r1
                            if not fast_valid(whclbr, required_stats):
                                continue

                            for o_idx in range(n_ring):
                                r2 = ring_stats[o_idx]
                                whclbrr = whclbr + r2
                                if not fast_valid(whclbrr, required_stats):
                                    continue

                                for p in range(n_bracelet):
                                    br = bracelet_stats[p]
                                    whclbrrba = whclbrr + br
                                    if not fast_valid(whclbrrba, required_stats):
                                        continue

                                    for q in range(n_necklace):
                                        nk = necklace_stats[q]
                                        final_stats = whclbrrba + nk
                                        if not fast_valid(final_stats, required_stats):
                                            continue

                                        # score: bv. eerste stat
                                        score = final_stats[0]

                                        # min-heap logic voor top best_amount
                                        min_idx = 0
                                        min_val = scores[0]
                                        for t in range(1, best_amount):
                                            if scores[t] < min_val:
                                                min_val = scores[t]
                                                min_idx = t
                                        if score > min_val:
                                            scores[min_idx] = score
                                            comb_indices[min_idx, 0] = i
                                            comb_indices[min_idx, 1] = j
                                            comb_indices[min_idx, 2] = k
                                            comb_indices[min_idx, 3] = l
                                            comb_indices[min_idx, 4] = m
                                            comb_indices[min_idx, 5] = n_idx
                                            comb_indices[min_idx, 6] = o_idx
                                            comb_indices[min_idx, 7] = p
                                            comb_indices[min_idx, 8] = q

    return scores, comb_indices

# ----------------------------
# Hoofdfunctie
# ----------------------------
def run_all_combinations(json_path: str, required_stats: dict, best_amount: int = 10):
    _, numba_structs = load_items_from_json(json_path)
    stat_order = numba_structs["stat_order"]
    required_arr = make_required_stats_array(required_stats, stat_order)

    scores, comb_indices = find_best_combinations(
        numba_structs["weapon_stats"],
        numba_structs["helmet_stats"],
        numba_structs["chest_stats"],
        numba_structs["legging_stats"],
        numba_structs["boot_stats"],
        numba_structs["ring_stats"],
        numba_structs["bracelet_stats"],
        numba_structs["necklace_stats"],
        required_arr,
        best_amount
    )

    # Controleer of lege arrays zijn teruggekomen
    if scores[0] == -9223372036854775808:
        return {}

    best_combinations = {}
    for i in range(scores.shape[0]):
        if scores[i] == -9223372036854775808:
            continue  # nooit ingevulde slot
        idxs = comb_indices[i]

        # Veilige reconstructie van namen
        name = reconstruct_combination_name(idxs, numba_structs)
        total_stats = (
            numba_structs["weapon_stats"][idxs[0]] +
            numba_structs["helmet_stats"][idxs[1]] +
            numba_structs["chest_stats"][idxs[2]] +
            numba_structs["legging_stats"][idxs[3]] +
            numba_structs["boot_stats"][idxs[4]] +
            numba_structs["ring_stats"][idxs[5]] +
            numba_structs["ring_stats"][idxs[6]] +
            numba_structs["bracelet_stats"][idxs[7]] +
            numba_structs["necklace_stats"][idxs[8]]
        )
        best_combinations[name] = total_stats
    return best_combinations

# ----------------------------
# Test
# ----------------------------
if __name__ == "__main__":
    JSON_PATH = "items.json"
    REQUIRED_STATS = {"strength": 10, "dexterity": 5, "intelligence": 0, "defense": 8, "agility": 0}
    BEST_AMOUNT = 5

    best_combos = run_all_combinations(JSON_PATH, REQUIRED_STATS, BEST_AMOUNT)
    for name, stats in best_combos.items():
        print(name, stats)
