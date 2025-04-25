import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import weibull_min
import math

# ------------------------------------------------------------------------------
# 1. Definition der SPEZIFISCHEN Leistungskurven (Sommer & Winter)
#    (Unverändert)
# ------------------------------------------------------------------------------
# Leistungskurve für Sommermonate
leistungskurve_sommer_daten = {
    'Windgeschwindigkeit (m/s)': [
        3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10,
        10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16,
        16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22,
        22.5, 23, 23.5, 24, 24.5, 25, 25.5, 26
    ],
    'Leistung (kW)': [
        28, 127, 260, 427, 628, 865, 1145, 1473, 1855, 2294, 2795, 3356,
        3950, 4545, 5126, 5656, 6066, 6364, 6572, 6707, 6780, 6799, 6800,
        6800, 6800, 6800, 6800, 6800, 6800, 6800, 6800, 6800, 6800, 6800,
        6800, 6603, 6331, 6059, 5794, 5528, 5270, 5012, 4760, 4508, 4264,
        4019, 3774
    ]
}
leistungskurve_sommer_df = pd.DataFrame(leistungskurve_sommer_daten)

# Leistungskurve für Wintermonate
leistungskurve_winter_daten = {
    'Windgeschwindigkeit (m/s)': [
        3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10,
        10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16,
        16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22,
        22.5, 23, 23.5, 24, 24.5, 25, 25.5, 26
    ],
    'Leistung (kW)': [
        37, 143, 288, 469, 687, 944, 1248, 1604, 2018, 2494, 3036, 3627,
        4230, 4820, 5382, 5864, 6218, 6472, 6644, 6749, 6795, 6800, 6800,
        6800, 6800, 6800, 6800, 6800, 6800, 6800, 6800, 6800, 6800, 6800,
        6800, 6603, 6331, 6059, 5794, 5528, 5270, 5012, 4760, 4508, 4264,
        4019, 3774
    ]
}
leistungskurve_winter_df = pd.DataFrame(leistungskurve_winter_daten)

# Funktion zur Leistungsinterpolation (Unverändert)
def get_leistung(windgeschwindigkeit, leistungskurve_df):
    min_ws = leistungskurve_df['Windgeschwindigkeit (m/s)'].min()
    leistung = np.interp(windgeschwindigkeit,
                         leistungskurve_df['Windgeschwindigkeit (m/s)'],
                         leistungskurve_df['Leistung (kW)'],
                         left=0.0,
                         right=leistungskurve_df['Leistung (kW)'].iloc[-1])
    leistung[windgeschwindigkeit < min_ws] = 0.0
    return leistung

# ------------------------------------------------------------------------------
# 2. Monatliche Winddaten & Saisonale Einteilung
#    (Die monatlichen Durchschnittsgeschwindigkeiten werden für die
#     Lambda-Berechnung nicht mehr direkt verwendet, bleiben aber hier definiert)
# ------------------------------------------------------------------------------
monatliche_durchschnittsgeschwindigkeiten = {
    'Jan': 8.5, 'Feb': 8.0, 'Mär': 7.8, 'Apr': 7.2, 'Mai': 6.5, 'Jun': 5.8,
    'Jul': 5.5, 'Aug': 5.7, 'Sep': 6.3, 'Okt': 7.0, 'Nov': 7.8, 'Dez': 8.2
}
sommer_monate = ['Mai', 'Jun', 'Jul', 'Aug', 'Sep']
nabenhoehe = 164
k_standort = 2 # Formparameter k bleibt bei 2
stunden_pro_monat = {'Jan': 31*24, 'Feb': 28*24, 'Mär': 31*24, 'Apr': 30*24, 'Mai': 31*24, 'Jun': 30*24,
                   'Jul': 31*24, 'Aug': 31*24, 'Sep': 30*24, 'Okt': 31*24, 'Nov': 30*24, 'Dez': 31*24}
monatsnamen = list(monatliche_durchschnittsgeschwindigkeiten.keys())

# ------------------------------------------------------------------------------
# 3. Windpark- und Anlagenparameter (Unverändert)
# ------------------------------------------------------------------------------
anzahl_windanlagen = 1
verfuegbarkeitsfaktor = 0.97

# ------------------------------------------------------------------------------
# 4. Funktion zur Berechnung des monatlichen Energieertrags mit Weibull-Verteilung
#    --> JETZT MIT FESTEM LAMBDA <--
# ------------------------------------------------------------------------------
def monatlicher_energieertrag_weibull(avg_windgeschwindigkeit, k, leistungskurve_df_aktuell, anzahl_anlagen, stunden_im_monat, anzahl_bins=100, verfuegbarkeitsfaktor=0.97):
    
    # FESTES LAMBDA verwenden
    lambda_param = 6.77
    
    # Die ursprüngliche Berechnung basierend auf avg_windgeschwindigkeit wird nicht mehr verwendet:
    # if avg_windgeschwindigkeit <= 0: return 0.0
    # lambda_param = avg_windgeschwindigkeit / math.gamma(1 + 1/k)

    max_ws_kurve = leistungskurve_df_aktuell['Windgeschwindigkeit (m/s)'].max()
    max_ws_integration = max(30, max_ws_kurve + 5)
    windgeschwindigkeiten = np.linspace(0, max_ws_integration, anzahl_bins)
    bin_breite = windgeschwindigkeiten[1] - windgeschwindigkeiten[0]
    v_mittelpunkte = windgeschwindigkeiten[:-1] + bin_breite / 2

    
    wahrscheinlichkeiten_pdf = weibull_min.pdf(v_mittelpunkte, k, scale=lambda_param)

    wahrscheinlichkeiten_bin = wahrscheinlichkeiten_pdf * bin_breite
    leistungen_kw = get_leistung(v_mittelpunkte, leistungskurve_df_aktuell)
    energie_kwh_pro_bin = leistungen_kw * wahrscheinlichkeiten_bin * stunden_im_monat
    gesamtertrag_kwh_monat_eine_anlage = np.sum(energie_kwh_pro_bin)
    gesamtertrag_kwh_monat_park = gesamtertrag_kwh_monat_eine_anlage * anzahl_anlagen * verfuegbarkeitsfaktor
    return gesamtertrag_kwh_monat_park

# ------------------------------------------------------------------------------
# 5. Berechnung des jährlichen und monatlichen Energieertrags
#   
# ------------------------------------------------------------------------------

# --- SCHRITT 5.1: Berechne den jährlichen Gesamtertrag  ---
jährlicher_ertrag_kwh_simuliert = 0
print("Berechne simulierten jährlichen Gesamtertrag (mit festem Lambda = 6.77)...")
for monat, avg_wind in monatliche_durchschnittsgeschwindigkeiten.items(): # Loop über Monate bleibt für Auswahl der Kurve und Stundenanzahl
    if monat in sommer_monate:
        aktuelle_leistungskurve_df = leistungskurve_sommer_df
    else:
        aktuelle_leistungskurve_df = leistungskurve_winter_df

    # Berechne den simulierten Ertrag für diesen Monat
    # avg_wind wird an die Funktion übergeben, aber intern nicht mehr für Lambda verwendet
    monatlicher_ertrag_kwh_sim = monatlicher_energieertrag_weibull(
        avg_wind, # Dieser Wert wird ignoriert für Lambda-Berechnung
        k_standort,
        aktuelle_leistungskurve_df,
        anzahl_windanlagen,
        stunden_pro_monat[monat],
        verfuegbarkeitsfaktor=verfuegbarkeitsfaktor
    )
    jährlicher_ertrag_kwh_simuliert += monatlicher_ertrag_kwh_sim

# Umrechnung des simulierten Jahresertrags in MWh
jährlicher_ertrag_mwh_simuliert = jährlicher_ertrag_kwh_simuliert / 1e3

print(f"\nSimulierter jährlicher Gesamtenergieertrag: {jährlicher_ertrag_mwh_simuliert:.2f} MWh")

# --- SCHRITT 5.2: Definiere die gewünschte prozentuale Verteilung  ---
monatliche_prozentuale_verteilung = {
    'Jan': 13.46 / 100, 'Feb': 12.23 / 100, 'Mär': 8.59 / 100,
    'Apr': 8.37 / 100, 'Mai': 5.60 / 100, 'Jun': 5.24 / 100,
    'Jul': 5.24 / 100, 'Aug': 4.80 / 100, 'Sep': 7.86 / 100,
    'Okt': 7.71 / 100, 'Nov': 9.10 / 100, 'Dez': 11.79 / 100
}
summe_prozente = sum(monatliche_prozentuale_verteilung.values()) * 100
print(f"Summe der definierten Prozentsätze: {summe_prozente:.2f}%")
if not math.isclose(summe_prozente, 100.0, abs_tol=0.1):
    print("WARNUNG: Die Summe der Prozentsätze weicht signifikant von 100% ab!")

# --- SCHRITT 5.3: Berechne die monatlichen Erträge basierend auf den Prozenten ) ---
monatliche_erträge_gwh_prognose = {}
print("\nBerechne monatliche Erträge basierend auf prozentualer Verteilung:")
for monat, prozent in monatliche_prozentuale_verteilung.items():
    monatlicher_ertrag_kwh_prognose = jährlicher_ertrag_kwh_simuliert * prozent
    monatliche_erträge_gwh_prognose[monat] = monatlicher_ertrag_kwh_prognose / 1e3

# --- SCHRITT 5.4: Gib die prognostizierten monatlichen Erträge aus  ---
print("\nPrognostizierter monatlicher Energieertrag (GWh) basierend auf Verteilung:")
for monat in monatsnamen:
    ertrag = monatliche_erträge_gwh_prognose.get(monat, 0.0)
    print(f"{monat}: {ertrag:.4f} MWh")

# ------------------------------------------------------------------------------
# 6. Erstellung eines beispielhaften Tageslastprofils 
# ------------------------------------------------------------------------------
mittlere_windgeschwindigkeit_jahr = np.mean(list(monatliche_durchschnittsgeschwindigkeiten.values()))
stunden_am_tag = np.arange(24)
windgeschwindigkeit_tagesprofil = mittlere_windgeschwindigkeit_jahr + 2 * np.sin(2 * np.pi * stunden_am_tag / 24)
windgeschwindigkeit_tagesprofil = np.maximum(0, windgeschwindigkeit_tagesprofil)
windparkleistung_tagesprofil_mw = get_leistung(windgeschwindigkeit_tagesprofil, leistungskurve_winter_df) * anzahl_windanlagen / 1000

plt.figure(figsize=(10, 5))
plt.plot(stunden_am_tag, windparkleistung_tagesprofil_mw, label='Beispiel-Windparkleistung (Winterkurve)')
plt.xlabel('Stunde des Tages')
plt.ylabel('Leistung (MW)')
plt.title(f'Beispielhaftes Tageslastprofil (basierend auf Jahresmittelwind {mittlere_windgeschwindigkeit_jahr:.2f} m/s)')
plt.grid(True)
plt.legend()
plt.xticks(np.arange(0, 24, 2))
plt.tight_layout()
plt.show()

# ------------------------------------------------------------------------------
# 7. Visualisierung des monatlichen Ertrags 
# ------------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
plot_werte = [monatliche_erträge_gwh_prognose.get(m, 0.0) for m in monatsnamen]
plt.bar(monatsnamen, plot_werte, color=['lightblue']*12)
plt.xlabel('Monat')
plt.ylabel('Energieertrag (GWh)')
plt.title('Prognostizierter monatlicher Energieertrag (basierend auf fester %-Verteilung)')
plt.grid(axis='y')
plt.tight_layout()
plt.show()

# ------------------------------------------------------------------------------
# 8. Visualisierung der Leistungskurven 
# ------------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.plot(leistungskurve_sommer_df['Windgeschwindigkeit (m/s)'],
         leistungskurve_sommer_df['Leistung (kW)'],
         marker='o', linestyle='-', color='orange', label='Leistungskurve Sommer')
plt.plot(leistungskurve_winter_df['Windgeschwindigkeit (m/s)'],
         leistungskurve_winter_df['Leistung (kW)'],
         marker='x', linestyle='--', color='blue', label='Leistungskurve Winter')
plt.xlabel('Windgeschwindigkeit (m/s)')
plt.ylabel('Leistung (kW)')
plt.title('Leistungskurven der Windkraftanlage (Sommer vs. Winter)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ------------------------------------------------------------------------------
# 9. Visualisierung der Weibull-Verteilung
#    
# ------------------------------------------------------------------------------

lambda_fest = 6.77

windgeschwindigkeiten_weibull = np.linspace(0, 30, 200)
# Berechne PDF mit festem Lambda
weibull_pdf = weibull_min.pdf(windgeschwindigkeiten_weibull, k_standort, scale=lambda_fest)

plt.figure(figsize=(8, 5))

plt.plot(windgeschwindigkeiten_weibull, weibull_pdf, label=f'Weibull (k={k_standort}, λ={lambda_fest})')
plt.xlabel('Windgeschwindigkeit (m/s)')
plt.ylabel('Wahrscheinlichkeitsdichte')
plt.title('Weibull-Verteilung der Windgeschwindigkeit (mit festem Lambda)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print("\nCode-Ausführung abgeschlossen.")
