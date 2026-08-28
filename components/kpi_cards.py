"""Reusable KPI tile grid used on the Home Dashboard and other pages."""
from __future__ import annotations

from typing import List, Optional, Tuple

import streamlit as st


def kpi_grid(items: List[Tuple[str, str, Optional[str]]], columns: int = 4) -> None:
    """
    items: list of (label, value, delta_or_none) tuples.
    Renders as a responsive grid of glass KPI tiles.
    """
    cols = st.columns(columns)
    for i, (label, value, delta) in enumerate(items):
        with cols[i % columns]:
            delta_html = f'<div class="pli-kpi-delta">{delta}</div>' if delta else ""
            st.markdown(
                f"""
                <div class="pli-kpi">
                    <div class="pli-kpi-label">{label}</div>
                    <div class="pli-kpi-value">{value}</div>
                    {delta_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
