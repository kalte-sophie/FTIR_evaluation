import os
import pandas as pd
import streamlit as st
from io import BytesIO
from utils import create_standard_plot  # Nutzung der zentralen Plot-Funktion

st.header("📊 Plot mit mehreren Datensätzen")

# 📥 Mehrere Dateien hochladen
uploaded_files = st.file_uploader("Wähle mehrere CSV-Dateien", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    st.markdown("### 🏷️ Legenden-Namen & Anzeige-Auswahl")

    file_data = []

    for i, file in enumerate(uploaded_files):
        filename_no_ext = os.path.splitext(file.name)[0]
        df = pd.read_csv(file, skiprows=2, sep=",", names=["Wave number", "Transmission"], header=None)

        col1, col2 = st.columns([3, 1])
        with col1:
            legend_name = st.text_input(f"Legendenname für Datei {i+1}", value=filename_no_ext, key=f"legend_{i}")
        with col2:
            show = st.checkbox("Anzeigen", value=True, key=f"show_{i}")

        file_data.append({
            "df": df,
            "legend": legend_name,
            "show": show
        })

    st.markdown("### ⚙️ Achsenanpassung")
    x_min = st.number_input("X-Achse Maximum", value=4000, step=10)
    x_max = st.number_input("X-Achse Minimum", value=520, step=10)
    y_min = st.number_input("Y-Achse Minimum", value=30, step=1)
    y_max = st.number_input("Y-Achse Maximum", value=100, step=1)

    # 📈 Plot erstellen
    st.markdown("### 📈 Spektren-Plot")

    # Wir erstellen manuell einen kombinierten Plot, da create_standard_plot für Einzelplot gemacht ist
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))

    plotted = False
    for data in file_data:
        if data["show"]:
            ax.plot(data["df"]["Wave number"], data["df"]["Transmission"],
                    label=data["legend"], alpha=0.7)
            plotted = True

    if plotted:
        ax.set_xlabel("Wellenzahl (cm⁻¹)")
        ax.set_ylabel("Transmission (%)")
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.legend(loc="lower left")
        st.pyplot(fig)

        # 📥 Download-Button für den Plot
        plot_buffer = BytesIO()
        fig.savefig(plot_buffer, format="png", dpi=300)
        plot_buffer.seek(0)
        st.download_button("📥 Download Plot (PNG)", data=plot_buffer,
                           file_name="mehrere_spektren_plot.png", mime="image/png")
    else:
        st.info("Bitte mindestens einen Datensatz zur Anzeige auswählen.")
else:
    st.info("Lade eine oder mehrere CSV-Dateien hoch.")
