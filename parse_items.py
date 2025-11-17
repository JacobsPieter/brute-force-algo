import json
import numpy as np
from typing import Dict, Tuple, List


def parse_stat_value(value):
    """
    Convert any JSON stat value into a single numeric value.
    - ints/floats → int
    - lists → sum of numeric entries
    - booleans → int(value)
    - strings → 0 (because 'Blunt Force' etc.)
    - None → 0
    - everything else → 0
    """

    # None
    if value is None:
        return 0

    # Boolean → 0 or 1
    if isinstance(value, bool):
        return int(value)

    # Integer or float
    if isinstance(value, (int, float)):
        return int(value)

    # List (sum numeric entries)
    if isinstance(value, list):
        total = 0
        for v in value:
            try:
                total += int(v)
            except (ValueError, TypeError):
                continue
        return total

    # Strings → 0 (e.g. "Blunt Force", "Fire", "Unique", etc.)
    if isinstance(value, str):
        return 0

    # Fallback
    return 0


def load_items_from_json(json_path: str) -> Tuple[List[Dict], Dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["items"]

    # Determine stat keys
    stat_keys = set()
    for item in items:
        for k, v in item.items():
            # Skip metadata fields
            if k not in ("name", "id", "category", "type", "drop", "lore", "icon", "tier"):
                stat_keys.add(k)

    stat_order = list(stat_keys)

    categories = ["weapon", "helmet", "chestplate", "legging", "boot", "ring", "bracelet", "necklace"]
    arrays_dict = {}
    names_dict = {}

    for cat in categories:
        cat_items = [i for i in items if i.get("type") == cat or i.get("category") == cat]

        stats_arr = np.zeros((len(cat_items), len(stat_order)), dtype=np.int64)
        names_arr = []

        for idx, item in enumerate(cat_items):
            names_arr.append(item.get("name", f"{cat}_{idx}"))

            for s_idx, stat in enumerate(stat_order):
                raw_value = item.get(stat, 0)
                stats_arr[idx, s_idx] = parse_stat_value(raw_value)

        arrays_dict[f"{cat}_stats"] = stats_arr
        names_dict[f"{cat}_names"] = names_arr

    numba_structs = {**arrays_dict, **names_dict, "stat_order": stat_order}
    return items, numba_structs


def make_required_stats_array(required_stats: dict, stat_order: list) -> np.ndarray:
    arr = np.zeros(len(stat_order), dtype=np.int64)
    for idx, stat in enumerate(stat_order):
        arr[idx] = required_stats.get(stat, 0)
    return arr


def reconstruct_combination_name(indices: np.ndarray, numba_structs: dict) -> str:
    try:
        return (
            f"{numba_structs['weapon_names'][indices[0]]} + "
            f"{numba_structs['helmet_names'][indices[1]]} + "
            f"{numba_structs['chestplate_names'][indices[2]]} + "
            f"{numba_structs['legging_names'][indices[3]]} + "
            f"{numba_structs['boot_names'][indices[4]]} + "
            f"{numba_structs['ring_names'][indices[5]]} + "
            f"{numba_structs['ring_names'][indices[6]]} + "
            f"{numba_structs['bracelet_names'][indices[7]]} + "
            f"{numba_structs['necklace_names'][indices[8]]}"
        )
    except IndexError:
        return "Invalid combination"
