"""
Premier League Intelligence — main entry point / Home Dashboard.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from components.filters import global_filters
from components.kpi_cards import kpi_grid
from utils.data_loader import get_full_dataset, compute_all_time_table
from utils.reference_data import get_competition_logo_path
from utils.theme import hero, inject_css, insight_box, section_title
from utils import viz

st.set_page_config(
    page_title="Premier League Intelligence",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

_pl_logo = get_competition_logo_path()
if _pl_logo:
    logo_col, _ = st.columns([1, 6])
    with logo_col:
        st.image(_pl_logo, use_container_width=True)


@st.cache_data(show_spinner=False)
def _load():
    return get_full_dataset()


try:
    df = _load()
except Exception as e:  # noqa: BLE001
    st.error(
        "Couldn't load `data/matches_clean.csv`. Make sure the file exists in the "
        f"`data/` folder next to app.py.\n\nDetails: {e}"
    )
    st.stop()

hero(
    "Premier League Intelligence",
    "A full analytics, machine-learning and simulation suite built on 25+ seasons "
    "of Premier League match data — explore form, ratings, predictions and more.",
)

filtered = global_filters(df)

# ---------------------------------------------------------------------- #
# KPI row
# ---------------------------------------------------------------------- #
section_title("League Snapshot")

total_matches = len(filtered)
total_goals = int(filtered["TotalGoals"].sum())
home_win_pct = (filtered["FTR"] == "H").mean() * 100 if total_matches else 0
away_win_pct = (filtered["FTR"] == "A").mean() * 100 if total_matches else 0
draw_pct = (filtered["FTR"] == "D").mean() * 100 if total_matches else 0
avg_goals = filtered["TotalGoals"].mean() if total_matches else 0
n_seasons = filtered["season"].nunique()
n_teams = len(set(filtered["HomeTeam"]) | set(filtered["AwayTeam"]))

if total_matches:
    top_match = filtered.loc[filtered["TotalGoals"].idxmax()]
    top_match_str = (
        f"{top_match['HomeTeam']} {int(top_match['FTHG'])}-{int(top_match['FTAG'])} "
        f"{top_match['AwayTeam']}"
    )
else:
    top_match_str = "—"

kpi_grid(
    [
        ("Total Matches", f"{total_matches:,}", None),
        ("Total Goals", f"{total_goals:,}", None),
        ("Home Win %", f"{home_win_pct:.1f}%", None),
        ("Away Win %", f"{away_win_pct:.1f}%", None),
        ("Draw %", f"{draw_pct:.1f}%", None),
        ("Avg Goals / Match", f"{avg_goals:.2f}", None),
        ("Seasons Covered", f"{n_seasons}", None),
        ("Teams Involved", f"{n_teams}", None),
    ],
    columns=4,
)

st.markdown(
    f'<div class="pli-card" style="margin-top:0.8rem;">🔥 <b>Highest scoring match in current filter:</b> {top_match_str}</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------- #
# Headline charts
# ---------------------------------------------------------------------- #
section_title("Trends at a Glance")
c1, c2 = st.columns([1.3, 1])
with c1:
    st.plotly_chart(viz.goals_timeline(filtered), use_container_width=True)
    insight_box(
        "Average goals per match fluctuates season to season but has generally "
        "trended upward since 2015 as pressing, transition football and set-piece "
        "coaching have matured league-wide."
    )
with c2:
    st.plotly_chart(viz.result_pie(filtered), use_container_width=True)
    insight_box(
        "Home advantage is real but shrinking over the dataset's history — "
        "look at the Head-to-Head and Team Analytics pages to see it broken down by team."
    )

st.plotly_chart(viz.animated_goals_trend(filtered), use_container_width=True)

# ---------------------------------------------------------------------- #
# All-time table preview
# ---------------------------------------------------------------------- #
section_title("All-Time Table (current filter)")
all_time = compute_all_time_table(filtered)
st.dataframe(all_time.head(10), use_container_width=True)
st.caption("Full table, per-season tables, and exports are available on the League Analytics and Downloads pages.")

st.markdown(
    """
    <div class="pli-card" style="margin-top:1rem;">
    <b>Navigate using the sidebar</b> — Match Explorer, Team Analytics, League Analytics,
    Head-to-Head, Prediction Center, AI Insights, Statistics, Downloads, Settings and About.
    </div>
    """,
    unsafe_allow_html=True,
)

