MIN_BUCKETS = 3
MAX_BUCKETS = 10
DEFAULT_TOTAL_PLAYERS = 500

BUCKET_CATALOG = [
    {"id": "shrimp",    "name": "Shrimp",    "range": "Micro spend",     "bg": "#F9E8E8", "tx": "#6B2020", "ac": "#D44A4A"},
    {"id": "guppy",     "name": "Guppy",     "range": "Very low spend",  "bg": "#EBF7E0", "tx": "#1E5B0E", "ac": "#4CAF20"},
    {"id": "minnow",    "name": "Minnow",    "range": "Low spend",       "bg": "#E1F5EE", "tx": "#085041", "ac": "#1D9E75"},
    {"id": "perch",     "name": "Perch",     "range": "Low-mid spend",   "bg": "#E0F7F5", "tx": "#065040", "ac": "#1AB5A0"},
    {"id": "bass",      "name": "Bass",      "range": "Mid spend",       "bg": "#E0EEF8", "tx": "#083050", "ac": "#1E6FB8"},
    {"id": "tuna",      "name": "Tuna",      "range": "Upper mid spend", "bg": "#E6F1FB", "tx": "#0C447C", "ac": "#378ADD"},
    {"id": "marlin",    "name": "Marlin",    "range": "High spend",      "bg": "#EAE9FC", "tx": "#2B2580", "ac": "#5E58E0"},
    {"id": "swordfish", "name": "Swordfish", "range": "Very high spend", "bg": "#F0E8FA", "tx": "#4A1A70", "ac": "#8B3EC8"},
    {"id": "shark",     "name": "Shark",     "range": "Elite spend",     "bg": "#F7E8F4", "tx": "#6B0850", "ac": "#C83090"},
    {"id": "whale",     "name": "Whale",     "range": "Top spend",       "bg": "#FAECE7", "tx": "#712B13", "ac": "#D85A30"},
]

# Default avg spend per player ($) by bucket id
DEFAULT_SPEND = {
    "shrimp":      50,
    "guppy":      100,
    "minnow":     150,
    "perch":      200,
    "bass":       300,
    "tuna":       400,
    "marlin":     600,
    "swordfish": 1000,
    "shark":     2000,
    "whale":     4000,
}

# Player share (%) per active bucket, low → high spend; must sum to 100
PLAYER_SHARE_BY_COUNT: dict[int, list[int]] = {
    3:  [60, 30, 10],                    # Shrimp, Minnow, Whale
    4:  [50, 25, 15, 10],                # Shrimp, Perch, Marlin, Whale
    5:  [40, 25, 20, 10,  5],            # Shrimp, Minnow, Bass, Swordfish, Whale
    6:  [35, 25, 18, 12,  7,  3],        # Shrimp, Minnow, Bass, Tuna, Swordfish, Whale
    7:  [30, 22, 16, 12,  9,  6,  5],    # Shrimp, Minnow, Perch, Bass, Marlin, Shark, Whale
    8:  [25, 18, 15, 12, 10,  8,  7,  5],
    9:  [22, 16, 14, 12, 10,  9,  8,  5,  4],
    10: [30, 20, 15, 10,  8,  6,  4,  3.6, 2,  1.4],
}

# Legacy: (players, spend) — players are overridden by distribute_players()
DEFAULTS = {bid: (0, DEFAULT_SPEND[bid]) for bid in DEFAULT_SPEND}


def get_active_buckets(count: int) -> list[dict]:
    count = max(MIN_BUCKETS, min(MAX_BUCKETS, count))
    if count == 3:
        return [BUCKET_CATALOG[0], BUCKET_CATALOG[2], BUCKET_CATALOG[9]]
    if count == MAX_BUCKETS:
        return BUCKET_CATALOG[:]
    indices = [round(i * (MAX_BUCKETS - 1) / (count - 1)) for i in range(count)]
    return [BUCKET_CATALOG[i] for i in indices]


def distribute_players(
    bucket_count: int,
    total: int = DEFAULT_TOTAL_PLAYERS,
) -> dict[str, int]:
    bucket_count = max(MIN_BUCKETS, min(MAX_BUCKETS, bucket_count))
    buckets = get_active_buckets(bucket_count)
    shares = PLAYER_SHARE_BY_COUNT[bucket_count]
    if len(shares) != len(buckets):
        raise ValueError(
            f"Share count {len(shares)} does not match bucket count {len(buckets)}"
        )

    raw = [total * s / 100 for s in shares]
    counts = [int(x) for x in raw]
    remainder = total - sum(counts)
    fractional = sorted(
        ((raw[i] - counts[i], i) for i in range(len(buckets))),
        reverse=True,
    )
    for k in range(remainder):
        counts[fractional[k][1]] += 1

    return {buckets[i]["id"]: counts[i] for i in range(len(buckets))}


def apply_default_player_distribution(
    session_state,
    bucket_count: int | None = None,
    total: int = DEFAULT_TOTAL_PLAYERS,
) -> None:
    count = bucket_count if bucket_count is not None else session_state.bucket_count
    distribution = distribute_players(count, total)
    active_ids = set(distribution)
    for b in BUCKET_CATALOG:
        bid = b["id"]
        session_state[f"{bid}_players"] = distribution.get(bid, 0)


# Legacy alias kept for any direct imports
BUCKETS = get_active_buckets(3)
