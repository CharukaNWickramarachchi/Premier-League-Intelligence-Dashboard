"""Downloads — export the filtered dataset, season/all-time tables, and any
trained model results as CSV or Excel."""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from components.filters import global_filters
from utils.data_loader import compute_all_time_table, compute_season_table, get_full_dataset, get_season_list
from utils.theme import hero, inject_css, insight_box, section_title

st.set_page_config(page_title="Downloads — PLI", page_icon="⬇️", layout="wide")
inject_css()
hero("Downloads", "Export any view in this app as CSV or Excel for your own reports.")

df = get_full_dataset()
filtered = global_filters(df)


def _to_excel_bytes(sheets: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=name[:31], index=True)
    return buf.getvalue()


section_title("Filtered Match Data")
st.caption(f"{len(filtered):,} matches currently match your sidebar filters.")
display_cols = [c for c in [
    "Date", "SeasonLabel", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
    "HS", "AS", "HST", "AST", "HC", "AC", "HY", "AY", "HR", "AR", "Referee",
    "EloHome", "EloAway", "HomeForm5", "AwayForm5",
] if c in filtered.columns]
export_df = filtered[display_cols]

c1, c2 = st.columns(2)
with c1:
    st.download_button(
        "⬇️ Download filtered matches (CSV)",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="pli_filtered_matches.csv",
        mime="text/csv",
        use_container_width=True,
    )
with c2:
    st.download_button(
        "⬇️ Download filtered matches (Excel)",
        data=_to_excel_bytes({"Matches": export_df}),
        file_name="pli_filtered_matches.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

st.dataframe(export_df.head(100), use_container_width=True, height=350)
insight_box("Preview shows the first 100 rows — the download contains every row in your current filter.")

section_title("League Tables")
seasons = get_season_list(df)
season_choice = st.selectbox("Season table to export", seasons, index=len(seasons) - 1,
                              format_func=lambda s: s.replace("season_", "").replace("_", "/"))
season_table = compute_season_table(df, season_choice)
all_time_table = compute_all_time_table(df)

c3, c4 = st.columns(2)
with c3:
    st.download_button(
        f"⬇️ Season table ({season_choice}) — CSV",
        data=season_table.to_csv().encode("utf-8"),
        file_name=f"pli_{season_choice}_table.csv",
        mime="text/csv",
        use_container_width=True,
    )
with c4:
    st.download_button(
        "⬇️ All-time table — CSV",
        data=all_time_table.to_csv().encode("utf-8"),
        file_name="pli_all_time_table.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.download_button(
    "⬇️ Both tables — Excel workbook",
    data=_to_excel_bytes({"Season Table": season_table, "All-Time Table": all_time_table}),
    file_name="pli_league_tables.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

section_title("Trained Model Results")
results = st.session_state.get("last_results")
if results:
    rows = []
    for name, r in results.items():
        rows.append({"Model": name, "Accuracy": r.accuracy, "Precision": r.precision,
                     "Recall": r.recall, "F1": r.f1, "CV Mean": r.cv_mean, "CV Std": r.cv_std})
    results_df = pd.DataFrame(rows)
    st.dataframe(results_df, use_container_width=True)
    st.download_button(
        "⬇️ Model comparison results — CSV",
        data=results_df.to_csv(index=False).encode("utf-8"),
        file_name="pli_model_results.csv",
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.info("No trained models yet this session — visit Prediction Center → Train & Compare Models first.")
