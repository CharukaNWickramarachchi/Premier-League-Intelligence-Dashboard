"""Team Analytics — deep dive into a single club: form, Elo history,
attack/defense radar, home vs away split, and disciplinary record."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.data_loader import get_full_dataset, get_team_list, team_long_format
from utils.reference_data import (
    get_logo_path,
    get_stadium,
    get_stadium_image_path,
    get_team_color,
)
from utils.theme import hero, image_to_data_uri, inject_css, insight_box, section_title
from utils import viz


# ------------------------------------------------------------------ #
# PAGE CONFIG
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="Team Analytics — PLI",
    page_icon="📊",
    layout="wide",
)

inject_css()

hero(
    "Team Analytics",
    "A 360° statistical profile for any club in the dataset.",
)


# ------------------------------------------------------------------ #
# LOAD DATA
# ------------------------------------------------------------------ #
df = get_full_dataset()
teams = get_team_list(df)

team = st.selectbox(
    "Choose a team",
    teams,
    index=teams.index("Arsenal") if "Arsenal" in teams else 0,
)

team_matches = df[(df["HomeTeam"] == team) | (df["AwayTeam"] == team)]
long_df = team_long_format(df)
team_long = long_df[long_df["Team"] == team]


# ------------------------------------------------------------------ #
# TEAM IDENTITY
# ------------------------------------------------------------------ #
color = get_team_color(team)
logo_path = get_logo_path(team)
stadium = get_stadium(team)
stadium_img_path = get_stadium_image_path(team)

match_count = len(team_matches)
season_count = team_matches["season"].nunique()

# A plain filesystem path can't be used inside a raw <img src="..."> tag --
# the browser rendering the markdown has no access to your local disk. We
# convert both images to base64 data URIs so they can actually be embedded.
# If a file is missing, these are simply None and the HTML below skips them.
logo_data_uri = image_to_data_uri(logo_path)
stadium_data_uri = image_to_data_uri(stadium_img_path)


# ------------------------------------------------------------------ #
# IMPORTANT — WHY THIS FILE LOOKS "FLAT" INSTEAD OF NICELY INDENTED
# ------------------------------------------------------------------ #
# Streamlit's st.markdown() runs your string through a Markdown parser
# BEFORE injecting the HTML. Markdown's rule is: any line indented 4+
# spaces gets treated as a *code block* and printed as literal text --
# exactly the "raw <div style=...> text with a copy button" bug you saw
# in your screenshot. It doesn't matter that unsafe_allow_html=True is
# set; the line never reaches the HTML parser at all.
#
# The fix is simple but easy to break by accident: every line inside an
# HTML string passed to st.markdown must start at column 0 (no leading
# spaces), even though that looks ugly compared to normal Python
# indentation. Every HTML string below follows that rule strictly.
# ------------------------------------------------------------------ #

CARD_CSS = """
<style>
.team-identity-wrapper {
display: flex;
align-items: center;
justify-content: space-between;
gap: 30px;
margin-top: 20px;
margin-bottom: 25px;
padding: 25px 30px;
border-radius: 20px;
background: linear-gradient(135deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
border: 1px solid rgba(255,255,255,0.08);
box-shadow: 0 10px 30px rgba(0,0,0,0.18);
flex-wrap: wrap;
}
.team-main-info {
display: flex;
align-items: center;
gap: 28px;
flex: 1;
min-width: 280px;
}
.team-logo-box {
width: 250px;
height: 250px;
min-width:250px;
display: flex;
align-items: center;
justify-content: center;
border-radius: 24px;
background: rgba(255,255,255,0.04);
border: 1px solid rgba(255,255,255,0.08);
padding: 12px;
box-sizing: border-box;
overflow: hidden;
}
.team-logo-box img {
max-width: 100%;
max-height: 100%;
object-fit: contain;
}
.team-logo-initials {
width: 100%;
height: 100%;
border-radius: 18px;
display: flex;
align-items: center;
justify-content: center;
font-size: 42px;
font-weight: 800;
color: white;
}
.team-text {
display: flex;
flex-direction: column;
justify-content: center;
padding-left: 22px;
}
.team-name {
font-size: 42px;
font-weight: 800;
line-height: 1.1;
margin: 0 0 12px 0;
color: #ffffff;
letter-spacing: -1px;
}
.team-description {
font-size: 16px;
line-height: 1.5;
color: rgba(255,255,255,0.65);
}
.team-highlight {
color: #ffffff;
font-weight: 700;
}
.stadium-card {
width: 300px;
min-width: 260px;
border-radius: 16px;
overflow: hidden;
background: rgba(255,255,255,0.035);
border: 1px solid rgba(255,255,255,0.08);
}
.stadium-image {
width: 100%;
height: 145px;
object-fit: cover;
display: block;
}
.stadium-info {
padding: 12px 15px 14px 15px;
}
.stadium-title {
font-size: 14px;
font-weight: 700;
color: #ffffff;
margin-bottom: 5px;
}
.stadium-details {
font-size: 12px;
line-height: 1.5;
color: rgba(255,255,255,0.60);
}
@media (max-width: 900px) {
.team-identity-wrapper { flex-direction: column; align-items: stretch; }
.stadium-card { width: 100%; min-width: 100%; }
.team-main-info { justify-content: center; }
}
@media (max-width: 600px) {
.team-main-info { flex-direction: column; text-align: center; }
.team-name { font-size: 32px; }
.team-logo-box { width: 130px; height: 130px; min-width: 130px; }
}
</style>
"""
st.markdown(CARD_CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------ #
# TEAM HEADER CARD
# Every piece below is built as a flat string with NO leading spaces
# on any line, then joined with "" (not with newlines+indentation),
# so Markdown can never mistake it for a code block.
# ------------------------------------------------------------------ #
if logo_data_uri:
    logo_html = f'<img src="{logo_data_uri}" alt="{team} logo">'
else:
    initials = "".join(word[0] for word in team.split()[:2]).upper()
    logo_html = f'<div class="team-logo-initials" style="background:{color};">{initials}</div>'

if stadium:
    if stadium_data_uri:
        stadium_image_html = f'<img class="stadium-image" src="{stadium_data_uri}" alt="{stadium["stadium"]}">'
    else:
        stadium_image_html = ""
    stadium_card_html = (
        '<div class="stadium-card">'
        + stadium_image_html
        + '<div class="stadium-info">'
        + f'<div class="stadium-title">🏟️ {stadium["stadium"]}</div>'
        + f'<div class="stadium-details">{stadium["city"]} &nbsp;•&nbsp; Capacity ≈ {stadium["capacity"]:,}</div>'
        + "</div>"
        + "</div>"
    )
else:
    stadium_card_html = ""

card_html = (
    '<div class="team-identity-wrapper">'
    + '<div class="team-main-info">'
    + f'<div class="team-logo-box">{logo_html}</div>'
    + '<div class="team-text" style="border-left:4px solid ' + color + ';">'
    + f'<div class="team-name">{team}</div>'
    + '<div class="team-description">'
    + f'<span class="team-highlight">{match_count:,}</span> matches across '
    + f'<span class="team-highlight">{season_count}</span> seasons in the dataset.'
    + "</div>"
    + "</div>"
    + "</div>"
    + stadium_card_html
    + "</div>"
)
st.markdown(card_html, unsafe_allow_html=True)


# ------------------------------------------------------------------ #
# KPIs
# ------------------------------------------------------------------ #
section_title("Season-Blind Career Snapshot")

wins = (team_long["Result"] == "W").sum()
draws = (team_long["Result"] == "D").sum()
losses = (team_long["Result"] == "L").sum()
goals_for = team_long["GoalsFor"].sum()
goals_against = team_long["GoalsAgainst"].sum()
points = team_long["Points"].sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Wins", int(wins))
k2.metric("Draws", int(draws))
k3.metric("Losses", int(losses))
k4.metric("Goals For", int(goals_for))
k5.metric("Goals Against", int(goals_against))
k6.metric("Points", int(points))


# ------------------------------------------------------------------ #
# FORM + ELO
# ------------------------------------------------------------------ #
section_title("Form & Rating Trajectory")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(viz.rolling_form_line(long_df, team), use_container_width=True)
with c2:
    st.plotly_chart(viz.elo_line(df, team), use_container_width=True)

insight_box(
    f"{team}'s Elo rating reflects opponent strength and margin of victory, "
    "not just points — a team can gain rating even in a loss against a much stronger side."
)


# ------------------------------------------------------------------ #
# RADAR: ATTACK / DEFENSE PROFILE
# ------------------------------------------------------------------ #
section_title("Attack / Defense Radar (vs league average)")

league_avg = pd.Series({
    "Goals For / Match": long_df["GoalsFor"].mean(),
    "Goals Against / Match": long_df["GoalsAgainst"].mean(),
    "Win Rate %": (long_df["Result"] == "W").mean() * 100,
    "Points / Match": long_df["Points"].mean(),
})

team_profile = pd.Series({
    "Goals For / Match": team_long["GoalsFor"].mean(),
    "Goals Against / Match": team_long["GoalsAgainst"].mean(),
    "Win Rate %": (team_long["Result"] == "W").mean() * 100,
    "Points / Match": team_long["Points"].mean(),
})

normalized = (team_profile / league_avg.replace(0, 1)) * 100

st.plotly_chart(
    viz.team_radar(normalized, f"{team} vs League Average (100 = league avg)"),
    use_container_width=True,
)


# ------------------------------------------------------------------ #
# HOME VS AWAY SPLIT
# ------------------------------------------------------------------ #
section_title("Home vs Away Split")

split = team_long.groupby("Venue").agg(
    Matches=("Points", "count"),
    Wins=("Result", lambda s: (s == "W").sum()),
    Draws=("Result", lambda s: (s == "D").sum()),
    Losses=("Result", lambda s: (s == "L").sum()),
    GoalsFor=("GoalsFor", "sum"),
    GoalsAgainst=("GoalsAgainst", "sum"),
    Points=("Points", "sum"),
).reset_index()

st.dataframe(split, use_container_width=True)


# ------------------------------------------------------------------ #
# DISCIPLINARY RECORD
# ------------------------------------------------------------------ #
if {"HY", "AY", "HR", "AR"}.issubset(df.columns):
    section_title("Disciplinary Record")

    yellows = team_matches.apply(
        lambda r: r["HY"] if r["HomeTeam"] == team else r["AY"], axis=1
    ).sum()
    reds = team_matches.apply(
        lambda r: r["HR"] if r["HomeTeam"] == team else r["AR"], axis=1
    ).sum()

    d1, d2 = st.columns(2)
    d1.metric("Total Yellow Cards", int(yellows))
    d2.metric("Total Red Cards", int(reds))