import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
from zipfile import ZipFile
from utils import identify_peaks, create_standard_plot

# 📌 Defaultwerte
default_num_peaks = 15
default_window_size = 7
default_prominence = 0.5

st.title("📦 Batch-Analyse & Download")

uploaded_files = st.file_uploader("Mehrere CSV-Dateien hochladen", type=["csv"], accept_multiple_files=True)

with st.expander("🔧 Optionale Einstellungen"):
    num_peaks = st.slider("Anzahl Peaks", 5, 30, default_num_peaks)
    window_size = st.slider("Glättungsfenster", 3, 21, default_window_size, step=2)
    prominence = st.slider("Prominenzschwelle", 0.1, 2.0, default_prominence, step=0.1)
    x_min = st.number_input("X-Achse Maximum", value=4000, step=10)
    x_max = st.number_input("X-Achse Minimum", value=520, step=10)
    y_min = st.number_input("Y-Achse Minimum", value=30, step=1)
    y_max = st.number_input("Y-Achse Maximum", value=100, step=1)

if uploaded_files and st.button("🚀 Alle Dateien auswerten & ZIP herunterladen"):
    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, "w") as zip_file:
        for file in uploaded_files:
            filename_no_ext = os.path.splitext(file.name)[0]

            # CSV laden
            df = pd.read_csv(file, skiprows=2, sep=",", names=["Wave number", "Transmission"], header=None)

            # Analyse durchführen
            peak_positions, peak_values, peak_indices = identify_peaks(df, num_peaks, window_size, prominence)

            # Ergebnisse als CSV
            peaks_df = pd.DataFrame({
                "Wave number (cm⁻¹)": peak_positions,
                "Transmission (%)": peak_values
            })
            csv_bytes = peaks_df.to_csv(index=False).encode("utf-8")
            zip_file.writestr(f"{filename_no_ext}_peaks.csv", csv_bytes)

            # Plot erstellen über util-Funktion
            fig = create_standard_plot(df, peak_indices, peak_positions, peak_values,
                                       legend_name=filename_no_ext,
                                       x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)

            # Plot als PNG speichern
            img_bytes = BytesIO()
            fig.savefig(img_bytes, format="png", dpi=300)
            img_bytes.seek(0)
            zip_file.writestr(f"{filename_no_ext}_plot.png", img_bytes.read())

    zip_buffer.seek(0)
    st.download_button(
        label="📥 ZIP-Datei herunterladen",
        data=zip_buffer,
        file_name="Batch_Analyse_Ergebnisse.zip",
        mime="application/zip"
    )
