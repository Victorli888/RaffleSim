import random


def run_draw(derived: dict[str, dict], num_prizes: int, buckets: list[dict]) -> list[str]:
    pool: list[str] = []
    for b in buckets:
        pool.extend([b["id"]] * derived[b["id"]]["total"])

    results: list[str] = []
    n = min(num_prizes, len(pool))
    for _ in range(n):
        idx = random.randrange(len(pool))
        results.append(pool[idx])
        pool.pop(idx)
    return results


def run_monte_carlo(derived: dict[str, dict], num_prizes: int, buckets: list[dict], n_cycles: int) -> dict[str, int]:
    tally = {b["id"]: 0 for b in buckets}
    for _ in range(n_cycles):
        for bid in run_draw(derived, num_prizes, buckets):
            tally[bid] += 1
    return tally
