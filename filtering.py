

def filter_combinations_by_stat(combinations: dict[str, dict[str, int]], stat: str) -> dict[str, dict[str, int]]:
    filtered: dict[str, dict[str, int]] = {}
    for combo_name, stats in combinations.items():
        if stat in stats:
            filtered[combo_name] = stats
    return filtered




def filter(combinations: dict[str, dict[str, int]], required_stats: list[str]) -> dict[str, dict[str, int]]:
    new_combinations = combinations.copy()
    for stat in required_stats:
        new_combinations = filter_combinations_by_stat(new_combinations, stat)
    return new_combinations