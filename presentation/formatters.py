def fmt(n: int) -> str:
    return f"{round(n):,}"


def fmt_k(n: float) -> str:
    if n >= 1_000_000:
        return f"${n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"${n/1_000:.1f}K"
    return f"${n:.0f}"
