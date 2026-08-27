"""League Analytics — season tables, all-time table, treemaps/sunbursts of
goals, and league-wide trend charts."""
from __future__ import annotations

import streamlit as st

from utils.data_loader import compute_all_time_table, compute_season_table, get_full_dataset, get_season_list
from utils.theme import hero, inject_css, insight_box, section_title
from utils import viz

st.set_page_config(page_title="League Analytics — PLI", page_icon="🏆", layout="wide")
inject_css()
hero("League Analytics", "Season-by-season tables, all-time standings and league-wide statistical patterns.")

df = get_full_dataset()
seasons = get_season_list(df)

tab1, tab2, tab3 = st.tabs(["📅 Season Table", "🏛️ All-Time Table", "🌳 Goal Distribution"])

with tab1:
    season_choice = st.selectbox("Season", seasons, index=len(seasons) - 1,
                                  format_func=lambda s: s.replace("season_", "").replace("_", "/"))
    table = compute_season_table(df, season_choice)
    st.dataframe(table, use_container_width=True, height=460)

    top_scorer_match = df[df["season"] == season_choice]
    if len(top_scorer_match):
        best = top_scorer_match.loc[top_scorer_match["TotalGoals"].idxmax()]
        insight_box(
            f"Highest scoring match of the season: {best['HomeTeam']} {int(best['FTHG'])}-{int(best['FTAG'])} "
            f"{best['AwayTeam']} on {best['Date'].date()}."
        )

with tab2:
    all_time = compute_all_time_table(df)
    st.dataframe(all_time, use_container_width=True, height=600)
    insight_box(
        "PPG (points per game) is a fairer cross-era comparison than total points, since clubs "
        "have played a very different number of seasons in this dataset."
    )
    st.plotly_chart(
        viz.bubble_chart(all_time.reset_index(), x="GF", y="GA", size="Pld", color="PPG",
                          hover_name="Team", title="Goals For vs Against (bubble size = matches played)"),
        use_container_width=True,
    )

with tab3:
    season_goal_totals = df.groupby(["SeasonLabel", "HomeTeam"])["FTHG"].sum().reset_index()
    season_goal_totals = season_goal_totals.rename(columns={"HomeTeam": "Team", "FTHG": "Goals"})
    st.plotly_chart(
        viz.treemap_by(season_goal_totals, ["SeasonLabel", "Team"], "Goals", "Home Goals by Season & Team"),
        use_container_width=True,
    )
    st.plotly_chart(
        viz.sunburst_by(season_goal_totals, ["SeasonLabel", "Team"], "Goals", "Home Goals — Sunburst View"),
        use_container_width=True,
    )
    insight_box("Treemap tile size and sunburst wedge size both encode total home goals scored — bigger means more prolific at home.")

section_title("League-Wide Trend")
st.plotly_chart(viz.animated_goals_trend(df), use_container_width=True)
