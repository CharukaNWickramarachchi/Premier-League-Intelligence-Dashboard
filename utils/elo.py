"""
Elo rating engine for Premier League Intelligence.

Implements a standard chess-style Elo system adapted for football, with
home-field advantage and margin-of-victory weighting (similar in spirit to
FiveThirtyEight's SPI / Elo approach).

All ratings are computed strictly sequentially in chronological order so
that a match's pre-game Elo never leaks information from that match or any
future match (no data leakage for downstream ML features).
"""
from __future__ import annotations

import pandas as pd
from typing import Dict, Tuple

DEFAULT_RATING: float = 1500.0
K_FACTOR: float = 20.0
HOME_ADVANTAGE: float = 60.0  # Elo points added to home team's effective rating


def _expected_score(rating_a: float, rating_b: float) -> float:
    """Probability that team A beats team B (draws split as 0.5/0.5 upstream)."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def _margin_multiplier(goal_diff: int) -> float:
    """Scale the Elo update by how comprehensive the win was."""
    goal_diff = abs(goal_diff)
    if goal_diff <= 1:
        return 1.0
    if goal_diff == 2:
        return 1.5
    return 1.75 + (goal_diff - 3) * 0.2


def compute_elo_ratings(
    matches: pd.DataFrame,
    k_factor: float = K_FACTOR,
    home_advantage: float = HOME_ADVANTAGE,
    default_rating: float = DEFAULT_RATING,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Walk through matches in chronological order and compute pre-match Elo
    ratings for the home and away side of every fixture.

    Parameters
    ----------
    matches : DataFrame sorted or sortable by Date, with HomeTeam, AwayTeam,
        FTHG, FTAG columns.

    Returns
    -------
    (matches_with_elo, final_ratings) where matches_with_elo has two new
    columns -- EloHome, EloAway (the ratings *before* that match kicked off)
    -- and final_ratings is a dict of the most recent rating for every team.
    """
    df = matches.sort_values("Date").reset_index(drop=True).copy()
    ratings: Dict[str, float] = {}

    elo_home_col = []
    elo_away_col = []

    for _, row in df.iterrows():
        home, away = row["HomeTeam"], row["AwayTeam"]
        r_home = ratings.get(home, default_rating)
        r_away = ratings.get(away, default_rating)

        elo_home_col.append(r_home)
        elo_away_col.append(r_away)

        goal_diff = int(row["FTHG"]) - int(row["FTAG"])
        if goal_diff > 0:
            actual_home = 1.0
        elif goal_diff < 0:
            actual_home = 0.0
        else:
            actual_home = 0.5

        expected_home = _expected_score(r_home + home_advantage, r_away)
        mult = _margin_multiplier(goal_diff)
        delta = k_factor * mult * (actual_home - expected_home)

        ratings[home] = r_home + delta
        ratings[away] = r_away - delta

    df["EloHome"] = elo_home_col
    df["EloAway"] = elo_away_col
    df["EloDiff"] = df["EloHome"] - df["EloAway"]
    return df, ratings


def elo_win_probabilities(
    elo_home: float, elo_away: float, home_advantage: float = HOME_ADVANTAGE
) -> Dict[str, float]:
    """
    Convert a pair of Elo ratings into Home/Draw/Away probabilities.

    Draws are modelled with an empirically reasonable fixed base rate that
    shrinks as the rating gap widens (blowouts draw less often), which is a
    simple but effective heuristic used by several public Elo-for-football
    implementations.
    """
    p_home_no_draw = _expected_score(elo_home + home_advantage, elo_away)
    gap = abs((elo_home + home_advantage) - elo_away)
    draw_base = 0.28
    draw_prob = max(0.12, draw_base - gap / 1600.0)

    p_home = p_home_no_draw * (1 - draw_prob)
    p_away = (1 - p_home_no_draw) * (1 - draw_prob)
    total = p_home + p_away + draw_prob
    return {
        "home_win": p_home / total,
        "draw": draw_prob / total,
        "away_win": p_away / total,
    }
