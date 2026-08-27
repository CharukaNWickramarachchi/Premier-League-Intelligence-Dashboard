"""About — what this app is, how it's built, and an honest account of what's
real vs simplified/simulated/omitted given offline build constraints."""
from __future__ import annotations

import streamlit as st

from utils.data_loader import get_full_dataset
from utils.ml_models import OPTIONAL_MODELS_AVAILABLE
from utils.theme import hero, inject_css, section_title

st.set_page_config(page_title="About — PLI", page_icon="ℹ️", layout="wide")
inject_css()
hero("About Premier League Intelligence", "What this app does, how it was built, and where its limits are.")

df = get_full_dataset()

section_title("Overview")
st.markdown(
    f"""
    <div class="pli-card">
    Premier League Intelligence is a multi-page Streamlit analytics + machine-learning app built on
    <code>matches_clean.csv</code> — {len(df):,} matches spanning {df['season'].nunique()} seasons
    ({df['SeasonLabel'].iloc[0]} to {df['SeasonLabel'].iloc[-1]}) and {len(set(df['HomeTeam'])|set(df['AwayTeam']))} clubs.
    </div>
    """,
    unsafe_allow_html=True,
)

section_title("What's Fully Implemented")
st.markdown(
    """
    <div class="pli-card">
    <ul>
        <li><b>Data engine:</b> cleaning, dedup, type coercion, per-team long-format reshaping.</li>
        <li><b>Feature engineering:</b> sequential Elo ratings (margin-of-victory weighted, home advantage,
            leak-free — pre-match ratings only), rolling 5/10-match form, BTTS, Over/Under 2.5, goal diff.</li>
        <li><b>League analytics:</b> per-season tables, all-time table with points-per-game, treemap/sunburst
            goal breakdowns.</li>
        <li><b>Team analytics:</b> form &amp; Elo trajectory, attack/defense radar vs league average, home/away
            split, disciplinary record.</li>
        <li><b>Head-to-head:</b> full history between any two clubs with win-share and timeline charts.</li>
        <li><b>Machine learning:</b> Logistic Regression, Random Forest, Gradient Boosting, KNN, SVM, Decision
            Tree, Naive Bayes, and an MLP neural net — trained side-by-side with accuracy/precision/recall/F1,
            k-fold cross-validation, confusion matrices, ROC/AUC (binary targets), and feature importance.
            XGBoost and LightGBM plug in automatically if installed.</li>
        <li><b>Simulation:</b> a Poisson-based Monte Carlo match simulator (10,000 runs) and a season-outcome
            simulator for title / top-4 / relegation probabilities.</li>
        <li><b>Statistics:</b> PCA, KMeans &amp; hierarchical clustering of teams, z-score/IQR outlier detection,
            t-tests, one-way ANOVA, chi-square independence tests, correlation heatmaps, simple linear
            regression, percentile ranks.</li>
        <li><b>Exports:</b> CSV and Excel downloads for filtered matches, league tables, and model results.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

section_title("What's Simplified, Simulated, or Not Included — and Why")
st.markdown(
    f"""
    <div class="pli-card">
    <ul>
        <li><b>No live Premier League feed.</b> This build environment has no internet access, so
            "standings," "fixtures," and predictions are computed entirely from your historical CSV —
            not a live API. Wiring in a real live-data API (e.g. football-data.org) is a natural next
            step if you deploy this with network access.</li>
        <li><b>Stadium map uses static, hand-curated coordinates</b> (<code>utils/reference_data.py</code>),
            not a live geocoding service. Accurate as of recent seasons, but a club relocating grounds
            won't update automatically.</li>
        <li><b>No real club crest images.</b> Logos are represented as color-coded badges using each club's
            primary color rather than fetched image assets — no image-hosting/licensing pipeline was set up.</li>
        <li><b>No Player Analytics page.</b> <code>matches_clean.csv</code> is match-level (team stats only,
            no player rows), so a genuine player-analytics page isn't possible from this data without a
            different dataset. Rather than fabricate placeholder player stats, that page was omitted.</li>
        <li><b>XGBoost / LightGBM / SHAP are optional dependencies.</b> They weren't installed in the
            sandbox this app was authored in, so they're wrapped in try/except and simply appear once you
            <code>pip install</code> them — currently available: XGBoost
            {"✅" if OPTIONAL_MODELS_AVAILABLE["XGBoost"] else "❌ (not installed in build env)"},
            LightGBM {"✅" if OPTIONAL_MODELS_AVAILABLE["LightGBM"] else "❌ (not installed in build env)"}.
            SHAP explanations weren't wired in for the same reason — the ROC/feature-importance views serve
            a similar diagnostic purpose today.</li>
        <li><b>Transfer market</b> is out of scope — there's no transfer data in the source CSV and no live
            transfer feed to connect to offline, so no placeholder page was built for it.</li>
        <li><b>PDF export</b> wasn't included in this build (no PDF library was available to verify against
            in the sandbox); CSV/Excel export is fully implemented in Downloads. Adding a PDF export via
            a library like <code>reportlab</code> is a contained follow-up.</li>
        <li><b>Elo K-factor / home-advantage sliders</b> on the Settings page are present but not yet wired
            into the cached data pipeline (documented there) — a small follow-up if you want them live.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

section_title("Tech Stack")
st.markdown(
    """
    <div class="pli-card">
    Streamlit · pandas · NumPy · scikit-learn · Plotly · SciPy · statsmodels · openpyxl
    </div>
    """,
    unsafe_allow_html=True,
)

section_title("Running Locally")
st.code(
    "pip install -r requirements.txt\nstreamlit run app.py",
    language="bash",
)
st.caption("This app was authored and syntax-checked in an offline sandbox; please run the two commands "
           "above locally to fully verify behavior before relying on it.")
