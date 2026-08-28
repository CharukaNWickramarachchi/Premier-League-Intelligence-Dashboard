"""Shared sidebar filter widgets. Selections are written to st.session_state
so every page reads the same filter context without re-prompting the user."""
from __future__ import annotations

from typing import List, Tuple

import pandas as pd
import streamlit as st


def init_filter_state(df: pd.DataFrame) -> None:
    if "filters_initialized" in st.session_state:
        return
    st.session_state["season_range"] = (
        df["SeasonLabel"].iloc[0],
        df["SeasonLabel"].iloc[-1],
    )
    st.session_state["selected_teams"] = []
    st.session_state["filters_initialized"] = True


def global_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render season + team filters in the sidebar and return the filtered
    dataframe. Call once per page near the top."""
    init_filter_state(df)

    st.sidebar.markdown("### 🔎 Global Filters")

    seasons_sorted = (
        df[["SeasonLabel", "SeasonSortKey"]]
        .drop_duplicates()
        .sort_values("SeasonSortKey")["SeasonLabel"]
        .tolist()
    )
    season_choice: Tuple[str, str] = st.sidebar.select_slider(
        "Season range",
        options=seasons_sorted,
        value=(seasons_sorted[0], seasons_sorted[-1]),
        key="season_range_slider",
    )

    all_teams = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))
    selected_teams: List[str] = st.sidebar.multiselect(
        "Teams (leave empty = all teams)",
        options=all_teams,
        default=[],
        key="team_multiselect",
    )

    start_idx = seasons_sorted.index(season_choice[0])
    end_idx = seasons_sorted.index(season_choice[1])
    active_seasons = set(seasons_sorted[start_idx : end_idx + 1])

    filtered = df[df["SeasonLabel"].isin(active_seasons)]
    if selected_teams:
        filtered = filtered[
            filtered["HomeTeam"].isin(selected_teams) | filtered["AwayTeam"].isin(selected_teams)
        ]

    st.sidebar.caption(f"{len(filtered):,} of {len(df):,} matches match current filters.")
    return filtered
