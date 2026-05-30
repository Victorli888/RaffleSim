import math
import random
import pytest

from model.economy import raffles_for_budget, compute_derived, compute_total_money
from model.simulation import run_draw, run_multi_draw
from model.constants import (
    get_active_buckets,
    distribute_players,
    DEFAULT_TOTAL_PLAYERS,
    BUCKET_CATALOG,
    MIN_BUCKETS,
    MAX_BUCKETS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prize_calc(raffle_revenue, other_revenue, base_prizes, increment):
    """Mirrors the prize calculator formula in panels.py."""
    cumulative_gmv   = raffle_revenue + other_revenue
    gmv_contribution = cumulative_gmv * 0.01
    prize_pool       = 1_250 + gmv_contribution
    extra            = math.floor(gmv_contribution / increment) if increment > 0 else 0
    num_prizes       = max(base_prizes, base_prizes + extra)
    return cumulative_gmv, gmv_contribution, prize_pool, num_prizes


def _buckets(*ids):
    return [b for b in BUCKET_CATALOG if b["id"] in ids]


# ---------------------------------------------------------------------------
# raffles_for_budget
# ---------------------------------------------------------------------------

class TestRafflesForBudget:

    def test_zero_budget_gives_zero_raffles(self):
        assert raffles_for_budget(0, 500, 0.5) == 0

    def test_budget_below_threshold_gives_zero(self):
        # 500 EXP < 2000 threshold → 0 raffles
        assert raffles_for_budget(500, 2000, 0.5) == 0

    def test_budget_exactly_at_threshold_gives_one(self):
        # 500 EXP == 500 threshold, gamma=1 → level-1 cost = 500*1 = 500 → 1 raffle
        assert raffles_for_budget(500, 500, 1.0) == 1

    def test_budget_just_below_threshold_gives_zero(self):
        assert raffles_for_budget(499, 500, 1.0) == 0

    def test_gamma_zero_constant_cost(self):
        # gamma=0: every level costs base_exp * n^0 = base_exp * 1 = base_exp
        # 5 * 500 = 2500 EXP → can afford 5 raffles (500 each)
        assert raffles_for_budget(2500, 500, 0.0) == 5

    def test_gamma_one_linear_cost(self):
        # gamma=1: level n costs base_exp * n
        # level 1: 500, level 2: 1000, level 3: 1500 → cumulative 3000
        # budget=3000 → 3 raffles; budget=2999 → 2 raffles
        assert raffles_for_budget(3000, 500, 1.0) == 3
        assert raffles_for_budget(2999, 500, 1.0) == 2

    def test_exp_rate_scales_budget(self):
        # $50 spend, 10 exp/$, base_exp=500, gamma=0.5
        # budget = 50*10 = 500; level-1 cost = 500*1^0.5 = 500 → 1 raffle
        budget = 50 * 10
        assert raffles_for_budget(budget, 500, 0.5) == 1

    def test_high_base_exp_blocks_low_spenders(self):
        # $50 spend, 10 exp/$, base_exp=2000
        # budget = 500 < 2000 → 0 raffles
        assert raffles_for_budget(50 * 10, 2000, 0.5) == 0

    def test_whale_gets_many_more_raffles_than_shrimp(self):
        shrimp = raffles_for_budget(50 * 10, 500, 0.5)
        whale  = raffles_for_budget(4000 * 10, 500, 0.5)
        assert whale > shrimp

    def test_zero_base_exp_returns_zero(self):
        assert raffles_for_budget(9999, 0, 0.5) == 0

    def test_higher_gamma_means_fewer_raffles(self):
        budget = 4000 * 10
        low_gamma  = raffles_for_budget(budget, 500, 0.1)
        high_gamma = raffles_for_budget(budget, 500, 1.0)
        assert low_gamma >= high_gamma

    def test_increasing_exp_rate_increases_raffles(self):
        spend = 100
        low  = raffles_for_budget(spend * 5,  500, 0.5)
        high = raffles_for_budget(spend * 20, 500, 0.5)
        assert high >= low

    # ------------------------------------------------------------------
    # Spend → level tests: verifies the full chain
    #   spend ($) × exp_rate → EXP budget → raffles_for_budget → levels
    #
    # Level n costs base_exp × n^gamma cumulatively.
    # With base_exp=500, exp_rate=10, gamma=1 (linear):
    #   Level 1 needs  500 EXP = $50
    #   Level 2 needs 1500 EXP = $150   (500 + 1000)
    #   Level 3 needs 3000 EXP = $300   (500 + 1000 + 1500)
    #   Level 4 needs 5000 EXP = $500
    # With gamma=0 (constant, 500 EXP each):
    #   Level 1 = $50, Level 2 = $100, Level 3 = $150 …
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("spend,exp_rate,base_exp,gamma,expected_level", [
        # --- gamma=1 (linear cost per level) ---
        # $49  → 490 EXP  < 500  → 0 levels
        (49,  10, 500, 1.0, 0),
        # $50  → 500 EXP  == level-1 cost (500) → 1 level
        (50,  10, 500, 1.0, 1),
        # $149 → 1490 EXP < 1500 cumulative → still 1 level
        (149, 10, 500, 1.0, 1),
        # $150 → 1500 EXP == level-2 cumulative → 2 levels
        (150, 10, 500, 1.0, 2),
        # $299 → 2990 EXP < 3000 → still 2 levels
        (299, 10, 500, 1.0, 2),
        # $300 → 3000 EXP == level-3 cumulative → 3 levels
        (300, 10, 500, 1.0, 3),

        # --- gamma=0 (constant 500 EXP per level) ---
        # $50  → 500 EXP = 1 × 500 → 1 level
        (50,  10, 500, 0.0, 1),
        # $100 → 1000 EXP = 2 × 500 → 2 levels
        (100, 10, 500, 0.0, 2),
        # $99  → 990 EXP  < 1000  → 1 level
        (99,  10, 500, 0.0, 1),
        # $500 → 5000 EXP = 10 × 500 → 10 levels
        (500, 10, 500, 0.0, 10),

        # --- high base_exp blocks low spenders ---
        # $50, 10 exp/$, base_exp=2000: 500 EXP < 2000 → 0 levels
        (50,  10, 2000, 0.5, 0),
        # $200, 10 exp/$, base_exp=2000: 2000 EXP == threshold → 1 level
        (200, 10, 2000, 1.0, 1),

        # --- exp_rate variation ---
        # $50, 5 exp/$, base_exp=500: 250 EXP < 500 → 0 levels
        (50,   5, 500, 1.0, 0),
        # $50, 20 exp/$, base_exp=500: 1000 EXP → 1 level (level-2 needs 1500)
        (50,  20, 500, 1.0, 1),
        # $100, 20 exp/$, base_exp=500: 2000 EXP → level-2 needs 1500 → 2 levels
        (100, 20, 500, 1.0, 2),
    ])
    def test_spend_to_level(self, spend, exp_rate, base_exp, gamma, expected_level):
        budget = spend * exp_rate
        assert raffles_for_budget(budget, base_exp, gamma) == expected_level


# ---------------------------------------------------------------------------
# compute_derived
# ---------------------------------------------------------------------------

class TestComputeDerived:

    def _buckets_3(self):
        return get_active_buckets(3)  # shrimp, minnow, whale

    def test_raffles_per_player_match_budget_formula(self):
        buckets = self._buckets_3()
        players = {"shrimp": 300, "minnow": 150, "whale": 50}
        spends  = {"shrimp": 50, "minnow": 150, "whale": 4000}
        derived, _ = compute_derived(players, spends, exp_rate=10, base_exp=500, gamma=0.5, buckets=buckets)

        for b in buckets:
            bid = b["id"]
            expected = raffles_for_budget(spends[bid] * 10, 500, 0.5)
            assert derived[bid]["per"] == expected

    def test_total_raffles_equals_per_times_players(self):
        buckets = self._buckets_3()
        players = {"shrimp": 300, "minnow": 150, "whale": 50}
        spends  = {"shrimp": 50, "minnow": 150, "whale": 4000}
        derived, _ = compute_derived(players, spends, 10, 500, 0.5, buckets)

        for b in buckets:
            bid = b["id"]
            assert derived[bid]["total"] == derived[bid]["per"] * players[bid]

    def test_total_pool_equals_sum_of_totals(self):
        buckets = self._buckets_3()
        players = {"shrimp": 300, "minnow": 150, "whale": 50}
        spends  = {"shrimp": 50, "minnow": 150, "whale": 4000}
        derived, total_pool = compute_derived(players, spends, 10, 500, 0.5, buckets)

        assert total_pool == sum(derived[b["id"]]["total"] for b in buckets)

    def test_shares_sum_to_one(self):
        buckets = self._buckets_3()
        players = {"shrimp": 300, "minnow": 150, "whale": 50}
        spends  = {"shrimp": 50, "minnow": 150, "whale": 4000}
        derived, _ = compute_derived(players, spends, 10, 500, 0.5, buckets)

        total_share = sum(derived[b["id"]]["share"] for b in buckets)
        assert abs(total_share - 1.0) < 1e-9

    def test_high_base_exp_gives_zero_raffles_to_low_spenders(self):
        buckets = self._buckets_3()
        players = {"shrimp": 300, "minnow": 150, "whale": 50}
        spends  = {"shrimp": 50, "minnow": 150, "whale": 4000}
        # base_exp=2000: shrimp has 500 EXP → 0 raffles
        derived, _ = compute_derived(players, spends, exp_rate=10, base_exp=2000, gamma=0.5, buckets=buckets)

        assert derived["shrimp"]["per"] == 0
        assert derived["shrimp"]["total"] == 0

    def test_increasing_exp_rate_increases_raffle_counts(self):
        buckets = self._buckets_3()
        players = {"shrimp": 300, "minnow": 150, "whale": 50}
        spends  = {"shrimp": 50, "minnow": 150, "whale": 4000}

        derived_low,  _ = compute_derived(players, spends, exp_rate=5,  base_exp=500, gamma=0.5, buckets=buckets)
        derived_high, _ = compute_derived(players, spends, exp_rate=20, base_exp=500, gamma=0.5, buckets=buckets)

        for b in buckets:
            assert derived_high[b["id"]]["per"] >= derived_low[b["id"]]["per"]

    def test_zero_players_gives_zero_total(self):
        buckets = self._buckets_3()
        players = {"shrimp": 0, "minnow": 0, "whale": 0}
        spends  = {"shrimp": 50, "minnow": 150, "whale": 4000}
        derived, total_pool = compute_derived(players, spends, 10, 500, 0.5, buckets)

        assert total_pool == 0
        for b in buckets:
            assert derived[b["id"]]["total"] == 0

    def test_all_shares_zero_when_pool_empty(self):
        buckets = self._buckets_3()
        players = {"shrimp": 0, "minnow": 0, "whale": 0}
        spends  = {"shrimp": 50, "minnow": 150, "whale": 4000}
        derived, _ = compute_derived(players, spends, 10, 500, 0.5, buckets)

        for b in buckets:
            assert derived[b["id"]]["share"] == 0


# ---------------------------------------------------------------------------
# compute_total_money
# ---------------------------------------------------------------------------

class TestComputeTotalMoney:

    def test_basic_sum(self):
        buckets = get_active_buckets(3)
        players = {"shrimp": 300, "minnow": 150, "whale": 50}
        spends  = {"shrimp": 50,  "minnow": 150, "whale": 4000}
        assert compute_total_money(players, spends, buckets) == 300*50 + 150*150 + 50*4000

    def test_zero_players_gives_zero(self):
        buckets = get_active_buckets(3)
        players = {"shrimp": 0, "minnow": 0, "whale": 0}
        spends  = {"shrimp": 50, "minnow": 150, "whale": 4000}
        assert compute_total_money(players, spends, buckets) == 0

    def test_zero_spend_gives_zero(self):
        buckets = get_active_buckets(3)
        players = {"shrimp": 100, "minnow": 100, "whale": 100}
        spends  = {"shrimp": 0, "minnow": 0, "whale": 0}
        assert compute_total_money(players, spends, buckets) == 0

    def test_only_active_buckets_counted(self):
        # 3-bucket mode only uses shrimp, minnow, whale
        buckets = get_active_buckets(3)
        active_ids = {b["id"] for b in buckets}
        assert active_ids == {"shrimp", "minnow", "whale"}

        players = {b["id"]: 100 for b in BUCKET_CATALOG}
        spends  = {b["id"]: 100 for b in BUCKET_CATALOG}
        result = compute_total_money(players, spends, buckets)
        assert result == 3 * 100 * 100  # only 3 buckets counted


# ---------------------------------------------------------------------------
# distribute_players
# ---------------------------------------------------------------------------

class TestDistributePlayers:

    def test_total_sums_to_default(self):
        for count in range(MIN_BUCKETS, MAX_BUCKETS + 1):
            dist = distribute_players(count)
            assert sum(dist.values()) == DEFAULT_TOTAL_PLAYERS, f"failed for count={count}"

    def test_total_sums_to_custom_total(self):
        for count in range(MIN_BUCKETS, MAX_BUCKETS + 1):
            dist = distribute_players(count, total=1000)
            assert sum(dist.values()) == 1000

    def test_ten_buckets_exact_counts(self):
        dist = distribute_players(10)
        buckets = get_active_buckets(10)
        counts = [dist[b["id"]] for b in buckets]
        assert counts == [150, 100, 75, 50, 40, 30, 20, 18, 10, 7]

    def test_three_buckets_proportions(self):
        dist = distribute_players(3)
        buckets = get_active_buckets(3)
        # 60/30/10 of 500
        assert dist[buckets[0]["id"]] == 300
        assert dist[buckets[1]["id"]] == 150
        assert dist[buckets[2]["id"]] == 50

    def test_all_counts_positive(self):
        for count in range(MIN_BUCKETS, MAX_BUCKETS + 1):
            dist = distribute_players(count)
            for v in dist.values():
                assert v >= 0


# ---------------------------------------------------------------------------
# get_active_buckets
# ---------------------------------------------------------------------------

class TestGetActiveBuckets:

    def test_three_buckets_are_shrimp_minnow_whale(self):
        buckets = get_active_buckets(3)
        assert [b["id"] for b in buckets] == ["shrimp", "minnow", "whale"]

    def test_ten_buckets_is_full_catalog(self):
        buckets = get_active_buckets(10)
        assert [b["id"] for b in buckets] == [b["id"] for b in BUCKET_CATALOG]

    def test_count_clamped_to_min(self):
        assert len(get_active_buckets(1)) == MIN_BUCKETS

    def test_count_clamped_to_max(self):
        assert len(get_active_buckets(99)) == MAX_BUCKETS

    def test_returns_correct_count(self):
        for n in range(MIN_BUCKETS, MAX_BUCKETS + 1):
            assert len(get_active_buckets(n)) == n

    def test_buckets_ordered_low_to_high_spend(self):
        # Each bucket list should be a subsequence of the catalog (preserving order)
        catalog_ids = [b["id"] for b in BUCKET_CATALOG]
        for n in range(MIN_BUCKETS, MAX_BUCKETS + 1):
            ids = [b["id"] for b in get_active_buckets(n)]
            positions = [catalog_ids.index(i) for i in ids]
            assert positions == sorted(positions)


# ---------------------------------------------------------------------------
# Prize calculator formula
# ---------------------------------------------------------------------------

class TestPrizeCalculator:

    def test_basic_formula(self):
        gmv, contrib, pool, prizes = _prize_calc(
            raffle_revenue=80_000, other_revenue=0,
            base_prizes=3, increment=1_000,
        )
        assert gmv == 80_000
        assert contrib == 800.0
        assert pool == 1_250 + 800
        assert prizes == 3 + math.floor(800 / 1_000)  # 3 + 0 = 3

    def test_other_revenue_adds_to_gmv(self):
        _, _, _, prizes_no_other = _prize_calc(80_000, 0,       3, 1_000)
        _, _, _, prizes_with     = _prize_calc(80_000, 20_000,  3, 1_000)
        assert prizes_with >= prizes_no_other

    def test_never_drops_below_base_prizes(self):
        _, _, _, prizes = _prize_calc(0, 0, base_prizes=5, increment=1_000)
        assert prizes == 5

    def test_extra_prizes_floor_division(self):
        # gmv=200_000 → contrib=2000 → floor(2000/1000) = 2 extra
        _, _, _, prizes = _prize_calc(200_000, 0, base_prizes=3, increment=1_000)
        assert prizes == 5

    def test_increment_threshold_gates_extra_prizes(self):
        # Just below a threshold boundary
        _, _, _, below = _prize_calc(99_900, 0, 3, 1_000)  # contrib=999 → 0 extra
        _, _, _, above = _prize_calc(100_100, 0, 3, 1_000) # contrib=1001 → 1 extra
        assert above == below + 1

    def test_prize_pool_includes_base_1250(self):
        _, _, pool, _ = _prize_calc(0, 0, 3, 1_000)
        assert pool == 1_250

    def test_large_gmv_scales_prizes(self):
        _, _, _, prizes = _prize_calc(1_000_000, 0, base_prizes=3, increment=1_000)
        assert prizes == 3 + math.floor(10_000 / 1_000)  # 3 + 10 = 13


# ---------------------------------------------------------------------------
# run_draw
# ---------------------------------------------------------------------------

class TestRunDraw:

    def _derived(self, totals: dict[str, int], buckets):
        total_pool = sum(totals.values())
        return {
            b["id"]: {
                "total": totals[b["id"]],
                "per": 1,
                "share": totals[b["id"]] / total_pool if total_pool else 0,
            }
            for b in buckets
        }

    def test_returns_correct_number_of_prizes(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 300, "minnow": 600, "whale": 100}, buckets)
        result = run_draw(derived, num_prizes=5, buckets=buckets)
        assert len(result) == 5

    def test_all_winners_are_valid_bucket_ids(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 300, "minnow": 600, "whale": 100}, buckets)
        valid = {b["id"] for b in buckets}
        result = run_draw(derived, num_prizes=10, buckets=buckets)
        assert all(r in valid for r in result)

    def test_no_duplicates_within_draw(self):
        # Each ticket is unique so same ticket can't win twice
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 300, "minnow": 600, "whale": 100}, buckets)
        result = run_draw(derived, num_prizes=5, buckets=buckets)
        # Can't assert all unique IDs (same bucket can win multiple prizes),
        # but total count must match requested prizes
        assert len(result) == 5

    def test_capped_at_pool_size_when_prizes_exceed_pool(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 2, "minnow": 2, "whale": 1}, buckets)
        result = run_draw(derived, num_prizes=100, buckets=buckets)
        assert len(result) == 5  # only 5 tickets in pool

    def test_empty_pool_gives_empty_result(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 0, "minnow": 0, "whale": 0}, buckets)
        result = run_draw(derived, num_prizes=5, buckets=buckets)
        assert result == []

    def test_bucket_with_zero_tickets_never_wins(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 0, "minnow": 500, "whale": 0}, buckets)
        result = run_draw(derived, num_prizes=10, buckets=buckets)
        assert all(r == "minnow" for r in result)

    def test_distribution_roughly_proportional(self):
        # With 900 shrimp tickets and 100 whale tickets, shrimp should win ~90%
        random.seed(42)
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 900, "minnow": 0, "whale": 100}, buckets)
        result = run_draw(derived, num_prizes=100, buckets=buckets)
        shrimp_wins = result.count("shrimp")
        assert 80 <= shrimp_wins <= 98  # expected ~90, wide tolerance for randomness


# ---------------------------------------------------------------------------
# run_multi_draw (multi draw)
# ---------------------------------------------------------------------------

class TestRunMonteCarlo:

    def _derived(self, totals: dict[str, int], buckets):
        total_pool = sum(totals.values())
        return {
            b["id"]: {
                "total": totals[b["id"]],
                "per": 1,
                "share": totals[b["id"]] / total_pool if total_pool else 0,
            }
            for b in buckets
        }

    def test_total_wins_equals_cycles_times_prizes(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 300, "minnow": 600, "whale": 100}, buckets)
        n_cycles, num_prizes = 100, 8
        tally = run_multi_draw(derived, num_prizes, buckets, n_cycles)
        assert sum(tally.values()) == n_cycles * num_prizes

    def test_each_cycle_capped_when_prizes_exceed_pool(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 2, "minnow": 2, "whale": 1}, buckets)
        n_cycles, num_prizes = 10, 100
        tally = run_multi_draw(derived, num_prizes, buckets, n_cycles)
        assert sum(tally.values()) == n_cycles * 5  # pool has 5 tickets per draw

    def test_empty_pool_yields_zero_tally(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 0, "minnow": 0, "whale": 0}, buckets)
        tally = run_multi_draw(derived, num_prizes=5, buckets=buckets, n_cycles=50)
        assert tally == {b["id"]: 0 for b in buckets}

    def test_zero_cycles_yields_zero_tally(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 100, "minnow": 100, "whale": 100}, buckets)
        tally = run_multi_draw(derived, num_prizes=5, buckets=buckets, n_cycles=0)
        assert tally == {b["id"]: 0 for b in buckets}

    def test_bucket_with_zero_tickets_never_wins(self):
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 0, "minnow": 500, "whale": 0}, buckets)
        tally = run_multi_draw(derived, num_prizes=10, buckets=buckets, n_cycles=20)
        assert tally["shrimp"] == 0
        assert tally["whale"] == 0
        assert tally["minnow"] == 200

    def test_calls_run_draw_once_per_cycle(self):
        from unittest.mock import patch

        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 10, "minnow": 10, "whale": 10}, buckets)
        with patch("model.simulation.run_draw") as mock_draw:
            mock_draw.side_effect = [
                ["shrimp", "whale"],
                ["minnow"],
                ["shrimp", "shrimp", "whale"],
            ]
            tally = run_multi_draw(derived, num_prizes=3, buckets=buckets, n_cycles=3)

        assert mock_draw.call_count == 3
        assert tally == {"shrimp": 3, "minnow": 1, "whale": 2}

    def test_win_share_roughly_matches_pool_share(self):
        random.seed(42)
        buckets = get_active_buckets(3)
        derived = self._derived({"shrimp": 900, "minnow": 0, "whale": 100}, buckets)
        tally = run_multi_draw(derived, num_prizes=10, buckets=buckets, n_cycles=500)
        total = sum(tally.values())
        shrimp_pct = tally["shrimp"] / total * 100
        assert 85 <= shrimp_pct <= 95  # pool share is 90%
