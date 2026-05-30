import math
import streamlit as st

from model.constants import (
    BUCKET_CATALOG,
    DEFAULT_SPEND,
    MIN_BUCKETS,
    MAX_BUCKETS,
    apply_default_player_distribution,
)
from presentation.charts import curve_svg
from presentation.formatters import fmt


def init_session_state():
    ss = st.session_state
    if "num_prizes" not in ss:
        ss.num_prizes = 8
    if "gamma" not in ss:
        ss.gamma = 0.5
    if "exp_rate" not in ss:
        ss.exp_rate = 10
    if "base_exp" not in ss:
        ss.base_exp = 500
    if "draw" not in ss:
        ss.draw = None
    if "monte_carlo" not in ss:
        ss.monte_carlo = None
    if "monte_carlo_n" not in ss:
        ss.monte_carlo_n = 1
    if "show_model" not in ss:
        ss.show_model = False
    if "bucket_count" not in ss:
        ss.bucket_count = 3
    if "prize_increment" not in ss:
        ss.prize_increment = 1000
    if "other_revenue" not in ss:
        ss.other_revenue = 0
    if "base_prizes" not in ss:
        ss.base_prizes = 3
    if "players_initialized" not in ss:
        apply_default_player_distribution(ss)
        ss.players_initialized = True
    for b in BUCKET_CATALOG:
        bid = b["id"]
        if f"{bid}_spend" not in ss:
            ss[f"{bid}_spend"] = DEFAULT_SPEND[bid]


def render_header():
    st.markdown("""
<div style="text-align:center;margin:0 4px 20px">
  <h1 style="font-size:19px;font-weight:700;letter-spacing:-0.01em;margin:0;color:#ededed">
    Raffle Prize Distribution Simulator
  </h1>
</div>
""", unsafe_allow_html=True)


def _render_bucket(ss, derived, b, compact: bool = False):
    bid = b["id"]
    d = derived[bid]

    ring_html = (
        f'<div class="bk-head" style="background:{b["bg"]}">'
        f'  <span class="bk-ring" style="color:{b["ac"]}"><span style="'
        f'    width:7px;height:7px;border-radius:50%;background:{b["ac"]};'
        f'    display:inline-block"></span></span>'
        f'  <span class="bk-name" style="color:{b["tx"]}">{b["name"]}</span>'
        f'  <span style="margin-left:auto">'
        f'    <span style="color:{b["ac"]};font-size:12px;font-weight:700;opacity:.9">reaches Lv.&nbsp;{d["per"]}</span>'
        f'  </span>'
        f'</div>'
    )
    st.markdown(f'<div class="bucket">{ring_html}</div>', unsafe_allow_html=True)

    if compact:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.markdown('<span class="clbl">Players</span>', unsafe_allow_html=True)
            ss[f"{bid}_players"] = st.number_input(
                "players", min_value=0, value=ss[f"{bid}_players"],
                label_visibility="collapsed", key=f"{bid}_players_inp",
            )
        with c2:
            st.markdown('<span class="clbl">$/player</span>', unsafe_allow_html=True)
            ss[f"{bid}_spend"] = st.number_input(
                "spend", min_value=0, value=ss[f"{bid}_spend"],
                label_visibility="collapsed", key=f"{bid}_spend_inp",
            )
        with c3:
            st.markdown(
                f'<div style="padding:6px 0;text-align:center">'
                f'  <div class="clbl">Total raffles</div>'
                f'  <div class="dval" style="color:{b["ac"]};font-size:20px;font-weight:700">{fmt(d["total"])}</div>'
                f'  <div class="deq" style="font-size:10px;color:#5e5e5e;font-family:monospace">'
                f'    {fmt(ss[f"{bid}_players"])} × {fmt(d["per"])}'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1.05])
        with c1:
            st.markdown('<span class="clbl">Player Count</span>', unsafe_allow_html=True)
            ss[f"{bid}_players"] = st.number_input(
                "players", min_value=0, value=ss[f"{bid}_players"],
                label_visibility="collapsed", key=f"{bid}_players_inp",
            )
        with c2:
            st.markdown('<span class="clbl">Spend Per Player ($)</span>', unsafe_allow_html=True)
            ss[f"{bid}_spend"] = st.number_input(
                "spend", min_value=0, value=ss[f"{bid}_spend"],
                label_visibility="collapsed", key=f"{bid}_spend_inp",
            )
        with c3:
            st.markdown(
                f'<div style="padding:6px 0;text-align:center">'
                f'  <div class="clbl">Raffles Per Player</div>'
                f'  <div class="dval" style="color:{b["ac"]};font-size:26px;font-weight:700">{fmt(d["per"])}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f'<div style="padding:6px 0;text-align:center">'
                f'  <div class="clbl">Total raffles</div>'
                f'  <div class="dval" style="color:{b["ac"]};font-size:26px;font-weight:700">{fmt(d["total"])}</div>'
                f'  <div class="deq" style="font-size:11px;color:#5e5e5e;font-family:monospace">'
                f'    {fmt(ss[f"{bid}_players"])} × {fmt(d["per"])}'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        "<hr style='border:none;border-top:1px solid #2c2c2c;margin:0 0 10px'>",
        unsafe_allow_html=True,
    )


def render_left_panel(ss, derived, on_run_draw, on_run_monte_carlo, buckets):
    kicker_col, counter_col = st.columns([5, 1])
    with kicker_col:
        st.markdown(
            '<div class="kicker" style="padding-top:8px;margin-bottom:0">Player Buckets</div>',
            unsafe_allow_html=True,
        )
    with counter_col:
        btn_minus, count_mid, btn_plus = st.columns([1, 1, 1])
        with btn_minus:
            st.markdown('<span class="counter-btn-minus"></span>', unsafe_allow_html=True)
            if st.button("−", key="bucket_minus", disabled=ss.bucket_count <= MIN_BUCKETS):
                ss.bucket_count = max(MIN_BUCKETS, ss.bucket_count - 1)
                apply_default_player_distribution(ss)
                ss.draw = None
                st.rerun()
        with count_mid:
            st.markdown(
                f'<div style="text-align:center;padding-top:3px;font-size:14px;'
                f'font-weight:700;color:#ededed">{ss.bucket_count}</div>',
                unsafe_allow_html=True,
            )
        with btn_plus:
            st.markdown('<span class="counter-btn-plus"></span>', unsafe_allow_html=True)
            if st.button("+", key="bucket_plus", disabled=ss.bucket_count >= MAX_BUCKETS):
                ss.bucket_count = min(MAX_BUCKETS, ss.bucket_count + 1)
                apply_default_player_distribution(ss)
                ss.draw = None
                st.rerun()

    st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)

    compact = len(buckets) > 5
    if compact:
        mid = 5
        grid_left, grid_right = st.columns(2)
        with grid_left:
            for b in buckets[:mid]:
                _render_bucket(ss, derived, b, compact=True)
        with grid_right:
            for b in buckets[mid:]:
                _render_bucket(ss, derived, b, compact=True)
    else:
        for b in buckets:
            _render_bucket(ss, derived, b, compact=False)

    st.markdown(
        '<div style="border-top:1px solid #2c2c2c;margin-top:26px;padding-top:26px">'
        '  <div style="display:flex;justify-content:space-between;align-items:center">'
        '    <span class="kicker" style="margin:0">Draw Results</span>',
        unsafe_allow_html=True,
    )

    if st.button("▶  Run Draw", key="run_draw_btn", type="primary",
                 help="Run the Monte-Carlo prize draw"):
        on_run_draw()

    st.markdown('</div>', unsafe_allow_html=True)

    draw = ss.draw
    if draw is None:
        st.markdown(
            f'<p style="color:#5e5e5e;font-size:14px;margin-top:12px">'
            f'Hit "Run draw" to simulate {fmt(ss.prize_num_prizes)} prize{"s" if ss.prize_num_prizes != 1 else ""}.'
            f'</p>',
            unsafe_allow_html=True,
        )
    else:
        tally = {b["id"]: 0 for b in buckets}
        for bid in draw:
            tally[bid] += 1

        rows = "".join(
            f'<tr>'
            f'  <td style="display:flex;align-items:center;gap:8px;padding:7px 0">'
            f'    <span style="width:9px;height:9px;border-radius:50%;background:{b["ac"]};flex-shrink:0;display:inline-block"></span>'
            f'    <span style="color:#aeaeae;font-size:13px">{b["name"]}</span>'
            f'  </td>'
            f'  <td style="text-align:right;padding:7px 0;font-size:14px;font-weight:700;color:{b["ac"]}">'
            f'    {tally[b["id"]]}'
            f'  </td>'
            f'</tr>'
            for b in buckets if tally[b["id"]] > 0
        )
        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;margin-top:10px">'
            f'  <thead><tr>'
            f'    <th style="text-align:left;font-size:10.5px;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:#5e5e5e;padding-bottom:6px">Bucket</th>'
            f'    <th style="text-align:right;font-size:10.5px;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:#5e5e5e;padding-bottom:6px">Number Of Winners</th>'
            f'  </tr></thead>'
            f'  <tbody style="border-top:1px solid #2c2c2c">{rows}</tbody>'
            f'</table>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Monte Carlo section
    st.markdown(
        '<div style="border-top:1px solid #2c2c2c;margin-top:26px;padding-top:26px">'
        '  <div style="display:flex;justify-content:space-between;align-items:center">'
        '    <span class="kicker" style="margin:0">Monte Carlo Simulation</span>',
        unsafe_allow_html=True,
    )

    mc_col_btn, mc_col_input = st.columns([2, 1])
    with mc_col_btn:
        st.markdown('<span class="clbl">&nbsp;</span>', unsafe_allow_html=True)
        if st.button("▶  Run Multi Draw", key="run_mc_btn", type="primary",
                     help="Run the draw N times and tally results"):
            on_run_monte_carlo()
    with mc_col_input:
        st.markdown('<span class="clbl">Draws</span>', unsafe_allow_html=True)
        ss.monte_carlo_n = st.number_input(
            "Number of draws",
            min_value=1,
            max_value=1000,
            value=ss.monte_carlo_n,
            label_visibility="collapsed",
            key="monte_carlo_n_inp",
        )

    st.markdown('</div>', unsafe_allow_html=True)

    mc = ss.monte_carlo
    if mc is None:
        st.markdown(
            '<p style="color:#5e5e5e;font-size:14px;margin-top:12px">'
            'Set the number of draws and hit "Run Monte Carlo" to simulate multiple prize draws.'
            '</p>',
            unsafe_allow_html=True,
        )
    else:
        total_wins = sum(mc.values())
        mc_rows = "".join(
            f'<tr>'
            f'  <td style="display:flex;align-items:center;gap:8px;padding:7px 0">'
            f'    <span style="width:9px;height:9px;border-radius:50%;background:{b["ac"]};flex-shrink:0;display:inline-block"></span>'
            f'    <span style="color:#aeaeae;font-size:13px">{b["name"]}</span>'
            f'  </td>'
            f'  <td style="text-align:right;padding:7px 0;font-size:14px;font-weight:700;color:{b["ac"]}">'
            f'    {mc[b["id"]]}'
            f'  </td>'
            f'  <td style="text-align:right;padding:7px 0;font-size:12px;color:#5e5e5e;font-family:monospace">'
            f'    {mc[b["id"]] / total_wins * 100:.1f}%'
            f'  </td>'
            f'</tr>'
            for b in buckets if mc[b["id"]] > 0
        )
        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;margin-top:10px">'
            f'  <thead><tr>'
            f'    <th style="text-align:left;font-size:10.5px;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:#5e5e5e;padding-bottom:6px">Bucket</th>'
            f'    <th style="text-align:right;font-size:10.5px;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:#5e5e5e;padding-bottom:6px">Total Wins</th>'
            f'    <th style="text-align:right;font-size:10.5px;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;color:#5e5e5e;padding-bottom:6px">Win %</th>'
            f'  </tr></thead>'
            f'  <tbody style="border-top:1px solid #2c2c2c">{mc_rows}</tbody>'
            f'</table>'
            f'<p style="color:#5e5e5e;font-size:11px;margin-top:8px">'
            f'  {ss.monte_carlo_n} draw{"s" if ss.monte_carlo_n != 1 else ""} × {fmt(ss.prize_num_prizes)} prizes = {fmt(total_wins)} total wins'
            f'</p>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


def _slider_label_style(active: str, name: str) -> str:
    color = "#ededed" if active == name else "#5e5e5e"
    weight = "600" if active == name else "400"
    return f'<span style="color:{color};font-weight:{weight};font-size:12px">{name}</span>'


def _sync_gamma_from_input():
    ss = st.session_state
    ss.gamma = min(1.0, round(float(ss.gamma_inp), 2))
    ss.gamma_slider = ss.gamma


def _sync_gamma_from_slider():
    ss = st.session_state
    ss.gamma = min(1.0, round(float(ss.gamma_slider), 2))
    ss.gamma_inp = ss.gamma

def _render_prize_calculator(ss, total_money: int):
    st.markdown('<div class="kicker" style="margin-bottom:10px">Prize Calculator</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        ss.base_prizes = st.number_input(
            "Base Prizes", min_value=1, value=ss.base_prizes, key="base_prizes_inp",
        )
    with c2:
        ss.prize_increment = st.number_input(
            "Affordability Ceiling ($)", min_value=1, value=ss.prize_increment, key="prize_increment_inp",
        )
    with c3:
        ss.other_revenue = st.number_input(
            "Other Revenue ($)", min_value=0, value=ss.other_revenue, key="other_revenue_inp",
        )

    raffle_revenue   = total_money
    cumulative_gmv   = raffle_revenue + ss.other_revenue
    gmv_contribution = cumulative_gmv * 0.01
    prize_pool       = 1_250 + gmv_contribution
    extra_prizes     = math.floor(gmv_contribution / ss.prize_increment) if ss.prize_increment > 0 else 0
    num_prizes       = max(ss.base_prizes, ss.base_prizes + extra_prizes)
    ss.prize_num_prizes = num_prizes

    row = "display:flex;justify-content:space-between;align-items:baseline;margin:5px 0"
    lbl = "font-size:12px;color:#7d7d7d"
    val = "font-size:12px;color:#5e5e5e;font-family:monospace"
    hi  = "color:#ededed;font-weight:700"

    st.markdown(
        f'<div style="margin-top:14px">'

        f'  <div style="{row}">'
        f'    <span style="{lbl}">Raffle revenue</span>'
        f'    <span style="{val}">${fmt(raffle_revenue)}</span>'
        f'  </div>'

        f'  <div style="{row}">'
        f'    <span style="{lbl}">Other revenue</span>'
        f'    <span style="{val}">+ ${fmt(ss.other_revenue)}</span>'
        f'  </div>'

        f'  <div style="border-top:1px solid #2c2c2c;margin:8px 0"></div>'

        f'  <div style="{row}">'
        f'    <span style="{lbl}">Cumulative GMV</span>'
        f'    <span style="{val}"><span style="{hi}">${fmt(cumulative_gmv)}</span></span>'
        f'  </div>'

        f'  <div style="{row}">'
        f'    <span style="{lbl}">1% of GMV → prize pool</span>'
        f'    <span style="{val}">$1,250 + (${fmt(cumulative_gmv)} × 1%) = <span style="{hi}">${fmt(prize_pool)}</span></span>'
        f'  </div>'

        f'  <div style="border-top:1px solid #2c2c2c;margin:8px 0"></div>'

        f'  <div style="{row}">'
        f'    <span style="{lbl}">Prizes</span>'
        f'    <span style="{val}">'
        f'      {ss.base_prizes} + floor(${fmt(gmv_contribution)} / ${fmt(ss.prize_increment)}) = '
        f'      <span style="{hi}">{num_prizes} prizes</span>'
        f'    </span>'
        f'  </div>'

        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<hr style="border:none;border-top:1px solid #2c2c2c;margin:18px 0">',
        unsafe_allow_html=True,
    )


def render_right_panel(ss, total_money: int):
    _render_prize_calculator(ss, total_money)

    ss.setdefault("gamma_slider", float(ss.gamma))
    ss.setdefault("gamma_inp", float(ss.gamma))

    title_col, gamma_col = st.columns([2.5, 1])
    with title_col:
        st.markdown(
            '<div class="kicker" style="margin-bottom:0;padding-top:6px">XP Threshold Curve</div>',
            unsafe_allow_html=True,
        )
    with gamma_col:
        st.number_input(
            "γ",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            format="%.2f",
            key="gamma_inp",
            on_change=_sync_gamma_from_input,
        )

    slider_active = "Constant" if ss.gamma < 0.1 else "Linear"

    st.markdown(
        '<span style="font-size:17px;font-weight:600;color:#aeaeae">'
        'EXP Threshold Curve Shape </em></span>',
        unsafe_allow_html=True,
    )

    st.slider(
        "γ", min_value=0.0, max_value=1.0,
        step=0.01, label_visibility="collapsed", key="gamma_slider",
        on_change=_sync_gamma_from_slider,
    )

    st.markdown(
        f'<div style="display:flex;justify-content:space-between;margin-top:4px">'
        f'  {_slider_label_style(slider_active, "Constant")}'
        f'  {_slider_label_style(slider_active, "Linear")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="text-align:center;margin:16px 0 14px">'
        '  <div style="font-size:22px;font-weight:700;color:#ededed;'
        '              font-family:\'Spline Sans Mono\',monospace;letter-spacing:-0.01em">'
        '    baseEXP × n<sup style="font-size:0.75em">γ</sup>'
        '  </div>'
        '</div>'
        '<div style="font-size:12.5px;color:#7d7d7d;line-height:1.65;margin-bottom:10px">'
        '  <p style="margin:0 0 8px">'
        '    <strong style="color:#aeaeae">baseEXP</strong> — '
        '    The EXP threshold at level&nbsp;1; the starting cost before level scaling is applied.'
        '  </p>'
        '  <p style="margin:0 0 8px">'
        '    <strong style="color:#aeaeae">n</strong> — '
        '    The player\'s current level.'
        '  </p>'
        '  <p style="margin:0">'
        '    <strong style="color:#aeaeae">γ</strong> — '
        '    The growth exponent. Controls how quickly the EXP threshold rises each level — '
        '    flat at&nbsp;0, linear at&nbsp;1, and increasingly steep above&nbsp;1.'
        '  </p>'
        '</div>',
        unsafe_allow_html=True,
    )
    ec1, ec2 = st.columns(2)
    with ec1:
        ss.exp_rate = st.number_input(
            "EXP per $1", min_value=1, value=ss.exp_rate, key="exp_rate_inp"
        )
    with ec2:
        ss.base_exp = round(st.number_input(
            "Initial EXP Threshold",
            min_value=0.01,
            value=float(ss.base_exp),
            step=0.01,
            format="%.2f",
            key="base_exp_inp",
        ), 2)

    st.markdown('<div class="kicker" style="margin-top:20px">EXP Cost Per Ticket Level</div>', unsafe_allow_html=True)
    st.markdown(curve_svg(ss.gamma, ss.base_exp), unsafe_allow_html=True)


def render_level_table(gamma: float, base_exp: float):
    def _f(v: float) -> str:
        return f"{v:,.0f}"

    levels = list(range(1, 51))
    costs  = [base_exp * (n ** gamma) for n in levels]

    groups_html = ""
    for g in range(5):
        rows = "".join(
            f'<tr><td>{levels[i]}</td><td>{_f(costs[i])}</td></tr>'
            for i in range(g * 10, g * 10 + 10)
        )
        groups_html += (
            f'<div>'
            f'  <table class="level-table">'
            f'    <thead><tr><th>Lvl</th><th>EXP Threshold</th></tr></thead>'
            f'    <tbody>{rows}</tbody>'
            f'  </table>'
            f'</div>'
        )

    st.markdown(
        f'<div style="border-top:1px solid #2c2c2c;margin-top:28px;padding-top:22px">'
        f'  <div class="kicker" style="margin-bottom:14px">EXP Threshold by Level</div>'
        f'  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:20px">'
        f'    {groups_html}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_pool_bar(derived, total_pool, total_players, total_money, buckets):
    segs = "".join(
        f'<div class="pool-seg" style="flex-grow:{max(derived[b["id"]]["share"], 0.001)};background:{b["ac"]}"></div>'
        for b in buckets
    )
    legend = "".join(
        f'<span class="pl">'
        f'  <span class="dot" style="background:{b["ac"]}"></span>'
        f'  {b["name"]} <b>{derived[b["id"]]["share"]*100:.1f}%</b>'
        f'</span>'
        for b in buckets
    )
    st.markdown(
        f'<div style="border-top:1px solid #2c2c2c;margin-top:28px;padding-top:22px">'
        f'  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:12px">'
        f'    <span style="font-size:15px;font-weight:600;color:#aeaeae">Total ticket pool</span>'
        f'    <div style="display:flex;gap:28px;align-items:baseline">'
        f'      <span style="font-size:16px;font-weight:600;color:#7d7d7d">'
        f'        {fmt(total_players)}'
        f'        <small style="font-size:12px;font-weight:400"> players</small>'
        f'      </span>'
        f'      <span style="font-size:19px;font-weight:700;color:#ededed">'
        f'        {fmt(total_pool)}'
        f'        <small style="color:#7d7d7d;font-size:13px;font-weight:400"> raffles</small>'
        f'      </span>'
        f'      <span style="font-size:19px;font-weight:700;color:#ededed">'
        f'        ${fmt(total_money)}'
        f'        <small style="color:#7d7d7d;font-size:13px;font-weight:400"> in circulation</small>'
        f'      </span>'
        f'    </div>'
        f'  </div>'
        f'  <div class="pool-bar">{segs}</div>'
        f'  <div class="pool-legend" style="margin-top:10px">{legend}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
