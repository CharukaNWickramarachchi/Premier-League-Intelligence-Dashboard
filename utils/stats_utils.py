"""
Statistical / data-science toolkit for the Statistics page: PCA, KMeans,
hierarchical clustering, outlier detection, hypothesis testing, ANOVA,
correlation, simple linear regression, z-scores and percentiles.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


def build_team_feature_matrix(all_time_table: pd.DataFrame) -> pd.DataFrame:
    """Turn the all-time table into a numeric feature matrix suitable for
    PCA / clustering (one row per team)."""
    feats = all_time_table.set_index("Team")[["Pld", "W", "D", "L", "GF", "GA", "GD", "Pts", "PPG"]]
    return feats


def run_pca(feature_df: pd.DataFrame, n_components: int = 2) -> Dict[str, object]:
    scaler = StandardScaler()
    scaled = scaler.fit_transform(feature_df.values)
    n_components = min(n_components, feature_df.shape[1])
    pca = PCA(n_components=n_components, random_state=42)
    components = pca.fit_transform(scaled)
    comp_df = pd.DataFrame(
        components, index=feature_df.index, columns=[f"PC{i+1}" for i in range(n_components)]
    )
    loadings = pd.DataFrame(
        pca.components_.T, index=feature_df.columns, columns=[f"PC{i+1}" for i in range(n_components)]
    )
    return {
        "components": comp_df,
        "explained_variance_ratio": pca.explained_variance_ratio_,
        "loadings": loadings,
    }


def run_kmeans(feature_df: pd.DataFrame, n_clusters: int = 4, random_state: int = 42) -> pd.Series:
    scaler = StandardScaler()
    scaled = scaler.fit_transform(feature_df.values)
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = km.fit_predict(scaled)
    return pd.Series(labels, index=feature_df.index, name="Cluster")


def run_hierarchical(feature_df: pd.DataFrame, n_clusters: int = 4) -> pd.Series:
    scaler = StandardScaler()
    scaled = scaler.fit_transform(feature_df.values)
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
    labels = model.fit_predict(scaled)
    return pd.Series(labels, index=feature_df.index, name="Cluster")


def detect_outliers_zscore(series: pd.Series, threshold: float = 2.5) -> pd.DataFrame:
    z = (series - series.mean()) / series.std(ddof=0)
    out = pd.DataFrame({"value": series, "zscore": z})
    out["is_outlier"] = out["zscore"].abs() > threshold
    return out.sort_values("zscore", ascending=False)


def detect_outliers_iqr(series: pd.Series) -> pd.DataFrame:
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out = pd.DataFrame({"value": series})
    out["is_outlier"] = (series < lower) | (series > upper)
    return out, (lower, upper)


def percentile_rank(series: pd.Series) -> pd.Series:
    return series.rank(pct=True) * 100


def two_sample_ttest(sample_a: pd.Series, sample_b: pd.Series) -> Dict[str, float]:
    t_stat, p_val = stats.ttest_ind(sample_a.dropna(), sample_b.dropna(), equal_var=False)
    return {"t_stat": float(t_stat), "p_value": float(p_val)}


def one_way_anova(*samples: pd.Series) -> Dict[str, float]:
    clean = [s.dropna() for s in samples if len(s.dropna()) > 0]
    f_stat, p_val = stats.f_oneway(*clean)
    return {"f_stat": float(f_stat), "p_value": float(p_val)}


def chi_square_independence(contingency: pd.DataFrame) -> Dict[str, float]:
    chi2, p, dof, _ = stats.chi2_contingency(contingency)
    return {"chi2": float(chi2), "p_value": float(p), "dof": int(dof)}


def correlation_matrix(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    return df[columns].corr(method="pearson")


def simple_linear_regression(x: pd.Series, y: pd.Series) -> Dict[str, float]:
    mask = x.notna() & y.notna()
    X = x[mask].values.reshape(-1, 1)
    Y = y[mask].values
    model = LinearRegression()
    model.fit(X, Y)
    r2 = model.score(X, Y)
    return {
        "slope": float(model.coef_[0]),
        "intercept": float(model.intercept_),
        "r_squared": float(r2),
    }


def interpret_p_value(p_value: float, alpha: float = 0.05) -> str:
    if np.isnan(p_value):
        return "Not enough data to draw a conclusion."
    if p_value < alpha:
        return f"Statistically significant (p = {p_value:.4f} < {alpha}) — reject the null hypothesis."
    return f"Not statistically significant (p = {p_value:.4f} ≥ {alpha}) — cannot reject the null hypothesis."
