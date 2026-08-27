"""AI Insights — automatically generated, data-driven narrative insights:
biggest upsets, referee patterns, home-advantage rankings, and a quick
feature-importance summary of what drives match outcomes."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.data_loader import get_full_dataset, team_long_format
from utils.ml_models import build_model_zoo, prepare_training_frame
from utils.theme import hero, inject_css, insight_box, section_title
from utils import viz

st.set_page_config(page_title="AI Insights — PLI", page_icon="🧠", layout="wide")
inject_css()
hero("AI Insights", "Automatically surfaced patterns and storylines mined from the full match history.")

df = get_full_dataset()
long_df = team_long_format(df)

# ------------------------------------------------------------------ #
# Biggest upsets: underdog (lower Elo) wins by biggest Elo gap
# ------------------------------------------------------------------ #
section_title("Biggest Upsets on Record")
df["Favorite"] = df.apply(lambda r: r["HomeTeam"] if r["EloHome"] >= r["EloAway"] else r["AwayTeam"], axis=1)
df["Underdog"] = df.apply(lambda r: r["AwayTeam"] if r["EloHome"] >= r["EloAway"] else r["HomeTeam"], axis=1)
df["FavoriteWon"] = df.apply(
    lambda r: (r["FTR"] == "H" and r["Favorite"] == r["HomeTeam"]) or (r["FTR"] == "A" and r["Favorite"] == r["AwayTeam"]),
    axis=1,
)
upsets = df[~df["FavoriteWon"] & (df["FTR"] != "D")].copy()
upsets["EloGap"] = (upsets["EloHome"] - upsets["EloAway"]).abs()
top_upsets = upsets.sort_values("EloGap", ascending=False).head(10)
upset_display = top_upsets.apply(
    lambda r: f"{r['Date'].date()}: {r['HomeTeam']} {int(r['FTHG'])}-{int(r['FTAG'])} {r['AwayTeam']} "
              f"(Elo gap {r['EloGap']:.0f}, underdog {r['Underdog']} won)",
    axis=1,
)
st.dataframe(pd.DataFrame({"Upset": upset_display.values}), use_container_width=True, height=300)
insight_box(
    "These are matches where the lower pre-match Elo-rated side won outright, ranked by how big the "
    "rating gap was — the closest thing this dataset has to a definitive 'giant-killing' list."
)

# ------------------------------------------------------------------ #
# Home advantage ranking
# ------------------------------------------------------------------ #
section_title("Home Advantage Ranking")
home_wr = long_df[long_df["Venue"] == "Home"].groupby("Team").apply(lambda g: (g["Result"] == "W").mean())
away_wr = long_df[long_df["Venue"] == "Away"].groupby("Team").apply(lambda g: (g["Result"] == "W").mean())
home_adv = (home_wr - away_wr).dropna().sort_values(ascending=False)
c1, c2 = st.columns(2)
with c1:
    st.write("**Biggest home fortress (Home win% − Away win%)**")
    st.dataframe(home_adv.head(8).rename("Home Advantage").reset_index(), use_container_width=True)
with c2:
    st.write("**Smallest home/away gap (most consistent)**")
    st.dataframe(home_adv.tail(8).rename("Home Advantage").reset_index(), use_container_width=True)
insight_box(
    "A large positive value means a club is dramatically better at home than away — useful context "
    "when betting markets or model predictions seem to over/under-value a fixture's venue."
)

# ------------------------------------------------------------------ #
# Referee patterns
# ------------------------------------------------------------------ #
if "Referee" in df.columns:
    section_title("Referee Patterns")
    ref_stats = df.groupby("Referee").agg(
        Matches=("Referee", "count"),
        AvgGoals=("TotalGoals", "mean"),
        AvgCards=("HY", lambda s: (df.loc[s.index, "HY"] + df.loc[s.index, "AY"]).mean()),
        AvgReds=("HR", lambda s: (df.loc[s.index, "HR"] + df.loc[s.index, "AR"]).mean()),
    ).query("Matches >= 30").sort_values("AvgCards", ascending=False)
    st.dataframe(ref_stats.head(15), use_container_width=True)
    insight_box(
        "Referees with a minimum of 30 matches, ranked by average combined yellow cards per game — "
        "useful for context, though we don't attribute causality (referees are also assigned to bigger/tighter games)."
    )

# ------------------------------------------------------------------ #
# What drives outcomes — quick feature importance
# ------------------------------------------------------------------ #
section_title("What Statistically Drives a Home Win?")
X, y = prepare_training_frame(df, "FTR")
if len(X) > 100:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder

    enc = LabelEncoder()
    y_enc = enc.fit_transform(y)
    rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
    rf.fit(X, y_enc)
    importance = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    st.plotly_chart(viz.feature_importance_bar(importance, "Random Forest Feature Importance — Match Result"),
                     use_container_width=True)
    top_feat = importance.index[0]
    insight_box(
        f"**{top_feat}** is the single strongest predictor of match result among the engineered features here "
        "(Elo ratings and rolling form). This isn't causal proof, but it does confirm that recent form and "
        "long-run team strength both carry real predictive signal — visit Prediction Center to use this live."
    )
else:
    st.info("Not enough matches with complete feature history to compute this yet.")

# ------------------------------------------------------------------ #
# Most/least disciplined teams
# ------------------------------------------------------------------ #
if {"HY", "AY"}.issubset(df.columns):
    section_title("Discipline League")
    yellows_home = df.groupby("HomeTeam")["HY"].sum()
    yellows_away = df.groupby("AwayTeam")["AY"].sum()
    total_yellows = (yellows_home.add(yellows_away, fill_value=0)).sort_values(ascending=False)
    st.bar_chart(total_yellows.head(15))
    insight_box("Total yellow cards accumulated across all recorded matches, home and away combined.")
