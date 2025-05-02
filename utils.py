import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import least_squares


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



# Funktion für Standard Plot mit Show Peaks Checkbox
def create_standard_plot(df, peak_indices, peak_positions, peak_values, legend_name, x_min, x_max, y_min, y_max, show_peaks):
    # Sicherheitscheck: konvertiere ggf. zu Listen
    peak_positions = list(peak_positions) if not isinstance(peak_positions, list) else peak_positions
    peak_values = list(peak_values) if not isinstance(peak_values, list) else peak_values

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Wave number"], df["Transmission"], label=legend_name, color="black", alpha=0.7)

    # Peaks nur anzeigen, wenn die Checkbox aktiviert ist
    if show_peaks:
        # Peaks markieren
        ax.scatter(
            df["Wave number"].iloc[peak_indices],
            df["Transmission"].iloc[peak_indices],
            color="red",
            s=7,
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



# Basislinien Korrektur Polynomial

def polynomial_baseline_correction(wavenumber, spectrum, poly_order=5):
  
    # Polynom-Koeffizienten berechnen
    coeffs = np.polyfit(wavenumber, spectrum, poly_order)
    
    # Basislinie berechnen
    baseline = np.polyval(coeffs, wavenumber)
    
    # Korrigiertes Spektrum berechnen
    # Für Transmissionsspektren: Division durch die Basislinie
    corrected_spectrum = spectrum / baseline * 100  # Normalisierung auf 100%
    
    # Für Absorptionsspektren würde man stattdessen subtrahieren:
    # corrected_spectrum = spectrum - baseline
    
    return corrected_spectrum, baseline



# Basislinien Korrektur Off-set

def automatic_offset_correction(wavenumber, spectrum, window_size=100, threshold=0.99):
    """
    Führt eine automatische Offset-Korrektur durch, indem absorptionsfreie Bereiche
    identifiziert werden und auf 100% Transmission gesetzt werden.
    """
    # Arrays in NumPy-Arrays umwandeln, falls sie es noch nicht sind
    wavenumber = np.array(wavenumber)
    spectrum = np.array(spectrum)
    
    # Lokale Maxima finden (potentielle absorptionsfreie Bereiche)
    peaks, _ = find_peaks(spectrum, height=np.max(spectrum)*threshold, distance=window_size)
    
    if len(peaks) < 2:
        # Wenn nicht genug Punkte gefunden wurden, nutze die Enden des Spektrums
        # und einige Punkte mit den höchsten Werten
        top_indices = np.argsort(spectrum)[-5:]  # Die 5 höchsten Punkte
        peaks = np.unique(np.append(peaks, [0, len(wavenumber)-1, *top_indices]))
    
    # Interpolieren zwischen den gefundenen Punkten
    baseline_points = np.zeros_like(spectrum)
    baseline_points[peaks] = spectrum[peaks]
    
    # Maske für die gefundenen Punkte
    mask = baseline_points > 0
    
    # Lineare Interpolation zwischen den Punkten
    from scipy.interpolate import interp1d
    f = interp1d(wavenumber[mask], baseline_points[mask], kind='linear', fill_value='extrapolate')
    baseline = f(wavenumber)
    
    # Korrigiertes Spektrum berechnen
    corrected_spectrum = spectrum / baseline * 100  # Normalisierung auf 100%
    
    return corrected_spectrum, baseline