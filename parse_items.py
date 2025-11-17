import json
import numpy as np
from typing import Dict, List, Tuple

# ----------------------------
# Stat arrays maken
# ----------------------------
def _make_stat_array(item: dict, stat_order: List[str]) -> np.ndarray:
    """
    Maakt een NumPy-array voor een item, vult alleen bestaande stats.
    Ontbrekende stats krijgen 0.
    """
    arr = np.zeros(len(stat_order), dtype=np.int64)
    for idx, stat in enumerate(stat_order):
        if stat in item:
            arr[idx] = item[stat]
    return arr

def make_stat_arrays(items: List[dict], stat_order: List[str]) -> np.ndarray:
    """
    Converteert een lijst items naar een 2D NumPy array (n_items x n_stats)
    """
    n_items = len(items)
    n_stats = len(stat_order)
    arr = np.zeros((n_items, n_stats), dtype=np.int64)
    for i, item in enumerate(items):
        arr[i] = _make_stat_array(item, stat_order)
    return arr

# ----------------------------
# Namen arrays
# ----------------------------
def make_name_list(items: List[dict], name_key: str) -> List[str]:
    """
    Haalt de namen op van een lijst items. Lege lijst als geen items.
    """
    if not items:
        return []
    return [item.get(name_key, f"<unnamed>") for item in items]

# ----------------------------
# Reconstructie van combinatienamen
# ----------------------------
def reconstruct_combination_name(indices: np.ndarray, name_structs: Dict[str, List[str]]) -> str:
    """
    Zet indices om in een combinatie naam. Veilige fallback voor ontbrekende indices.
    """
    cats = ["weapon", "helmet", "chest", "legging", "boot", "ring", "ring", "bracelet", "necklace"]
    names = []
    for i, cat in enumerate(cats):
        name_list = name_structs.get(f"{cat}_names", [])
        if i >= len(indices) or indices[i] >= len(name_list):
            names.append(f"<missing {cat}>")
        else:
            names.append(name_list[indices[i]])
    return " + ".join(names)

# ----------------------------
# Required stats array
# ----------------------------
def make_required_stats_array(required_stats: Dict[str, int], stat_order: List[str]) -> np.ndarray:
    """
    Converteert required stats dict naar NumPy array
    """
    if stat_order is None:
        stat_order = list(required_stats.keys())
    arr = np.zeros(len(stat_order), dtype=np.int64)
    for idx, stat in enumerate(stat_order):
        if stat in required_stats and required_stats[stat] is not None:
            arr[idx] = required_stats[stat]
        # anders blijft 0
    return arr

# ----------------------------
# JSON laden
# ----------------------------
def load_items_from_json(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Bepaal stat_order indien None
    stats_set = set()
    for cat_items in data.values():
        if isinstance(cat_items, list):
            for item in cat_items:
                if isinstance(item, dict):
                    stats_set.update(k for k in item.keys() if k != "name")
    stat_order = list(stats_set)

    numba_structs = {}
    categories = [
        ("weapon", "weapons"),
        ("helmet", "helmets"),
        ("chest", "chestplates"),
        ("legging", "leggings"),
        ("boot", "boots"),
        ("ring", "rings"),
        ("bracelet", "bracelets"),
        ("necklace", "necklaces"),
    ]

    for short, long_name in categories:
        cat_items = data.get(long_name, [])

        # -- FIX: categorie moet lijst zijn, zoniet vervangen door lege lijst --
        if not isinstance(cat_items, list):
            cat_items = []

        # Filter alle niet-dicts (kan ook voorkomen)
        cat_items = [it for it in cat_items if isinstance(it, dict)]

        if len(cat_items) == 0:
            numba_structs[f"{short}_stats"] = np.zeros((0, len(stat_order)), dtype=np.int64)
            numba_structs[f"{short}_names"] = []
        else:
            numba_structs[f"{short}_stats"] = make_stat_arrays(cat_items, stat_order)
            numba_structs[f"{short}_names"] = make_name_list(cat_items, "name")

    numba_structs["stat_order"] = stat_order
    return data, numba_structs


    for cat in ["weapon", "helmet", "chest", "legging", "boot", "ring", "bracelet", "necklace"]:
        items_list = data.get(cat + "s", [])
        numba_structs[f"{cat}_stats"] = make_stat_arrays(items_list, stat_order) if items_list else np.zeros((0,len(stat_order)), dtype=np.int64)
        numba_structs[f"{cat}_names"] = make_name_list(items_list, "name") if items_list else []

    numba_structs["stat_order"] = stat_order

    return data, numba_structs
