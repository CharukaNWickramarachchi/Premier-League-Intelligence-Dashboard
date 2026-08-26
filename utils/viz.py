"""Shared Plotly figure builders + a consistent dark theme applied to every
chart in the app. Centralizing this keeps every page visually consistent."""
from __future__ import annotations

from typing import List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PLI_COLORWAY = ["#00ff85", "#7b2ff7", "#ffb020", "#38bdf8", "#ff5c8a", "#f5d76e", "#4ade80", "#a78bfa"]

TEMPLATE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.03)",
    font=dict(color="#eef1f8", family="Inter, -apple-system, sans-serif"),
    colorway=PLI_COLORWAY,
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=30, r=20, t=50, b=30),
)


def style_fig(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(**TEMPLATE_LAYOUT, height=height)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.12)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.12)")
    return fig


def goals_timeline(df: pd.DataFrame, freq: str = "ME") -> go.Figure:
    ts = df.set_index("Date").resample(freq)["TotalGoals"].mean().reset_index()
    fig = px.line(ts, x="Date", y="TotalGoals", markers=True, title="Average Goals per Match Over Time")
    return style_fig(fig)


def result_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["FTR"].value_counts().rename({"H": "Home Win", "D": "Draw", "A": "Away Win"})
    fig = px.pie(values=counts.values, names=counts.index, hole=0.45, title="Match Outcome Split")
    return style_fig(fig, height=380)


def team_radar(stats: pd.Series, title: str) -> go.Figure:
    categories = list(stats.index)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=stats.values, theta=categories, fill="toself", name=title))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, title=title)
    return style_fig(fig, height=440)


def correlation_heatmap(corr: pd.DataFrame, title: str = "Correlation Matrix") -> go.Figure:
    fig = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdYlGn", zmin=-1, zmax=1, title=title, aspect="auto"
    )
    return style_fig(fig, height=520)


def scatter_matrix(df: pd.DataFrame, dims: List[str], color: Optional[str] = None) -> go.Figure:
    fig = px.scatter_matrix(df, dimensions=dims, color=color, title="Scatter Matrix")
    return style_fig(fig, height=650)


def treemap_by(df: pd.DataFrame, path: List[str], values: str, title: str) -> go.Figure:
    fig = px.treemap(df, path=path, values=values, title=title, color=values, color_continuous_scale="Viridis")
    return style_fig(fig, height=520)


def sunburst_by(df: pd.DataFrame, path: List[str], values: str, title: str) -> go.Figure:
    fig = px.sunburst(df, path=path, values=values, title=title, color=values, color_continuous_scale="Plasma")
    return style_fig(fig, height=520)


def bubble_chart(df: pd.DataFrame, x: str, y: str, size: str, color: str, hover_name: str, title: str) -> go.Figure:
    fig = px.scatter(df, x=x, y=y, size=size, color=color, hover_name=hover_name, title=title, size_max=40)
    return style_fig(fig, height=480)


def violin_by_team(long_df: pd.DataFrame, y: str, title: str) -> go.Figure:
    fig = px.violin(long_df, x="Team", y=y, box=True, points=False, title=title)
    fig.update_xaxes(tickangle=45)
    return style_fig(fig, height=480)


def box_by(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = px.box(df, x=x, y=y, title=title)
    fig.update_xaxes(tickangle=45)
    return style_fig(fig, height=460)


def rolling_form_line(long_df: pd.DataFrame, team: str) -> go.Figure:
    team_df = long_df[long_df["Team"] == team].sort_values("Date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=team_df["Date"], y=team_df["Form5"], mode="lines", name="Form (last 5)"))
    fig.add_trace(go.Scatter(x=team_df["Date"], y=team_df["Form10"], mode="lines", name="Form (last 10)"))
    fig.update_layout(title=f"{team} — Rolling Form")
    return style_fig(fig, height=420)


def elo_line(df: pd.DataFrame, team: str) -> go.Figure:
    home = df[df["HomeTeam"] == team][["Date", "EloHome"]].rename(columns={"EloHome": "Elo"})
    away = df[df["AwayTeam"] == team][["Date", "EloAway"]].rename(columns={"EloAway": "Elo"})
    combined = pd.concat([home, away]).sort_values("Date")
    fig = px.line(combined, x="Date", y="Elo", title=f"{team} — Elo Rating History")
    return style_fig(fig, height=420)


def heatmap_team_form(long_df: pd.DataFrame, teams: List[str], window: int = 5) -> go.Figure:
    col = "Form5" if window == 5 else "Form10"
    pivot_rows = []
    for team in teams:
        sub = long_df[long_df["Team"] == team].sort_values("Date").tail(20)
        pivot_rows.append(sub[col].tolist()[-20:])
    max_len = max((len(r) for r in pivot_rows), default=0)
    padded = [[None] * (max_len - len(r)) + r for r in pivot_rows]
    fig = px.imshow(
        padded,
        labels=dict(x="Recent Matches →", y="Team", color=f"Pts (last {window})"),
        y=teams,
        color_continuous_scale="RdYlGn",
        title=f"Team Form Heatmap (rolling {window}-match points)",
        aspect="auto",
    )
    return style_fig(fig, height=max(320, 40 * len(teams)))


def confusion_matrix_heatmap(cm_df: pd.DataFrame, title: str = "Confusion Matrix") -> go.Figure:
    fig = px.imshow(
        cm_df, text_auto=True, color_continuous_scale="Blues", title=title,
        labels=dict(x="Predicted", y="Actual", color="Count"),
    )
    return style_fig(fig, height=420)


def roc_curve_fig(fpr, tpr, auc: float, title: str = "ROC Curve") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"ROC (AUC={auc:.3f})", line=dict(width=3)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random", line=dict(dash="dash", color="gray")))
    fig.update_layout(title=title, xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
    return style_fig(fig, height=420)


def feature_importance_bar(importance: pd.Series, title: str = "Feature Importance") -> go.Figure:
    fig = px.bar(
        importance.sort_values(ascending=True), orientation="h", title=title,
        labels={"value": "Relative importance", "index": "Feature"},
    )
    return style_fig(fig, height=max(320, 35 * len(importance)))


def model_comparison_bar(results_df: pd.DataFrame, metric: str) -> go.Figure:
    fig = px.bar(
        results_df.sort_values(metric, ascending=False), x="Model", y=metric, color="Model",
        title=f"Model Comparison — {metric}",
    )
    return style_fig(fig, height=440)


def pca_scatter(components: pd.DataFrame, clusters: Optional[pd.Series] = None) -> go.Figure:
    plot_df = components.copy()
    plot_df["Team"] = plot_df.index
    color = None
    if clusters is not None:
        plot_df["Cluster"] = clusters.reindex(plot_df.index).astype(str)
        color = "Cluster"
    fig = px.scatter(
        plot_df, x="PC1", y="PC2", text="Team", color=color, title="PCA — Team Clustering (2 components)"
    )
    fig.update_traces(textposition="top center")
    return style_fig(fig, height=560)


def animated_goals_trend(df: pd.DataFrame) -> go.Figure:
    season_avg = df.groupby(["SeasonLabel", "SeasonSortKey"])["TotalGoals"].mean().reset_index()
    season_avg = season_avg.sort_values("SeasonSortKey")
    fig = px.bar(
        season_avg, x="SeasonLabel", y="TotalGoals", title="Average Goals per Match by Season",
        color="TotalGoals", color_continuous_scale="Viridis",
    )
    fig.update_xaxes(tickangle=45)
    return style_fig(fig, height=440)
