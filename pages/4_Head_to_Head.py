"""Head-to-Head — pick any two clubs and compare their full history against
each other, including a timeline and win-share breakdown."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from utils.data_loader import get_full_dataset, get_team_list, head_to_head
from utils.reference_data import get_logo_path, get_team_color
from utils.theme import hero, inject_css, insight_box, section_title
from utils import viz

st.set_page_config(page_title="Head-to-Head — PLI", page_icon="⚔️", layout="wide")
inject_css()
hero("Head-to-Head", "Every meeting between two clubs, side by side.")

df = get_full_dataset()
teams = get_team_list(df)

c1, c2 = st.columns(2)
with c1:
    team_a = st.selectbox("Team A", teams, index=teams.index("Arsenal") if "Arsenal" in teams else 0)
with c2:
    default_b = "Chelsea" if "Chelsea" in teams and "Chelsea" != team_a else teams[1]
    team_b = st.selectbox("Team B", [t for t in teams if t != team_a],
                           index=[t for t in teams if t != team_a].index(default_b) if default_b in teams and default_b != team_a else 0)

matches = head_to_head(df, team_a, team_b)

if matches.empty:
    st.warning(f"{team_a} and {team_b} have never met within the current dataset.")
    st.stop()

a_wins = ((matches["HomeTeam"] == team_a) & (matches["FTR"] == "H")).sum() + (
    (matches["AwayTeam"] == team_a) & (matches["FTR"] == "A")
).sum()
b_wins = ((matches["HomeTeam"] == team_b) & (matches["FTR"] == "H")).sum() + (
    (matches["AwayTeam"] == team_b) & (matches["FTR"] == "A")
).sum()
draws = (matches["FTR"] == "D").sum()

section_title(f"{team_a} vs {team_b} — {len(matches)} Meetings")

logo_a, vs_col, logo_b = st.columns([1, 0.4, 1], vertical_alignment="center")

with logo_a:
    path_a = get_logo_path(team_a)
    if path_a:
        st.image(path_a)

with vs_col:
    st.markdown(
        """
        <div style="
            text-align: center;
            font-size: 4rem;
            font-weight: 900;
            line-height: 1;
            color: #ffffff;
            opacity: 0.85;
        ">
            VS
        </div>
        """,
        unsafe_allow_html=True,
    )

with logo_b:
    path_b = get_logo_path(team_b)
    if path_b:
        st.image(path_b)

k1, k2, k3 = st.columns(3)
k1.metric(f"{team_a} Wins", int(a_wins))
k2.metric("Draws", int(draws))
k3.metric(f"{team_b} Wins", int(b_wins))

fig = px.pie(
    values=[a_wins, draws, b_wins], names=[f"{team_a} Wins", "Draws", f"{team_b} Wins"],
    hole=0.45, title="Head-to-Head Win Share",
    color_discrete_sequence=[get_team_color(team_a), "#a3aac4", get_team_color(team_b)],
)
st.plotly_chart(viz.style_fig(fig, height=400), use_container_width=True)

section_title("Match Timeline")
timeline = matches.copy()
timeline["Scoreline"] = timeline.apply(
    lambda r: f"{r['HomeTeam']} {int(r['FTHG'])}-{int(r['FTAG'])} {r['AwayTeam']}", axis=1
)
fig2 = px.scatter(
    timeline, x="Date", y="TotalGoals", size="TotalGoals", color="FTR", hover_name="Scoreline",
    title="Goals Scored in Each Meeting Over Time",
    color_discrete_map={"H": "#00ff85", "D": "#a3aac4", "A": "#ff5c8a"},
)
st.plotly_chart(viz.style_fig(fig2, height=440), use_container_width=True)

section_title("Full Match List")
st.dataframe(
    timeline[["Date", "SeasonLabel", "Scoreline", "TotalGoals"]].sort_values("Date", ascending=False),
    use_container_width=True,
)

avg_goals = matches["TotalGoals"].mean()
insight_box(
    f"These fixtures have averaged {avg_goals:.2f} goals per match — "
    f"{'notably high-scoring' if avg_goals > df['TotalGoals'].mean() + 0.3 else 'around league average' if abs(avg_goals - df['TotalGoals'].mean()) <= 0.3 else 'tighter/lower-scoring'} "
    "compared to the league-wide average."
)
