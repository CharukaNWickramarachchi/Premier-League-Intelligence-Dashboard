"""Statistics — a proper data-science toolkit: PCA, KMeans / hierarchical
clustering of teams, outlier detection, hypothesis testing (t-test, ANOVA,
chi-square), correlation, simple regression, z-scores and percentiles."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_loader import compute_all_time_table, get_full_dataset
from utils.stats_utils import (
    build_team_feature_matrix,
    chi_square_independence,
    correlation_matrix,
    detect_outliers_iqr,
    detect_outliers_zscore,
    interpret_p_value,
    one_way_anova,
    percentile_rank,
    run_hierarchical,
    run_kmeans,
    run_pca,
    simple_linear_regression,
    two_sample_ttest,
)
from utils.theme import hero, inject_css, insight_box, section_title
from utils import viz

st.set_page_config(page_title="Statistics — PLI", page_icon="📐", layout="wide")
inject_css()
hero("Statistics", "PCA, clustering, hypothesis testing and classic descriptive statistics on the full dataset.")

df = get_full_dataset()
all_time = compute_all_time_table(df)
feature_matrix = build_team_feature_matrix(all_time)

tab1, tab2, tab3, tab4 = st.tabs(["🧬 PCA & Clustering", "📈 Correlation & Regression", "🧪 Hypothesis Testing", "🎯 Outliers & Percentiles"])

# ============================================================ #
with tab1:
    section_title("Principal Component Analysis")
    pca_result = run_pca(feature_matrix, n_components=2)
    variance = pca_result["explained_variance_ratio"]
    st.caption(f"PC1 explains {variance[0]*100:.1f}% of variance, PC2 explains {variance[1]*100:.1f}% "
               f"({(variance[0]+variance[1])*100:.1f}% combined).")

    cluster_method = st.radio("Clustering method", ["KMeans", "Hierarchical (Ward linkage)"], horizontal=True)
    n_clusters = st.slider("Number of clusters", 2, 8, 4)
    clusters = (
        run_kmeans(feature_matrix, n_clusters) if cluster_method == "KMeans"
        else run_hierarchical(feature_matrix, n_clusters)
    )
    st.plotly_chart(viz.pca_scatter(pca_result["components"], clusters), use_container_width=True)

    section_title("What Drives Each Principal Component")
    st.dataframe(pca_result["loadings"], use_container_width=True)
    insight_box(
        "Loadings show how much each raw stat (Pld, W, D, L, GF, GA, GD, Pts, PPG) contributes to each "
        "component. PC1 is almost always a general 'overall strength' axis; PC2 typically separates "
        "attacking vs defensive profiles."
    )

    section_title("Cluster Membership")
    cluster_df = pd.DataFrame({"Team": clusters.index, "Cluster": clusters.values}).sort_values("Cluster")
    st.dataframe(cluster_df, use_container_width=True, height=350)

# ============================================================ #
with tab2:
    section_title("Correlation Matrix — Match Stats")
    numeric_candidates = [c for c in ["FTHG", "FTAG", "TotalGoals", "HS", "AS", "HST", "AST",
                                        "HC", "AC", "HF", "AF", "HY", "AY", "EloHome", "EloAway"] if c in df.columns]
    chosen = st.multiselect("Columns to correlate", numeric_candidates, default=numeric_candidates[:8])
    if len(chosen) >= 2:
        corr = correlation_matrix(df, chosen)
        st.plotly_chart(viz.correlation_heatmap(corr), use_container_width=True)

        section_title("Simple Linear Regression")
        c1, c2 = st.columns(2)
        x_col = c1.selectbox("X variable", chosen, index=0)
        y_col = c2.selectbox("Y variable", chosen, index=min(1, len(chosen) - 1))
        reg = simple_linear_regression(df[x_col], df[y_col])
        st.write(f"**{y_col} ≈ {reg['slope']:.3f} × {x_col} + {reg['intercept']:.3f}**  |  R² = {reg['r_squared']:.3f}")
        fig = px.scatter(df, x=x_col, y=y_col, trendline="ols", opacity=0.4,
                          title=f"{y_col} vs {x_col}")
        st.plotly_chart(viz.style_fig(fig, height=460), use_container_width=True)
        insight_box(f"R² of {reg['r_squared']:.3f} means {x_col} explains about {reg['r_squared']*100:.1f}% "
                    f"of the variance in {y_col} on its own — a useful sanity check before trusting any single-variable story.")
    else:
        st.info("Pick at least two columns to correlate.")

# ============================================================ #
with tab3:
    section_title("Two-Sample T-Test: Home Goals vs Away Goals")
    ttest = two_sample_ttest(df["FTHG"], df["FTAG"])
    st.write(f"t = {ttest['t_stat']:.3f}, p = {ttest['p_value']:.5f}")
    insight_box(interpret_p_value(ttest["p_value"]))

    section_title("One-Way ANOVA: Total Goals Across Seasons")
    seasons_sample = df["season"].drop_duplicates().tolist()[-6:]
    groups = [df[df["season"] == s]["TotalGoals"] for s in seasons_sample]
    anova = one_way_anova(*groups)
    st.write(f"F = {anova['f_stat']:.3f}, p = {anova['p_value']:.5f} (last {len(seasons_sample)} seasons)")
    insight_box(interpret_p_value(anova["p_value"]))

    section_title("Chi-Square Test: Referee vs Match Result Independence")
    if "Referee" in df.columns:
        top_refs = df["Referee"].value_counts().head(6).index
        sub = df[df["Referee"].isin(top_refs)]
        contingency = pd.crosstab(sub["Referee"], sub["FTR"])
        chi = chi_square_independence(contingency)
        st.dataframe(contingency, use_container_width=True)
        st.write(f"χ² = {chi['chi2']:.3f}, dof = {chi['dof']}, p = {chi['p_value']:.5f}")
        insight_box(interpret_p_value(chi["p_value"]) + " (Testing whether match outcome distribution is independent of which of the top-6 busiest referees officiated.)")

# ============================================================ #
with tab4:
    section_title("Outlier Detection")
    metric = st.selectbox("Metric", ["TotalGoals", "FTHG", "FTAG"] + (["HS", "AS"] if "HS" in df.columns else []))
    method = st.radio("Method", ["Z-score", "IQR"], horizontal=True)
    if method == "Z-score":
        threshold = st.slider("Z-score threshold", 1.5, 4.0, 2.5, 0.1)
        out = detect_outliers_zscore(df[metric], threshold)
        n_outliers = int(out["is_outlier"].sum())
        st.write(f"**{n_outliers}** matches flagged as outliers on `{metric}` (|z| > {threshold}).")
        st.dataframe(out[out["is_outlier"]].join(df[["Date", "HomeTeam", "AwayTeam"]]).sort_values("zscore", ascending=False).head(20),
                     use_container_width=True)
    else:
        out, bounds = detect_outliers_iqr(df[metric])
        n_outliers = int(out["is_outlier"].sum())
        st.write(f"**{n_outliers}** matches flagged as outliers on `{metric}` (outside [{bounds[0]:.2f}, {bounds[1]:.2f}]).")
        st.dataframe(out[out["is_outlier"]].join(df[["Date", "HomeTeam", "AwayTeam"]]).head(20), use_container_width=True)

    section_title("Percentile Rank")
    pct = percentile_rank(df[metric])
    hist_fig = px.histogram(pct, nbins=30, title=f"Percentile Distribution — {metric}")
    st.plotly_chart(viz.style_fig(hist_fig, height=380), use_container_width=True)
    insight_box(f"Every match's `{metric}` value converted into a percentile (0–100) relative to every other match on record.")
