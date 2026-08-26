"""
Machine learning suite for Premier League Intelligence.

Trains and compares classical ML models on engineered match features to
predict match outcomes (H/D/A), BTTS, and Over/Under 2.5 goals. Designed to
degrade gracefully: XGBoost / LightGBM are used only if installed, and the
UI is expected to check `OPTIONAL_MODELS_AVAILABLE` before offering them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

try:
    from xgboost import XGBClassifier  # type: ignore
    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False

try:
    from lightgbm import LGBMClassifier  # type: ignore
    _HAS_LGBM = True
except ImportError:
    _HAS_LGBM = False

OPTIONAL_MODELS_AVAILABLE: Dict[str, bool] = {"XGBoost": _HAS_XGB, "LightGBM": _HAS_LGBM}

FEATURE_COLUMNS: List[str] = [
    "EloHome", "EloAway", "EloDiff",
    "HomeForm5", "HomeForm10", "AwayForm5", "AwayForm10",
    "HomeGF5", "HomeGA5", "AwayGF5", "AwayGA5",
]


def build_model_zoo(include_optional: bool = True) -> Dict[str, object]:
    """Return a fresh, unfitted instance of every requested classifier."""
    zoo: Dict[str, object] = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000)),
        ]),
        "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=42),
        "K-Nearest Neighbors": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", KNeighborsClassifier(n_neighbors=15)),
        ]),
        "Support Vector Machine": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(probability=True, kernel="rbf", C=1.0)),
        ]),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "Naive Bayes": GaussianNB(),
        "Neural Network (MLP)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=800, random_state=42)),
        ]),
    }
    if include_optional and _HAS_XGB:
        zoo["XGBoost"] = XGBClassifier(
            n_estimators=250, max_depth=4, learning_rate=0.08,
            eval_metric="logloss", random_state=42,
        )
    if include_optional and _HAS_LGBM:
        zoo["LightGBM"] = LGBMClassifier(n_estimators=250, max_depth=6, learning_rate=0.08, random_state=42)
    return zoo


@dataclass
class ModelResult:
    name: str
    model: object
    accuracy: float
    precision: float
    recall: float
    f1: float
    cv_mean: float
    cv_std: float
    y_test: np.ndarray
    y_pred: np.ndarray
    y_proba: Optional[np.ndarray] = None
    classes: List[str] = field(default_factory=list)
    feature_importance: Optional[pd.Series] = None
    fit_time_s: float = 0.0


def prepare_training_frame(
    df: pd.DataFrame, target: str, feature_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.Series]:
    """Drop rows with missing engineered features (early-season teams with
    no rolling history yet) and split into X / y for the requested target."""
    cols = feature_cols or FEATURE_COLUMNS
    valid_cols = [c for c in cols if c in df.columns]
    work = df.dropna(subset=valid_cols + [target]).copy()
    X = work[valid_cols]
    y = work[target]
    return X, y


def train_and_evaluate(
    df: pd.DataFrame,
    target: str,
    model_names: List[str],
    feature_cols: Optional[List[str]] = None,
    test_size: float = 0.2,
    cv_folds: int = 5,
    random_state: int = 42,
) -> Dict[str, ModelResult]:
    """Train every requested model on the same train/test split and return
    a dict of ModelResult keyed by model name, for apples-to-apples comparison."""
    import time

    X, y = prepare_training_frame(df, target, feature_cols)

    encoder: Optional[LabelEncoder] = None
    if y.dtype == object or str(y.dtype) == "category":
        encoder = LabelEncoder()
        y_enc = encoder.fit_transform(y)
        classes = list(encoder.classes_)
    else:
        y_enc = y.values
        classes = sorted(pd.Series(y).unique().tolist())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=test_size, random_state=random_state, stratify=y_enc
    )

    zoo = build_model_zoo()
    results: Dict[str, ModelResult] = {}

    for name in model_names:
        if name not in zoo:
            continue
        model = zoo[name]
        start = time.time()
        model.fit(X_train, y_train)
        fit_time = time.time() - start

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

        try:
            cv_scores = cross_val_score(model, X, y_enc, cv=cv_folds, scoring="accuracy")
            cv_mean, cv_std = float(cv_scores.mean()), float(cv_scores.std())
        except Exception:
            cv_mean, cv_std = float("nan"), float("nan")

        avg = "binary" if len(classes) == 2 else "macro"
        importance = _extract_feature_importance(model, X.columns)

        results[name] = ModelResult(
            name=name,
            model=model,
            accuracy=accuracy_score(y_test, y_pred),
            precision=precision_score(y_test, y_pred, average=avg, zero_division=0),
            recall=recall_score(y_test, y_pred, average=avg, zero_division=0),
            f1=f1_score(y_test, y_pred, average=avg, zero_division=0),
            cv_mean=cv_mean,
            cv_std=cv_std,
            y_test=y_test,
            y_pred=y_pred,
            y_proba=y_proba,
            classes=[str(c) for c in classes],
            feature_importance=importance,
            fit_time_s=fit_time,
        )
    return results


def _extract_feature_importance(model, feature_names) -> Optional[pd.Series]:
    """Pull out a normalized feature-importance vector regardless of which
    underlying estimator we're dealing with (handles Pipelines too)."""
    est = model
    if isinstance(model, Pipeline):
        est = model.named_steps.get("clf", model)

    if hasattr(est, "feature_importances_"):
        vals = est.feature_importances_
    elif hasattr(est, "coef_"):
        coef = est.coef_
        vals = np.abs(coef).mean(axis=0) if coef.ndim > 1 else np.abs(coef)
    else:
        return None

    series = pd.Series(vals, index=feature_names).sort_values(ascending=False)
    total = series.sum()
    return series / total if total > 0 else series


def confusion_matrix_df(result: ModelResult) -> pd.DataFrame:
    cm = confusion_matrix(result.y_test, result.y_pred)
    return pd.DataFrame(cm, index=result.classes, columns=result.classes)


def roc_data(result: ModelResult) -> Optional[Dict[str, np.ndarray]]:
    """Only meaningful for binary targets with predict_proba support."""
    if result.y_proba is None or len(result.classes) != 2:
        return None
    fpr, tpr, _ = roc_curve(result.y_test, result.y_proba[:, 1])
    auc = roc_auc_score(result.y_test, result.y_proba[:, 1])
    return {"fpr": fpr, "tpr": tpr, "auc": auc}


def monte_carlo_match_simulation(
    home_elo: float, away_elo: float, n_sims: int = 10_000, home_advantage: float = 60.0, seed: int = 42
) -> Dict[str, float]:
    """
    Simulate a single fixture n_sims times using a Poisson goal model whose
    expected goals are derived from the Elo gap, then tally outcomes. Used
    by the Prediction Center's Monte Carlo panel.
    """
    rng = np.random.default_rng(seed)
    elo_gap = (home_elo + home_advantage) - away_elo
    base_goals = 1.35
    home_xg = np.clip(base_goals * 10 ** (elo_gap / 800), 0.3, 4.5)
    away_xg = np.clip(base_goals * 10 ** (-elo_gap / 800), 0.3, 4.5)

    home_goals = rng.poisson(home_xg, n_sims)
    away_goals = rng.poisson(away_xg, n_sims)

    home_win = float(np.mean(home_goals > away_goals))
    draw = float(np.mean(home_goals == away_goals))
    away_win = float(np.mean(home_goals < away_goals))
    btts = float(np.mean((home_goals > 0) & (away_goals > 0)))
    over25 = float(np.mean((home_goals + away_goals) > 2.5))

    return {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "btts": btts,
        "over25": over25,
        "avg_home_goals": float(home_goals.mean()),
        "avg_away_goals": float(away_goals.mean()),
        "home_xg": float(home_xg),
        "away_xg": float(away_xg),
        "most_likely_score": _most_likely_score(home_goals, away_goals),
    }


def _most_likely_score(home_goals: np.ndarray, away_goals: np.ndarray) -> str:
    pairs = list(zip(home_goals.tolist(), away_goals.tolist()))
    counts: Dict[Tuple[int, int], int] = {}
    for p in pairs:
        counts[p] = counts.get(p, 0) + 1
    best = max(counts.items(), key=lambda kv: kv[1])[0]
    return f"{best[0]}-{best[1]}"


def season_monte_carlo(
    current_table: pd.DataFrame,
    remaining_fixtures: pd.DataFrame,
    elo_ratings: Dict[str, float],
    n_sims: int = 2000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Simulate the rest of a season n_sims times to produce title / European /
    relegation probability estimates for every team still in the table.
    """
    rng = np.random.default_rng(seed)
    teams = current_table["Team"].tolist()
    base_points = dict(zip(current_table["Team"], current_table["Pts"]))
    base_gd = dict(zip(current_table["Team"], current_table["GD"]))

    title_count = {t: 0 for t in teams}
    top4_count = {t: 0 for t in teams}
    bottom3_count = {t: 0 for t in teams}

    fixtures = remaining_fixtures[["HomeTeam", "AwayTeam"]].to_dict("records")

    for _ in range(n_sims):
        points = dict(base_points)
        gd = dict(base_gd)
        for fx in fixtures:
            h, a = fx["HomeTeam"], fx["AwayTeam"]
            if h not in points or a not in points:
                continue
            probs = _elo_probs(elo_ratings.get(h, 1500), elo_ratings.get(a, 1500))
            outcome = rng.choice(["H", "D", "A"], p=[probs["home_win"], probs["draw"], probs["away_win"]])
            if outcome == "H":
                points[h] += 3
                gd[h] += 1
                gd[a] -= 1
            elif outcome == "A":
                points[a] += 3
                gd[a] += 1
                gd[h] -= 1
            else:
                points[h] += 1
                points[a] += 1

        ranking = sorted(teams, key=lambda t: (points[t], gd[t]), reverse=True)
        title_count[ranking[0]] += 1
        for t in ranking[:4]:
            top4_count[t] += 1
        for t in ranking[-3:]:
            bottom3_count[t] += 1

    out = pd.DataFrame({
        "Team": teams,
        "CurrentPts": [base_points[t] for t in teams],
        "TitleProb%": [round(100 * title_count[t] / n_sims, 2) for t in teams],
        "Top4Prob%": [round(100 * top4_count[t] / n_sims, 2) for t in teams],
        "RelegationProb%": [round(100 * bottom3_count[t] / n_sims, 2) for t in teams],
    }).sort_values("CurrentPts", ascending=False).reset_index(drop=True)
    return out


def _elo_probs(elo_home: float, elo_away: float, home_advantage: float = 60.0) -> Dict[str, float]:
    from utils.elo import elo_win_probabilities
    return elo_win_probabilities(elo_home, elo_away, home_advantage)
