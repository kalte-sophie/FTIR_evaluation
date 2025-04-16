import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Funktion zur Peak-Identifikation
def identify_peaks(df, num_peaks, window_size, prominence):
    df["Smoothed"] = df["Transmission"].rolling(window=window_size, center=True).mean()
    inverted = -df["Smoothed"]
    peaks, properties = find_peaks(inverted, distance=20, prominence=prominence)

    num_found = min(len(peaks), num_peaks)
    strongest_indices = sorted(
        range(len(peaks)),
        key=lambda i: properties["prominences"][i],
        reverse=True
    )[:num_found]
    strongest_peaks = peaks[strongest_indices]

    peak_positions = df["Wave number"].iloc[strongest_peaks]
    peak_values = df["Transmission"].iloc[strongest_peaks]

    return peak_positions.tolist(), peak_values.tolist(), strongest_peaks  # Jetzt als Listen zurückgeben



# Funktion für Strandard Plot
import matplotlib.pyplot as plt

def create_standard_plot(df, peak_indices, peak_positions, peak_values, legend_name, x_min, x_max, y_min, y_max):
    # Sicherheitscheck: konvertiere ggf. zu Listen
    peak_positions = list(peak_positions) if not isinstance(peak_positions, list) else peak_positions
    peak_values = list(peak_values) if not isinstance(peak_values, list) else peak_values

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Wave number"], df["Transmission"], label=legend_name, color="black", alpha=0.7)

    # Peaks markieren
    ax.scatter(
        df["Wave number"].iloc[peak_indices],
        df["Transmission"].iloc[peak_indices],
        color="red",
        s=50,
        zorder=3,
        label="Identifizierte Peaks"
    )

    for pos, val in zip(peak_positions, peak_values):
        ax.plot([pos, pos], [0, val], color='red', linestyle='--', alpha=0.5, linewidth=0.5)

    ax.set_xlabel("Wellenzahl (cm⁻¹)")
    ax.set_ylabel("Transmission (%)")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.legend(loc="lower left")

    return fig


