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
