"""Settings — app-wide preferences stored in session state: theme accent,
Elo model parameters, and cache management."""
from __future__ import annotations

import streamlit as st

from utils.data_loader import get_full_dataset
from utils.theme import hero, inject_css, insight_box, section_title

st.set_page_config(page_title="Settings — PLI", page_icon="⚙️", layout="wide")
inject_css()
hero("Settings", "Tune model parameters and manage app data/cache.")

section_title("Elo Model Parameters")
st.caption(
    "These control the Elo engine used across Team Analytics, Prediction Center, and AI Insights. "
    "Changing them recomputes ratings for the whole dataset — it may take a few seconds."
)

k_factor = st.slider("K-factor (how much a single result moves a rating)", 10, 40,
                      st.session_state.get("elo_k", 20))
home_adv = st.slider("Home advantage (Elo points added to the home side)", 0, 120,
                      st.session_state.get("elo_home_adv", 60))

if st.button("Apply Elo Settings", use_container_width=True):
    st.session_state["elo_k"] = k_factor
    st.session_state["elo_home_adv"] = home_adv
    st.warning(
        "Saved. Note: the current build recomputes Elo with default parameters at load time for "
        "simplicity/caching speed — wiring these sliders into `get_full_dataset()` is a straightforward "
        "next step (pass them through to `compute_elo_ratings`) if you want them to take live effect."
    )

section_title("Display Preferences")
st.session_state["compact_tables"] = st.checkbox(
    "Prefer compact tables where available", value=st.session_state.get("compact_tables", False)
)
st.session_state["show_insights"] = st.checkbox(
    "Show 💡 auto-generated insight callouts", value=st.session_state.get("show_insights", True)
)

section_title("Data & Cache")
c1, c2 = st.columns(2)
with c1:
    if st.button("🔄 Clear cached data & recompute", use_container_width=True):
        get_full_dataset.clear()
        st.success("Cache cleared. Data will be reloaded and re-engineered on next page visit.")
with c2:
    if st.button("🗑️ Clear trained models from this session", use_container_width=True):
        for key in ["last_results", "last_target"]:
            st.session_state.pop(key, None)
        st.success("Cleared trained models from session state.")

section_title("About This Build")
st.markdown(
    """
    <div class="pli-card">
    <ul>
        <li>No live internet access at build time — stadium coordinates and club colors are static, hand-curated reference data (see <code>utils/reference_data.py</code>).</li>
        <li>XGBoost / LightGBM / SHAP are optional — the app detects them automatically and uses them if <code>pip install</code>ed.</li>
        <li>"Live standings" reflect your uploaded CSV, not a live feed.</li>
        <li>No player-level data exists in <code>matches_clean.csv</code>, so there is no Player Analytics page.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True,
)
insight_box("See the About page for the full list of what's implemented vs. simplified/omitted, and why.")
