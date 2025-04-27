# Windenergieertrags-Rechner (Weibull mit festem Lambda & saisonalen Leistungskurven)

## Übersicht

Dieses Python-Skript dient zur Berechnung des erwarteten jährlichen und monatlichen Energieertrags einer Windkraftanlage (oder eines Windparks mit einer Anlage). Es verwendet spezifische, saisonal unterschiedliche Leistungskurven (Sommer/Winter) und modelliert die Wahrscheinlichkeitsverteilung der Windgeschwindigkeiten mithilfe einer Weibull-Verteilung.

Eine Besonderheit dieses Skripts ist die Verwendung eines **festen Skalenparameters (Lambda)** für die Weibull-Verteilung über das ganze Jahr, anstatt diesen aus den (ebenfalls im Code definierten) monatlichen Durchschnittswindgeschwindigkeiten abzuleiten. Der berechnete jährliche Gesamtenergieertrag wird anschließend anhand einer vordefinierten prozentualen Aufteilung auf die einzelnen Monate verteilt.

## Methodik

Das Skript folgt diesen Schritten:

1.  **Leistungskurven-Definition:** Zwei detaillierte Leistungskurven (Leistung in kW vs. Windgeschwindigkeit in m/s) werden definiert – eine für den Betrieb in den Sommermonaten, eine für den Winter. Eine Interpolationsfunktion (`get_leistung`) wird bereitgestellt, um die Leistung für beliebige Windgeschwindigkeiten zu ermitteln.
2.  **Weibull-Verteilung:** Die Verteilung der Windgeschwindigkeiten wird mit der `scipy.stats.weibull_min`-Funktion modelliert. Es wird ein fester Formparameter (`k_standort = 2`) und ein **fester Skalenparameter (`lambda_param = 6.77`)** verwendet. *Wichtiger Hinweis: Der Lambda-Parameter ist im Code hartcodiert und wird NICHT aus den monatlichen Durchschnittsgeschwindigkeiten berechnet.*
3.  **Monatliche Ertragsberechnung (Simulation):** Für jeden Monat wird der Energieertrag einer einzelnen Anlage berechnet. Dies geschieht durch Integration über die Weibull-Verteilung: Für kleine Windgeschwindigkeitsintervalle ("bins") wird die Wahrscheinlichkeit dieses Intervalls (aus der Weibull-PDF mit festem Lambda) mit der Leistung der Anlage bei dieser Geschwindigkeit (aus der saisonal passenden Leistungskurve) und der Anzahl der Stunden im Monat multipliziert.
4.  **Jährlicher Gesamtertrag (Simulation):** Die simulierten monatlichen Erträge werden aufsummiert und um den Verfügbarkeitsfaktor (`verfuegbarkeitsfaktor`) sowie die Anzahl der Anlagen (`anzahl_windanlagen`) korrigiert. Dies ergibt den `jährlicher_ertrag_mwh_simuliert`.
5.  **Finale monatliche Ertragsprognose:** Der in Schritt 4 berechnete *jährliche* Gesamtertrag wird nun anhand einer fest definierten prozentualen Verteilung (`monatliche_prozentuale_verteilung`) auf die einzelnen Monate aufgeteilt. Dies ergibt die endgültigen prognostizierten Monatserträge (`monatliche_erträge_gwh_prognose`). *Hinweis: Die Form der monatlichen Verteilung wird hier also durch die Prozentsätze bestimmt, nicht direkt durch die monatliche Simulation mit festem Lambda.*
6.  **Visualisierung:** Das Skript generiert mehrere Plots zur Veranschaulichung der Eingangsdaten und Ergebnisse.

## Wichtige Parameter

* **Leistungskurven:** `leistungskurve_sommer_df`, `leistungskurve_winter_df`
* **Weibull-Parameter:** `k_standort` (Form), `lambda_param` (Skala, **fest codiert!**)
* **Anlagenparameter:** `anzahl_windanlagen`, `verfuegbarkeitsfaktor`
* **Monatliche Verteilung:** `monatliche_prozentuale_verteilung` (wird zur Aufteilung des Jahresertrags verwendet)

## Ausgaben

1.  **Konsolenausgaben:**
    * Simulierter jährlicher Gesamtenergieertrag (MWh).
    * Prognostizierte monatliche Energieerträge (MWh), basierend auf der prozentualen Verteilung.
2.  **Diagramme:**
    * Ein beispielhaftes Tageslastprofil (rein illustrativ).
    * Balkendiagramm der prognostizierten monatlichen Energieerträge.
    * Liniendiagramm der Sommer- und Winter-Leistungskurven.
    * Liniendiagramm der verwendeten Weibull-Wahrscheinlichkeitsdichtefunktion (PDF).

## Code-Struktur

1.  Definition der Leistungskurven und Interpolationsfunktion.
2.  Definition monatlicher Basisdaten und saisonaler Einteilung.
3.  Definition von Windpark-/Anlagenparametern.
4.  Funktion zur Berechnung des monatlichen Ertrags mit *festem Lambda*.
5.  Berechnung des *simulierten Jahresertrags* und anschließende Verteilung auf *prognostizierte Monatserträge* mittels Prozentwerten.
6.  Erstellung eines Beispiel-Tagesprofils.
7.  Visualisierung des prognostizierten Monatsertrags.
8.  Visualisierung der Leistungskurven.
9.  Visualisierung der Weibull-Verteilung.

## Anforderungen

* Python 3.x
* Benötigte Bibliotheken: `pandas`, `numpy`, `matplotlib`, `scipy`

    Installation über pip:
    ```bash
    pip install pandas numpy matplotlib scipy
    ```

## Benutzung

1.  **Parameter prüfen/anpassen:** Überprüfe insbesondere die Leistungskurven, die festen Weibull-Parameter (`k_standort`, `lambda_param`) und die `monatliche_prozentuale_verteilung` im Code.
2.  **Ausführen:** Führe das Skript über die Kommandozeile aus:
    ```bash
    python dein_skriptname.py
    ```
3.  **Ergebnisse prüfen:** Analysiere die Konsolenausgaben und die angezeigten Plots.

## Limitationen & Hinweise

* **Fester Lambda-Wert:** Der Skalenparameter Lambda der Weibull-Verteilung ist fest auf 6.77 gesetzt und spiegelt nicht die saisonalen Unterschiede wider, die durch die `monatliche_durchschnittsgeschwindigkeiten` angedeutet werden.
* **Zweistufige Monatsverteilung:** Die endgültige monatliche Verteilung des Ertrags basiert auf der festen prozentualen Vorgabe, nicht auf den Ergebnissen der monatlichen Weibull-Simulation (diese dient nur zur Bestimmung des *Gesamt*-Jahresertrags).
* **Tagesprofil:** Das generierte Tagesprofil ist rein illustrativ und basiert auf vereinfachten Annahmen.
