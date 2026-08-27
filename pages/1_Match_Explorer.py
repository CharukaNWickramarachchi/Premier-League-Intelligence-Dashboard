"""Match Explorer — searchable, filterable table of every match with a
detail drill-down for any single fixture."""
from __future__ import annotations

import streamlit as st

from components.filters import global_filters
from utils.data_loader import get_full_dataset
from utils.theme import hero, inject_css, insight_box, section_title

st.set_page_config(page_title="Match Explorer — PLI", page_icon="🔍", layout="wide")
inject_css()
hero("Match Explorer", "Search, filter and drill into any Premier League fixture on record.")

df = get_full_dataset()
filtered = global_filters(df)

section_title("Filters")
c1, c2, c3 = st.columns(3)
with c1:
    result_filter = st.multiselect("Result", ["H", "D", "A"], default=["H", "D", "A"],
                                    format_func=lambda x: {"H": "Home Win", "D": "Draw", "A": "Away Win"}[x])
with c2:
    min_goals, max_goals = int(filtered["TotalGoals"].min()), int(filtered["TotalGoals"].max())
    goal_range = st.slider("Total goals in match", min_goals, max_goals, (min_goals, max_goals))
with c3:
    search_team = st.text_input("Search team name contains…", "")

view = filtered[
    filtered["FTR"].isin(result_filter)
    & filtered["TotalGoals"].between(goal_range[0], goal_range[1])
]
if search_team:
    mask = view["HomeTeam"].str.contains(search_team, case=False) | view["AwayTeam"].str.contains(
        search_team, case=False
    )
    view = view[mask]

section_title(f"Matches ({len(view):,})")
display_cols = [
    "Date", "SeasonLabel", "HomeTeam", "FTHG", "FTAG", "AwayTeam", "FTR",
    "HS", "AS", "HST", "AST", "HC", "AC", "HY", "AY", "HR", "AR", "Referee",
]
display_cols = [c for c in display_cols if c in view.columns]
st.dataframe(
    view[display_cols].sort_values("Date", ascending=False),
    use_container_width=True,
    height=420,
)

section_title("Match Detail Drill-Down")
if len(view):
    view = view.sort_values("Date", ascending=False).reset_index(drop=True)
    labels = [
        f"{r.Date.date()} — {r.HomeTeam} {int(r.FTHG)}-{int(r.FTAG)} {r.AwayTeam}"
        for r in view.itertuples()
    ]
    choice = st.selectbox("Pick a match", options=list(range(len(view))), format_func=lambda i: labels[i])
    match = view.iloc[choice]

    m1, m2, m3 = st.columns(3)
    m1.metric(match["HomeTeam"], int(match["FTHG"]))
    m2.metric("Result", {"H": "Home Win", "D": "Draw", "A": "Away Win"}[match["FTR"]])
    m3.metric(match["AwayTeam"], int(match["FTAG"]))

    stat_pairs = [
        ("Shots", "HS", "AS"), ("Shots on Target", "HST", "AST"),
        ("Corners", "HC", "AC"), ("Fouls", "HF", "AF"),
        ("Yellow Cards", "HY", "AY"), ("Red Cards", "HR", "AR"),
    ]
    rows = []
    for label, hcol, acol in stat_pairs:
        if hcol in match and acol in match:
            rows.append({"Stat": label, match["HomeTeam"]: match[hcol], match["AwayTeam"]: match[acol]})
    if rows:
        import pandas as pd
        st.dataframe(pd.DataFrame(rows).set_index("Stat"), use_container_width=True)

    insight_box(
        f"Half-time score was {int(match.get('HTHG', 0))}-{int(match.get('HTAG', 0))}. "
        f"Pre-match Elo: {match['HomeTeam']} {match['EloHome']:.0f} vs {match['AwayTeam']} {match['EloAway']:.0f} "
        f"(gap of {abs(match['EloDiff']):.0f} points)."
    )
else:
    st.info("No matches found for the current filters.")
