import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import weibull_min
import math

# ------------------------------------------------------------------------------
# 1. Definition der SPEZIFISCHEN Leistungskurve
# ------------------------------------------------------------------------------
leistungskurve_daten_spezifisch = {
    'Windgeschwindigkeit (m/s)': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0],
    'Leistung (kW)': [0.0, 0.0, 29.1, 268.8, 647.2, 1180.5, 1889.3, 2626.5, 3259.1, 3807.5, 4314.3, 4761.2, 5056.3, 5212.4, 5267.2, 5270.0, 5270.0, 5270.0, 5270.0, 5270.0, 5270.0, 5270.0, 5270.0, 4760.0, 4264.0, 3774.0]
}
leistungskurve_df = pd.DataFrame(leistungskurve_daten_spezifisch)

def get_leistung(windgeschwindigkeit, leistungskurve):
    """
    Gibt die interpolierte Leistung (in kW) für eine gegebene Windgeschwindigkeit zurück.
    """
    return np.interp(windgeschwindigkeit, leistungskurve['Windgeschwindigkeit (m/s)'], leistungskurve['Leistung (kW)'])

# ------------------------------------------------------------------------------
# 2. Monatliche Winddaten (SIMULATION VON SAISONALEN SCHWANKUNGEN)
#    Hier definieren wir realistische(re) monatliche durchschnittliche Windgeschwindigkeiten.
#    Diese Werte sind beispielhaft und sollten durch genauere Daten ersetzt werden.
# ------------------------------------------------------------------------------
monatliche_durchschnittsgeschwindigkeiten = {
    'Jan': 8.5,
    'Feb': 8.0,
    'Mär': 7.8,
    'Apr': 7.2,
    'Mai': 6.5,
    'Jun': 5.8,  # Reduzierter Sommerwert
    'Jul': 5.5,  # Stark reduzierter Sommerwert
    'Aug': 5.7,  # Stark reduzierter Sommerwert
    'Sep': 6.3,  # Erholung im Spätsommer
    'Okt': 7.0,
    'Nov': 7.8,
    'Dez': 8.2
}

nabenhoehe = 164  # m

# Annahme eines typischen Formparameters k für Binnenlandstandorte (gleich über das Jahr)
k_standort = 2

# Anzahl der Stunden pro Monat
stunden_pro_monat = {'Jan': 31*24, 'Feb': 28*24, 'Mär': 31*24, 'Apr': 30*24, 'Mai': 31*24, 'Jun': 30*24,
                     'Jul': 31*24, 'Aug': 31*24, 'Sep': 30*24, 'Okt': 31*24, 'Nov': 30*24, 'Dez': 31*24}
monatsnamen = list(monatliche_durchschnittsgeschwindigkeiten.keys())

# ------------------------------------------------------------------------------
# 3. Windpark- und Anlagenparameter
# ------------------------------------------------------------------------------
anzahl_windanlagen = 1
verfuegbarkeitsfaktor = 0.97

# ------------------------------------------------------------------------------
# 4. Funktion zur Berechnung des monatlichen Energieertrags mit Weibull-Verteilung
#    Nutzt nun die monatlichen Durchschnittsgeschwindigkeiten zur Berechnung von lambda.
# ------------------------------------------------------------------------------
def monatlicher_energieertrag_weibull(avg_windgeschwindigkeit, k, leistungskurve, anzahl_anlagen, stunden_im_monat, anzahl_bins=100, verfuegbarkeitsfaktor=0.97):
    """
    Schätzt den monatlichen Energieertrag unter Berücksichtigung der Weibull-Verteilung
    basierend auf der monatlichen durchschnittlichen Windgeschwindigkeit.
    """
    lambda_param = avg_windgeschwindigkeit / math.gamma(1 + 1/k)
    windgeschwindigkeiten = np.linspace(0, leistungskurve['Windgeschwindigkeit (m/s)'].max(), anzahl_bins)
    wahrscheinlichkeiten = weibull_min.pdf(windgeschwindigkeiten, k, scale=lambda_param)

    gesamtertrag_kwh_monat = 0
    for i in range(len(windgeschwindigkeiten) - 1):
        v_mittel = (windgeschwindigkeiten[i] + windgeschwindigkeiten[i+1]) / 2
        dauer_in_sekunden = (wahrscheinlichkeiten[i] + wahrscheinlichkeiten[i+1]) / 2 * (windgeschwindigkeiten[i+1] - windgeschwindigkeiten[i]) * stunden_im_monat * 3600
        leistung_kw = get_leistung(v_mittel, leistungskurve)
        energie_kwh = leistung_kw * (dauer_in_sekunden / 3600)
        gesamtertrag_kwh_monat += energie_kwh

    return gesamtertrag_kwh_monat * anzahl_anlagen * verfuegbarkeitsfaktor

# ------------------------------------------------------------------------------
# 5. Berechnung des jährlichen und monatlichen Energieertrags
# ------------------------------------------------------------------------------
jährlicher_ertrag_kwh = 0
monatliche_erträge_gwh = {}

for monat, avg_wind in monatliche_durchschnittsgeschwindigkeiten.items():
    monatlicher_ertrag_kwh = monatlicher_energieertrag_weibull(
        avg_wind, k_standort, leistungskurve_df, anzahl_windanlagen, stunden_pro_monat[monat]
    )
    jährlicher_ertrag_kwh += monatlicher_ertrag_kwh
    monatliche_erträge_gwh[monat] = monatlicher_ertrag_kwh / 1e6

jährlicher_ertrag_gwh = jährlicher_ertrag_kwh / 1e3

print(f"Geschätzter jährlicher Energieertrag: {jährlicher_ertrag_gwh:.2f} MWh")
print("\nGeschätzter monatlicher Energieertrag:")
for monat, ertrag in monatliche_erträge_gwh.items():
    print(f"{monat}: {ertrag:.3f} GWh")

# ------------------------------------------------------------------------------
# 6. Erstellung eines beispielhaften Tageslastprofils (basierend auf dem Jahresdurchschnitt)
#    Da wir keine monatlichen oder täglichen Winddaten haben, bleibt dies eine Vereinfachung.
#    Wir verwenden den Jahresdurchschnitt der simulierten Monatsdaten.
# ------------------------------------------------------------------------------
mittlere_windgeschwindigkeit_jahr = np.mean(list(monatliche_durchschnittsgeschwindigkeiten.values()))
stunden_am_tag = np.arange(24)
windgeschwindigkeit_tagesprofil = mittlere_windgeschwindigkeit_jahr + 2 * np.sin(2 * np.pi * stunden_am_tag / 24)
windparkleistung_tagesprofil_mw = np.array([get_leistung(v, leistungskurve_df) for v in windgeschwindigkeit_tagesprofil]) * anzahl_windanlagen / 1000

plt.figure(figsize=(10, 5))
plt.plot(stunden_am_tag, windparkleistung_tagesprofil_mw, label='Windparkleistung (generiert)')
plt.xlabel('Stunde des Tages')
plt.ylabel('Leistung (MW)')
plt.title('Beispielhaftes Tageslastprofil des Windparks (basierend auf Jahresdurchschnitt)')
plt.grid(True)
plt.legend()
plt.xticks(np.arange(0, 24, 2))
plt.tight_layout()
plt.show()

# ------------------------------------------------------------------------------
# 7. Visualisierung des monatlichen Ertrags
# ------------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.bar(monatsnamen, monatliche_erträge_gwh.values())
plt.xlabel('Monat')
plt.ylabel('Energieertrag (GWh)')
plt.title('Geschätzter monatlicher Energieertrag des Windparks (mit simulierten Schwankungen)')
plt.grid(axis='y')
plt.tight_layout()
plt.show()

# ------------------------------------------------------------------------------
# 8. Visualisierung der Leistungskurve
# ------------------------------------------------------------------------------
windgeschwindigkeiten_plot = np.linspace(0, leistungskurve_df['Windgeschwindigkeit (m/s)'].max(), 100)
leistung_plot = [get_leistung(v, leistungskurve_df) for v in windgeschwindigkeiten_plot]

plt.figure(figsize=(8, 5))
plt.plot(leistungskurve_df['Windgeschwindigkeit (m/s)'], leistungskurve_df['Leistung (kW)'], marker='o', linestyle='-', label='Leistungskurve')
plt.plot(windgeschwindigkeiten_plot, leistung_plot, linestyle='--', label='Interpolierte Leistung')
plt.xlabel('Windgeschwindigkeit (m/s)')
plt.ylabel('Leistung (kW)')
plt.title('Leistungskurve der Windkraftanlage')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ------------------------------------------------------------------------------
# 9. Visualisierung der Weibull-Verteilung
# ------------------------------------------------------------------------------
windgeschwindigkeiten_weibull = np.linspace(0, 25, 100)  # Windgeschwindigkeiten für den Plot
weibull_pdf = weibull_min.pdf(windgeschwindigkeiten_weibull, k_standort, scale=6.77) # Verwenden den Jahresdurchschnitt

plt.figure(figsize=(8, 5))
plt.plot(windgeschwindigkeiten_weibull, weibull_pdf, label=f'Weibull (k={k_standort}, λ={6.77})')
plt.xlabel('Windgeschwindigkeit (m/s)')
plt.ylabel('Wahrscheinlichkeitsdichte')
plt.title('Weibull-Verteilung der Windgeschwindigkeit')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()