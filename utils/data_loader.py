"""
Data loading, cleaning and feature engineering for Premier League Intelligence.

Everything here is pure pandas/numpy so it can be unit tested outside of
Streamlit. Streamlit-specific caching wrappers live at the bottom of the
module.
"""
from __future__ import annotations

import os
from typing import Dict, List

import numpy as np
import pandas as pd
import streamlit as st

from utils.elo import compute_elo_ratings

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "matches_clean.csv")

# Columns we expect. If a match stats column (shots, corners, cards...) is
# missing from a given source file the app still runs -- it just quietly
# skips features/charts that depend on it.
CORE_COLUMNS = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "season"]
STAT_COLUMNS = [
    "HTHG", "HTAG", "HTR", "Referee", "HS", "AS", "HST", "AST",
    "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR",
]


def _season_label(raw: str) -> str:
    """'season_2000_01' -> '2000/01' for display purposes."""
    if not isinstance(raw, str):
        return str(raw)
    parts = raw.replace("season_", "").split("_")
    if len(parts) == 2:
        return f"{parts[0]}/{parts[1]}"
    return raw


def _season_sort_key(raw: str) -> int:
    parts = raw.replace("season_", "").split("_")
    try:
        return int(parts[0])
    except (ValueError, IndexError):
        return 0


def load_raw_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Read the CSV from disk with defensive dtype handling."""
    df = pd.read_csv(path)
    missing_core = [c for c in CORE_COLUMNS if c not in df.columns]
    if missing_core:
        raise ValueError(
            f"matches_clean.csv is missing required columns: {missing_core}"
        )
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Type coercion, dedup, and basic sanity filtering."""
    df = df.copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"])

    for col in ["FTHG", "FTAG", "HTHG", "HTAG", "HS", "AS", "HST", "AST",
                "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["HomeTeam"] = df["HomeTeam"].astype(str).str.strip()
    df["AwayTeam"] = df["AwayTeam"].astype(str).str.strip()

    df = df.drop_duplicates(subset=["Date", "HomeTeam", "AwayTeam"])
    df = df.sort_values("Date").reset_index(drop=True)

    df["SeasonLabel"] = df["season"].apply(_season_label)
    df["SeasonSortKey"] = df["season"].apply(_season_sort_key)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns used across the whole app."""
    df = df.copy()

    df["TotalGoals"] = df["FTHG"] + df["FTAG"]
    df["GoalDiff"] = df["FTHG"] - df["FTAG"]
    df["BTTS"] = ((df["FTHG"] > 0) & (df["FTAG"] > 0)).astype(int)
    df["Over25"] = (df["TotalGoals"] > 2.5).astype(int)
    df["HomePoints"] = np.where(df["FTR"] == "H", 3, np.where(df["FTR"] == "D", 1, 0))
    df["AwayPoints"] = np.where(df["FTR"] == "A", 3, np.where(df["FTR"] == "D", 1, 0))
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    df["Weekday"] = df["Date"].dt.day_name()

    if {"HS", "AS"}.issubset(df.columns):
        df["ShotDiff"] = df["HS"] - df["AS"]
    if {"HST", "AST"}.issubset(df.columns):
        df["ShotAccHome"] = np.where(df["HS"] > 0, df["HST"] / df["HS"], np.nan)
        df["ShotAccAway"] = np.where(df["AS"] > 0, df["AST"] / df["AS"], np.nan)
    if {"HC", "AC"}.issubset(df.columns):
        df["CornerDiff"] = df["HC"] - df["AC"]

    df, _ = compute_elo_ratings(df)
    df = _add_rolling_form(df)
    return df


def _long_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reshape one row-per-match into two rows-per-match (one per team) so that
    rolling "form" windows can be computed per team with a simple groupby.
    """
    home = df[["Date", "season", "SeasonLabel", "HomeTeam", "AwayTeam", "HomePoints", "FTHG", "FTAG"]].rename(
        columns={"HomeTeam": "Team", "AwayTeam": "Opponent", "HomePoints": "Points",
                 "FTHG": "GoalsFor", "FTAG": "GoalsAgainst"}
    )
    home["Venue"] = "Home"
    away = df[["Date", "season", "SeasonLabel", "AwayTeam", "HomeTeam", "AwayPoints", "FTAG", "FTHG"]].rename(
        columns={"AwayTeam": "Team", "HomeTeam": "Opponent", "AwayPoints": "Points",
                 "FTAG": "GoalsFor", "FTHG": "GoalsAgainst"}
    )
    away["Venue"] = "Away"
    long_df = pd.concat([home, away], ignore_index=True).sort_values(["Team", "Date"])
    long_df["Result"] = np.select(
        [long_df["Points"] == 3, long_df["Points"] == 1],
        ["W", "D"],
        default="L",
    )
    return long_df


def _long_format_with_form(df: pd.DataFrame) -> pd.DataFrame:
    """Long-format table with pre-match rolling form columns attached
    (Form5, Form10, GoalsForForm5, GoalsAgainstForm5), shifted so the
    current match is excluded from its own rolling window."""
    long_df = _long_format(df)
    long_df["Form5"] = (
        long_df.groupby("Team")["Points"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).sum())
    )
    long_df["Form10"] = (
        long_df.groupby("Team")["Points"].transform(lambda s: s.shift(1).rolling(10, min_periods=1).sum())
    )
    long_df["GoalsForForm5"] = (
        long_df.groupby("Team")["GoalsFor"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())
    )
    long_df["GoalsAgainstForm5"] = (
        long_df.groupby("Team")["GoalsAgainst"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())
    )
    return long_df


def _add_rolling_form(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add pre-match rolling form (points won in last 5 / last 10 matches,
    shifted so the current match is excluded) back onto the wide match table
    for both the home and the away team.
    """
    long_df = _long_format_with_form(df)

    home_form = long_df[long_df["Venue"] == "Home"][
        ["Date", "Team", "Form5", "Form10", "GoalsForForm5", "GoalsAgainstForm5"]
    ].rename(columns={
        "Team": "HomeTeam", "Form5": "HomeForm5", "Form10": "HomeForm10",
        "GoalsForForm5": "HomeGF5", "GoalsAgainstForm5": "HomeGA5",
    })
    away_form = long_df[long_df["Venue"] == "Away"][
        ["Date", "Team", "Form5", "Form10", "GoalsForForm5", "GoalsAgainstForm5"]
    ].rename(columns={
        "Team": "AwayTeam", "Form5": "AwayForm5", "Form10": "AwayForm10",
        "GoalsForForm5": "AwayGF5", "GoalsAgainstForm5": "AwayGA5",
    })

    df = df.merge(home_form, on=["Date", "HomeTeam"], how="left")
    df = df.merge(away_form, on=["Date", "AwayTeam"], how="left")
    return df


def team_long_format(df: pd.DataFrame) -> pd.DataFrame:
    """Public accessor for the per-team long format table, including rolling
    form columns (Form5/Form10) used by Team Analytics' form chart."""
    return _long_format_with_form(df)


def compute_season_table(df: pd.DataFrame, season: str) -> pd.DataFrame:
    """Classic PL table: Pld/W/D/L/GF/GA/GD/Pts, sorted by points."""
    season_df = df[df["season"] == season]
    long_df = _long_format(season_df)

    table = long_df.groupby("Team").agg(
        Pld=("Points", "count"),
        W=("Result", lambda s: (s == "W").sum()),
        D=("Result", lambda s: (s == "D").sum()),
        L=("Result", lambda s: (s == "L").sum()),
        GF=("GoalsFor", "sum"),
        GA=("GoalsAgainst", "sum"),
        Pts=("Points", "sum"),
    ).reset_index()
    table["GD"] = table["GF"] - table["GA"]
    table = table.sort_values(["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
    table.index = table.index + 1
    table.index.name = "Pos"
    return table[["Team", "Pld", "W", "D", "L", "GF", "GA", "GD", "Pts"]]


def compute_all_time_table(df: pd.DataFrame) -> pd.DataFrame:
    """All-time aggregate table across every season in the dataset."""
    long_df = _long_format(df)
    table = long_df.groupby("Team").agg(
        Pld=("Points", "count"),
        W=("Result", lambda s: (s == "W").sum()),
        D=("Result", lambda s: (s == "D").sum()),
        L=("Result", lambda s: (s == "L").sum()),
        GF=("GoalsFor", "sum"),
        GA=("GoalsAgainst", "sum"),
        Pts=("Points", "sum"),
        Seasons=("season", "nunique"),
    ).reset_index()
    table["GD"] = table["GF"] - table["GA"]
    table["PPG"] = (table["Pts"] / table["Pld"]).round(2)
    table = table.sort_values("Pts", ascending=False).reset_index(drop=True)
    table.index = table.index + 1
    table.index.name = "Rank"
    return table


def get_team_list(df: pd.DataFrame) -> List[str]:
    return sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))


def get_season_list(df: pd.DataFrame) -> List[str]:
    seasons = df[["season", "SeasonSortKey"]].drop_duplicates().sort_values("SeasonSortKey")
    return seasons["season"].tolist()


def head_to_head(df: pd.DataFrame, team_a: str, team_b: str) -> pd.DataFrame:
    mask = (
        ((df["HomeTeam"] == team_a) & (df["AwayTeam"] == team_b))
        | ((df["HomeTeam"] == team_b) & (df["AwayTeam"] == team_a))
    )
    return df[mask].sort_values("Date")


# --------------------------------------------------------------------------- #
# Streamlit-cached entry point
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner="Loading and engineering Premier League data...")
def get_full_dataset(path: str = DATA_PATH) -> pd.DataFrame:
    raw = load_raw_data(path)
    cleaned = clean_data(raw)
    engineered = engineer_features(cleaned)
    return engineered


@st.cache_data(show_spinner=False)
def get_team_list_cached(df: pd.DataFrame) -> List[str]:
    return get_team_list(df)
