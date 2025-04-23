import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
from utils import identify_peaks, create_standard_plot

st.set_page_config(layout="wide")
st.title('🔍 Einzeldatei-Analyse mit Peak-Erkennung')

# --- Default-Werte ---
default_values = {
    "num_peaks": 15,
    "window_size": 7,
    "prominence": 0.3,
    "legend_name": "",
    "x_min": 30,
    "x_max": 100,
    "y_min": 4000,
    "y_max": 520
}

# --- Session-State Initialisierung ---
for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Reset Button ---
if st.button("🔁 Standardwerte wiederherstellen"):
    for key, val in default_values.items():
        st.session_state[key] = val

# --- Datei-Upload ---
uploaded_file = st.file_uploader("Wählen Sie eine CSV-Datei", type=["csv"])

# --- Einstellungen ---
if uploaded_file is not None:
    filename_no_ext = os.path.splitext(uploaded_file.name)[0]
    if not st.session_state.legend_name:
        st.session_state.legend_name = filename_no_ext

    df = pd.read_csv(uploaded_file, skiprows=2, sep=",", names=["Wave number", "Transmission"], header=None)

    col1, col2 = st.columns(2)

    # Linke Spalte: Legende & Peak-Einstellungen
    with col1:
        st.markdown("##### Analyse-Einstellungen")

        row = st.columns([1, 3])
        row[0].markdown("**Name**")
        row[1].text_input("", value=st.session_state.legend_name, key="legend_name", label_visibility="collapsed")

        row = st.columns([1, 3])
        row[0].markdown("**# Peaks**")
        row[1].number_input("", min_value=5, max_value=30, step=1, key="num_peaks", label_visibility="collapsed")

        row = st.columns([1, 3])
        row[0].markdown("**Glättung**")
        row[1].number_input("", min_value=3, max_value=21, step=2, key="window_size", label_visibility="collapsed")

        row = st.columns([1, 3])
        row[0].markdown("**Prominenz**")
        row[1].number_input("", min_value=0.05, max_value=2.0, step=0.1, key="prominence", label_visibility="collapsed")

    # Rechte Spalte: Achsen-Einstellungen
    with col2:
        st.markdown("##### Achsen-Einstellungen")
        row = st.columns([1, 3])
        row[0].markdown("**X-Min**")
        row[1].number_input("", step=10, key="x_min", label_visibility="collapsed")

        row = st.columns([1, 3])
        row[0].markdown("**X-Max**")
        row[1].number_input("", step=10, key="x_max", label_visibility="collapsed")

        row = st.columns([1, 3])
        row[0].markdown("**Y-Min**")
        row[1].number_input("", step=1, key="y_min", label_visibility="collapsed")

        row = st.columns([1, 3])
        row[0].markdown("**Y-Max**")
        row[1].number_input("", step=1, key="y_max", label_visibility="collapsed")

    # --- Peaks berechnen ---
    peak_positions, peak_values, peaks = identify_peaks(
        df,
        st.session_state.num_peaks,
        st.session_state.window_size,
        st.session_state.prominence
    )

    peaks_df = pd.DataFrame({
        "Wave number (cm⁻¹)": peak_positions,
        "Transmission (%)": peak_values
    })

    # --- Plot ---
    fig = create_standard_plot(
        df,
        peaks,
        peak_positions,
        peak_values,
        st.session_state.legend_name,
        st.session_state.y_min,
        st.session_state.y_max,
        st.session_state.x_min,
        st.session_state.x_max
    )

    st.pyplot(fig)

    # --- Tabelle der Peaks ---
    st.subheader('Identifizierte Peaks:')
    st.write(peaks_df.reset_index(drop=True).rename_axis(' ').set_index(pd.RangeIndex(1, len(peaks_df) + 1)))

    # --- Download Plot & CSV ---
    plot_buffer = BytesIO()
    fig.savefig(plot_buffer, format="png", dpi=300)
    plot_buffer.seek(0)

    csv_buffer = BytesIO()
    peaks_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    st.download_button("📥 Download Plot (PNG)", data=plot_buffer, file_name=f"{filename_no_ext}_plot.png", mime="image/png")
    st.download_button("📥 Download Peaks (CSV)", data=csv_buffer, file_name=f"{filename_no_ext}_peaks.csv", mime="text/csv")
