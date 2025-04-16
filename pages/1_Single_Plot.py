import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
from utils import identify_peaks, create_standard_plot

st.title('🔍 Einzeldatei-Analyse mit Peak-Erkennung')

# Datei-Upload
uploaded_file = st.file_uploader("Wählen Sie eine CSV-Datei", type=["csv"])

# Defaultwerte
default_num_peaks = 15
default_window_size = 7
default_prominence = 0.5

if "num_peaks" not in st.session_state:
    st.session_state.num_peaks = default_num_peaks
if "window_size" not in st.session_state:
    st.session_state.window_size = default_window_size
if "prominence" not in st.session_state:
    st.session_state.prominence = default_prominence

# Reset Button
if st.button("🔁 Standardwerte wiederherstellen"):
    st.session_state.num_peaks = default_num_peaks
    st.session_state.window_size = default_window_size
    st.session_state.prominence = default_prominence
    st.session_state.legend_name = ""

# Wenn Datei geladen ist
if uploaded_file is not None:
    filename_no_ext = os.path.splitext(uploaded_file.name)[0]

    if "legend_name" not in st.session_state or st.session_state.legend_name == "":
        st.session_state.legend_name = filename_no_ext

    df = pd.read_csv(uploaded_file, skiprows=2, sep=",", names=["Wave number", "Transmission"], header=None)

    legend_name = st.text_input("Name in der Legende", value=st.session_state.legend_name, key="legend_name")
    num_peaks = st.slider("Anzahl Peaks", 5, 30, st.session_state.num_peaks, key="num_peaks")
    window_size = st.slider("Glättungsfenster (rolling window)", 3, 21, step=2, value=st.session_state.window_size, key="window_size")
    prominence = st.slider("Prominenzschwelle", 0.1, 2.0, step=0.1, value=st.session_state.prominence, key="prominence")

    x_min = st.number_input("X-Achse Maximum", value=4000, step=10)
    x_max = st.number_input("X-Achse Minimum", value=520, step=10)
    y_min = st.number_input("Y-Achse Minimum", value=30, step=1)
    y_max = st.number_input("Y-Achse Maximum", value=100, step=1)

    # Peaks berechnen
    peak_positions, peak_values, peaks = identify_peaks(df, num_peaks, window_size, prominence)

    peaks_df = pd.DataFrame({
        "Wave number (cm⁻¹)": peak_positions,
        "Transmission (%)": peak_values
    })

    st.subheader('Identifizierte Peaks:')
    st.write(peaks_df.reset_index(drop=True).rename_axis(' ').set_index(pd.RangeIndex(1, len(peaks_df) + 1)))

    # Plot erzeugen
    fig = create_standard_plot(df, peaks, peak_positions, peak_values, legend_name, x_min, x_max, y_min, y_max)
    st.pyplot(fig)


    # Downloads
    plot_buffer = BytesIO()
    fig.savefig(plot_buffer, format="png", dpi=300)
    plot_buffer.seek(0)

    csv_buffer = BytesIO()
    peaks_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    st.download_button("📥 Download Plot (PNG)", data=plot_buffer, file_name=f"{filename_no_ext}_plot.png", mime="image/png")
    st.download_button("📥 Download Peaks (CSV)", data=csv_buffer, file_name=f"{filename_no_ext}_peaks.csv", mime="text/csv")
