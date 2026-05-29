def raffles_for_budget(budget_exp: float, base_exp: float, gamma: float) -> int:
    if base_exp <= 0:
        return 0
    n, cum = 0, 0.0
    while n < 100_000:
        nxt = cum + base_exp * ((n + 1) ** gamma)
        if nxt > budget_exp:
            break
        cum, n = nxt, n + 1
    return n


def compute_derived(
    players: dict[str, int],
    spends: dict[str, int],
    exp_rate: int,
    base_exp: float,
    gamma: float,
    buckets: list[dict],
) -> tuple[dict[str, dict], int]:
    derived: dict[str, dict] = {}
    total_pool = 0

    for b in buckets:
        bid = b["id"]
        per = raffles_for_budget(spends[bid] * exp_rate, base_exp, gamma)
        total = per * players[bid]
        derived[bid] = {"per": per, "total": total}
        total_pool += total

    for b in buckets:
        bid = b["id"]
        derived[bid]["share"] = derived[bid]["total"] / total_pool if total_pool > 0 else 0

    return derived, total_pool


def compute_total_money(
    players: dict[str, int],
    spends: dict[str, int],
    buckets: list[dict],
) -> int:
    return sum(players[b["id"]] * spends[b["id"]] for b in buckets)
