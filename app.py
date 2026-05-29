import math
import streamlit as st

from model import get_active_buckets, compute_derived, compute_total_money, run_draw
from presentation import CSS, init_session_state, render_header, render_left_panel, render_right_panel, render_pool_bar, render_level_table

st.set_page_config(
    page_title="Raffle Prize Distribution Simulator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(CSS, unsafe_allow_html=True)

init_session_state()
ss = st.session_state

buckets = get_active_buckets(ss.bucket_count)
players = {
    b["id"]: ss[f"{b['id']}_players_inp"] if f"{b['id']}_players_inp" in ss else ss[f"{b['id']}_players"]
    for b in buckets
}
spends = {
    b["id"]: ss[f"{b['id']}_spend_inp"] if f"{b['id']}_spend_inp" in ss else ss[f"{b['id']}_spend"]
    for b in buckets
}
exp_rate = ss["exp_rate_inp"] if "exp_rate_inp" in ss else ss.exp_rate
base_exp = ss["base_exp_inp"] if "base_exp_inp" in ss else ss.base_exp
gamma    = min(1.0, ss["gamma_inp"] if "gamma_inp" in ss else ss.gamma)
derived, total_pool = compute_derived(players, spends, exp_rate, base_exp, gamma, buckets)
total_players = sum(players.values())
total_money = compute_total_money(players, spends, buckets)

if "prize_num_prizes" not in ss:
    _gmv = total_money + ss.other_revenue
    _extra = math.floor((_gmv * 0.01) / ss.prize_increment) if ss.prize_increment > 0 else 0
    ss.prize_num_prizes = max(ss.base_prizes, ss.base_prizes + _extra)


def handle_run_draw():
    ss.draw = run_draw(derived, ss.prize_num_prizes, buckets)


render_header()

left, _, right = st.columns([1.18, 0.15, 1], gap="small")

with left:
    render_left_panel(ss, derived, handle_run_draw, buckets)

with right:
    render_right_panel(ss, total_money)

render_pool_bar(derived, total_pool, total_players, total_money, buckets)
render_level_table(ss.gamma, ss.base_exp)
