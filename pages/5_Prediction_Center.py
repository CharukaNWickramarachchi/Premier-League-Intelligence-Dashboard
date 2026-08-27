"""Prediction Center — train/compare classical ML models, predict a
hypothetical fixture, run Monte Carlo simulations, and project season
outcome probabilities (title / top-4 / relegation)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from utils.data_loader import compute_season_table, get_full_dataset, get_season_list, get_team_list
from utils.elo import elo_win_probabilities
from utils.reference_data import get_logo_path
from utils.ml_models import (
    FEATURE_COLUMNS,
    OPTIONAL_MODELS_AVAILABLE,
    build_model_zoo,
    confusion_matrix_df,
    monte_carlo_match_simulation,
    prepare_training_frame,
    roc_data,
    season_monte_carlo,
    train_and_evaluate,
)
from utils.theme import hero, inject_css, insight_box, section_title
from utils import viz

st.set_page_config(page_title="Prediction Center — PLI", page_icon="🔮", layout="wide")
inject_css()
hero("Prediction Center", "Train and compare machine-learning models, then use them to predict fixtures and simulate the season.")

df = get_full_dataset()

if not OPTIONAL_MODELS_AVAILABLE["XGBoost"] or not OPTIONAL_MODELS_AVAILABLE["LightGBM"]:
    missing = [k for k, v in OPTIONAL_MODELS_AVAILABLE.items() if not v]
    st.markdown(
        f'<div class="pli-card">⚠️ {", ".join(missing)} not installed in this environment — '
        "they'll appear automatically once you `pip install` them. Every other model below works today.</div>",
        unsafe_allow_html=True,
    )

tab1, tab2, tab3, tab4 = st.tabs(
    ["🤖 Train & Compare Models", "🔮 Predict a Fixture", "🎲 Monte Carlo Simulation", "📈 Season Probability Tracker"]
)

# ============================================================ #
# TAB 1 — Train & Compare
# ============================================================ #
with tab1:
    section_title("Choose a Prediction Target")
    target_map = {
        "Match Result (H/D/A)": "FTR",
        "Both Teams to Score (BTTS)": "BTTS",
        "Over 2.5 Goals": "Over25",
    }
    target_label = st.selectbox("Target", list(target_map.keys()))
    target_col = target_map[target_label]

    zoo_names = list(build_model_zoo().keys())
    selected_models = st.multiselect("Models to train", zoo_names, default=zoo_names[:5])

    c1, c2, c3 = st.columns(3)
    test_size = c1.slider("Test set size", 0.1, 0.4, 0.2, 0.05)
    cv_folds = c2.slider("Cross-validation folds", 3, 10, 5)
    run = c3.button("🚀 Train Models", use_container_width=True)

    X_check, y_check = prepare_training_frame(df, target_col)
    st.caption(
        f"Training on {len(X_check):,} matches with complete feature history "
        f"(earliest few matches per team are dropped since rolling form/Elo need history first)."
    )

    if run and selected_models:
        with st.spinner("Training models — this can take a little while for SVM/MLP on the full dataset..."):
            results = train_and_evaluate(df, target_col, selected_models, cv_folds=cv_folds, test_size=test_size)
        st.session_state["last_results"] = results
        st.session_state["last_target"] = target_col

    results = st.session_state.get("last_results")
    if results:
        section_title("Model Comparison")
        rows = []
        for name, r in results.items():
            rows.append({
                "Model": name, "Accuracy": r.accuracy, "Precision": r.precision,
                "Recall": r.recall, "F1": r.f1, "CV Mean": r.cv_mean, "CV Std": r.cv_std,
                "Fit Time (s)": round(r.fit_time_s, 2),
            })
        results_df = pd.DataFrame(rows).sort_values("Accuracy", ascending=False)
        st.dataframe(results_df.style.format({
            "Accuracy": "{:.3f}", "Precision": "{:.3f}", "Recall": "{:.3f}",
            "F1": "{:.3f}", "CV Mean": "{:.3f}", "CV Std": "{:.3f}",
        }), use_container_width=True)
        st.plotly_chart(viz.model_comparison_bar(results_df, "Accuracy"), use_container_width=True)

        best_name = results_df.iloc[0]["Model"]
        insight_box(f"**{best_name}** had the highest held-out accuracy for predicting {target_label.lower()} "
                    "on this split. Check cross-validation mean/std too — a model that's stable across folds "
                    "generalizes more reliably than one that's only strong on this particular split.")

        section_title("Inspect a Single Model")
        pick = st.selectbox("Model detail", list(results.keys()))
        r = results[pick]
        d1, d2 = st.columns(2)
        with d1:
            cm = confusion_matrix_df(r)
            st.plotly_chart(viz.confusion_matrix_heatmap(cm, f"{pick} — Confusion Matrix"), use_container_width=True)
        with d2:
            roc = roc_data(r)
            if roc:
                st.plotly_chart(viz.roc_curve_fig(roc["fpr"], roc["tpr"], roc["auc"], f"{pick} — ROC Curve"),
                                 use_container_width=True)
            else:
                st.info("ROC curve is only shown for binary targets (BTTS / Over 2.5) with probability support.")

        if r.feature_importance is not None:
            st.plotly_chart(viz.feature_importance_bar(r.feature_importance, f"{pick} — Feature Importance"),
                             use_container_width=True)
        else:
            st.caption(f"{pick} doesn't expose a native feature-importance/coefficient view.")
    else:
        st.info("Pick a target, choose models, and hit **Train Models** to see results.")

# ============================================================ #
# TAB 2 — Predict a Fixture
# ============================================================ #
with tab2:
    section_title("Predict a Hypothetical Fixture")
    teams = get_team_list(df)
    c1, c2 = st.columns(2)
    home_team = c1.selectbox("Home Team", teams, key="pred_home")
    away_team = c2.selectbox("Away Team", [t for t in teams if t != home_team], key="pred_away")

    logo_a, logo_b = st.columns(2)
    with logo_a:
        p = get_logo_path(home_team)
        if p:
            st.image(p, width=70)
    with logo_b:
        p = get_logo_path(away_team)
        if p:
            st.image(p, width=70)

    def _latest_snapshot(team: str, venue: str) -> dict:
        col_home = {"Elo": "EloHome", "Form5": "HomeForm5", "Form10": "HomeForm10", "GF5": "HomeGF5", "GA5": "HomeGA5"}
        col_away = {"Elo": "EloAway", "Form5": "AwayForm5", "Form10": "AwayForm10", "GF5": "AwayGF5", "GA5": "AwayGA5"}
        cols = col_home if venue == "home" else col_away
        team_col = "HomeTeam" if venue == "home" else "AwayTeam"
        sub = df[df[team_col] == team].sort_values("Date")
        if sub.empty:
            return {k: np.nan for k in cols}
        last = sub.iloc[-1]
        return {k: last[c] for k, c in cols.items()}

    home_snap = _latest_snapshot(home_team, "home")
    away_snap = _latest_snapshot(away_team, "away")

    st.caption(f"Using each team's most recent known Elo rating and rolling form as of their last recorded match.")
    m1, m2 = st.columns(2)
    m1.metric(f"{home_team} Elo", f"{home_snap['Elo']:.0f}")
    m2.metric(f"{away_team} Elo", f"{away_snap['Elo']:.0f}")

    elo_probs = elo_win_probabilities(home_snap["Elo"], away_snap["Elo"])
    section_title("Elo-Based Win Probability")
    p1, p2, p3 = st.columns(3)
    p1.metric(f"{home_team} Win", f"{elo_probs['home_win']*100:.1f}%")
    p2.metric("Draw", f"{elo_probs['draw']*100:.1f}%")
    p3.metric(f"{away_team} Win", f"{elo_probs['away_win']*100:.1f}%")

    if st.session_state.get("last_results") and st.session_state.get("last_target") == "FTR":
        section_title("ML Model Prediction (using your trained models from Tab 1)")
        feature_row = pd.DataFrame([{
            "EloHome": home_snap["Elo"], "EloAway": away_snap["Elo"],
            "EloDiff": home_snap["Elo"] - away_snap["Elo"],
            "HomeForm5": home_snap["Form5"], "HomeForm10": home_snap["Form10"],
            "AwayForm5": away_snap["Form5"], "AwayForm10": away_snap["Form10"],
            "HomeGF5": home_snap["GF5"], "HomeGA5": home_snap["GA5"],
            "AwayGF5": away_snap["GF5"], "AwayGA5": away_snap["GA5"],
        }])[FEATURE_COLUMNS]

        results = st.session_state["last_results"]
        preds = []
        for name, r in results.items():
            try:
                proba = r.model.predict_proba(feature_row)[0]
                pred_class = r.classes[int(np.argmax(proba))]
                preds.append({"Model": name, "Predicted": pred_class,
                              **{f"P({c})": f"{p*100:.1f}%" for c, p in zip(r.classes, proba)}})
            except Exception:
                continue
        if preds:
            st.dataframe(pd.DataFrame(preds), use_container_width=True)
        else:
            st.caption("Trained models couldn't score this fixture (missing feature history for one of the teams).")
    else:
        st.caption("Train models on the **Match Result (H/D/A)** target in Tab 1 to also see ML predictions here.")

# ============================================================ #
# TAB 3 — Monte Carlo
# ============================================================ #
with tab3:
    section_title("Monte Carlo Match Simulation (10,000 runs)")
    teams = get_team_list(df)
    c1, c2 = st.columns(2)
    mc_home = c1.selectbox("Home Team", teams, key="mc_home")
    mc_away = c2.selectbox("Away Team", [t for t in teams if t != mc_home], key="mc_away")

    home_sub = df[df["HomeTeam"] == mc_home].sort_values("Date")
    away_sub = df[df["AwayTeam"] == mc_away].sort_values("Date")
    home_elo = home_sub.iloc[-1]["EloHome"] if len(home_sub) else 1500.0
    away_elo = away_sub.iloc[-1]["EloAway"] if len(away_sub) else 1500.0

    if st.button("🎲 Run 10,000 Simulations", use_container_width=True):
        sim = monte_carlo_match_simulation(home_elo, away_elo, n_sims=10_000)
        r1, r2, r3 = st.columns(3)
        r1.metric(f"{mc_home} Win", f"{sim['home_win']*100:.1f}%")
        r2.metric("Draw", f"{sim['draw']*100:.1f}%")
        r3.metric(f"{mc_away} Win", f"{sim['away_win']*100:.1f}%")
        r4, r5, r6 = st.columns(3)
        r4.metric("BTTS", f"{sim['btts']*100:.1f}%")
        r5.metric("Over 2.5 Goals", f"{sim['over25']*100:.1f}%")
        r6.metric("Most Likely Score", sim["most_likely_score"])
        insight_box(
            f"Simulated expected goals: {mc_home} {sim['home_xg']:.2f} vs {mc_away} {sim['away_xg']:.2f}. "
            "These come from a Poisson goal model calibrated on the Elo gap between the two teams — "
            "a simplification of real match dynamics (no injuries, tactics, or weather), useful as a "
            "probabilistic baseline rather than a certainty."
        )

# ============================================================ #
# TAB 4 — Season Probability Tracker
# ============================================================ #
with tab4:
    section_title("Season Winner / Top-4 / Relegation Probability Tracker")
    seasons = get_season_list(df)
    season_choice = st.selectbox("Season to simulate the remainder of", seasons, index=len(seasons) - 1,
                                  format_func=lambda s: s.replace("season_", "").replace("_", "/"), key="season_mc")

    season_df = df[df["season"] == season_choice].sort_values("Date")
    if season_df.empty:
        st.warning("No data for that season.")
    else:
        cutoff_pct = st.slider("Simulate from this point in the season onward (% of matches played)", 10, 95, 60)
        cutoff_idx = int(len(season_df) * cutoff_pct / 100)
        played = season_df.iloc[:cutoff_idx]
        remaining = season_df.iloc[cutoff_idx:]

        current_table = compute_season_table(df[df["season"] == season_choice].loc[played.index], season_choice) \
            if len(played) else compute_season_table(df, season_choice).iloc[0:0]

        # Elo snapshot at cutoff: last known rating per team from the played subset
        elo_snapshot = {}
        for _, row in played.iterrows():
            elo_snapshot[row["HomeTeam"]] = row["EloHome"]
            elo_snapshot[row["AwayTeam"]] = row["EloAway"]
        # Also seed with post-match rating using the final played row's Elo+ (approx via next match's pre-Elo if available)
        for team in set(season_df["HomeTeam"]) | set(season_df["AwayTeam"]):
            if team not in elo_snapshot:
                elo_snapshot[team] = 1500.0

        n_sims = st.slider("Number of season simulations", 500, 5000, 2000, 500)
        if st.button("📊 Simulate Rest of Season", use_container_width=True):
            with st.spinner("Simulating..."):
                sim_table = season_monte_carlo(current_table.reset_index(), remaining, elo_snapshot, n_sims=n_sims)
            st.dataframe(sim_table, use_container_width=True, height=500)
            insight_box(
                "Title / Top-4 / Relegation probabilities are estimated by simulating every remaining fixture "
                "thousands of times using Elo-implied win probabilities, then counting how often each team "
                "finishes in each range. Treat these as informative estimates, not guarantees — real seasons "
                "have injuries, squad rotation and form swings this model doesn't see."
            )
