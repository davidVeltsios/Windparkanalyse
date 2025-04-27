# Optimierungsmodell für ein Energiesystem (PV + Wind + Batterie)

## Übersicht

Dieses Python-Skript modelliert und optimiert ein netzgekoppeltes Energiesystem, bestehend aus Photovoltaik (PV), Windkraftanlagen und einem Batteriespeicher. Ziel ist es, die kostenoptimalen Kapazitäten dieser Komponenten zu bestimmen und deren Betrieb zu simulieren, um einen gegebenen Strombedarf zu decken. Die Optimierung minimiert dabei die annualisierten Gesamtkosten des Systems über die definierte Projektlaufzeit.

## Funktionalität

* **Kapazitätsoptimierung:** Berechnet die optimalen Nennleistungen für PV (MWp) und Wind (MW) sowie die optimale Energie- (MWh) und Leistungskapazität (MW) der Batterie.
* **Betriebssimulation:** Simuliert die Energieflüsse (Erzeugung, Bedarf, Netzbezug/-einspeisung, Batterieladung/-entladung, Abregelung) in einer hohen zeitlichen Auflösung (z.B. 15 Minuten) über ein ganzes Jahr.
* **Wirtschaftlichkeitsanalyse:**
    * Berechnet die annualisierten Gesamtkosten des Systems.
    * Ermittelt Stromgestehungskosten (LCOE) für das Gesamtsystem sowie spezifisch für PV und Wind.
    * Ermittelt Speicherkosten (LCOS - Levelized Cost of Storage) für die Batterie.
    * Berechnet den internen Zinsfuß (IRR) und den kumulierten Cashflow über die Projektlaufzeit.
    * Bestimmt Kennzahlen wie Autarkiegrad und Erneuerbare Deckungsrate.
* **Ausgabe:** Generiert detaillierte Ergebnisse auf der Konsole, mehrere Diagramme (z.B. Jahresprofile, Cashflow, SoC) und exportiert die detaillierten Zeitreihen in eine Excel-Datei.

## Funktionsweise des Codes (Struktur)

Der Code ist modular aufgebaut:

1.  **Imports & Setup:** Laden der Bibliotheken und grundlegende Einstellungen.
2.  **Eingabedaten & Annahmen:** Definition aller technischen und ökonomischen Parameter (Kosten, Lebensdauern, Wirkungsgrade, Strompreise, Zinssatz, Lastprofil-Basis, Ertragsdaten etc.). *Hier können Anpassungen für eigene Szenarien vorgenommen werden.*
3.  **Zeitreihengenerierung:** Umwandlung der (ggf. monatlichen) Ertragsdaten in hochaufgelöste Jahresprofile für PV und Wind (pro MW installierter Leistung). Berücksichtigung von Nachtabschaltung (PV) und Skalierung auf Ziel-Jahreserträge. Erstellung des Einspeisevergütungsprofils.
4.  **Annuitätenfaktor:** Berechnung des Faktors zur Umwandlung von Investitionskosten in jährliche Kosten unter Berücksichtigung von Lebensdauer und Zinssatz.
5.  **Optimierungsmodell-Definition (PuLP):**
    * Definition des Minimierungsziels (Gesamtkosten).
    * Definition der Entscheidungsvariablen (Kapazitäten, Betriebsdaten pro Zeitschritt).
    * Formulierung der Zielfunktion (Summe der annualisierten Kosten und Erlöse).
    * Formulierung der Nebenbedingungen (Energiebilanz, Batteriephysik, technische Limits).
6.  **Optimierung lösen:** Übergabe des Modells an einen externen LP-Solver (Standard: CBC) zur Berechnung der optimalen Lösung.
7.  **Ergebnisauswertung:** Extrahieren der optimalen Variablenwerte, Berechnung von Jahresbilanzen, Kostenkomponenten und Kennzahlen (LCOE, LCOS, IRR, Autarkie etc.).
8.  **Ausgabe (Plots & Excel):** Visualisierung der Ergebnisse und Export der Zeitreihendaten.

## Optimierungslogik

Das Herzstück des Skripts ist ein **Lineares Optimierungsmodell (LP)**, das mit der Bibliothek `PuLP` formuliert wird.

* **Ziel:** Minimierung der **annualisierten Gesamtkosten** des Systems über die Projektlaufzeit.
* **Entscheidungsvariablen:**
    * Kapazitäten: $Cap_{PV}$ (MWp), $Cap_{Wind}$ (MW), $Cap_{Batt}^{MWh}$ (MWh), $Cap_{Batt}^{MW}$ (MW)
    * Betrieb (pro Zeitschritt $t$): Netzbezug $P^{GridBuy}_t$, Netzeinspeisung $P^{GridSell}_t$, Abregelung $P^{Curtail}_t$, Batterieladung $P^{BattCh}_t$, Batterieentladung $P^{BattDis}_t$, Batterieladezustand $SoC_t$.
* **Zielfunktion (vereinfacht):**
    $$ \min \sum_{tech} (\text{Ann. CAPEX}_{tech} + \text{Ann. OPEX}_{tech}) + \sum_{t} (\text{Netzbezugskosten}_t - \text{Einspeiseerlöse}_t) $$
    wobei die annualisierten Kosten über den Annuitätsfaktor aus Investition, Lebensdauer und Zinssatz berechnet werden.
* **Wichtige Nebenbedingungen (Constraints):**
    * **Energiebilanz (für jeden Zeitschritt $t$):** Stellt sicher, dass die Summe aller Energiequellen (PV, Wind, Netzbezug, Batterieentladung) der Summe aller Energiesenken (Bedarf, Netzeinspeisung, Abregelung, Batterieladung) entspricht.
        $$ P^{Gen}_{PV,t} + P^{Gen}_{Wind,t} + P^{GridBuy}_t + P^{BattDis}_t = D_t + P^{GridSell}_t + P^{Curtail}_t + P^{BattCh}_t $$
    * **Batteriephysik:** Modelliert die Änderung des Ladezustands ($SoC$) unter Berücksichtigung von Ladung/Entladung und Wirkungsgrad ($\eta_{Batt}$), die Einhaltung von minimalem/maximalem SoC sowie der maximalen Lade-/Entladeleistung ($Cap_{Batt}^{MW}$).
        $$ SoC_{t+1} = SoC_t + P^{BattCh}_t \cdot \sqrt{\eta_{Batt}} - P^{BattDis}_t / \sqrt{\eta_{Batt}} $$
        $$ SoC_{min} \cdot Cap_{Batt}^{MWh} \le SoC_t \le Cap_{Batt}^{MWh} $$
        $$ P^{BattCh/Dis}_t \le Cap_{Batt}^{MW} \cdot \Delta t $$
    * **Zyklischer Betrieb:** Der Ladezustand am Ende des Jahres muss dem am Anfang entsprechen ($SoC_{N} = SoC_0$).
    * **Nicht-Negativität:** Alle Energieflüsse und Kapazitäten müssen $\ge 0$ sein.

Der verwendete Solver (z.B. CBC) findet die Werte für alle Entscheidungsvariablen, die diese Bedingungen erfüllen und dabei die Zielfunktion minimieren. Dabei wird implizit die optimale Betriebsstrategie (inkl. der Batterieladezyklen) ermittelt.

## Eingabeparameter

Die zentralen Eingabeparameter werden direkt am Anfang des Skripts in Abschnitt 1 definiert. Dazu gehören u.a.:

* Zeitliche Auflösung (`time_resolution_hours`)
* Lastprofil (`demand_per_hour_kwh`)
* Monatliche relative Erträge für PV und Wind
* Spezifische Jahreserträge für PV und Wind
* Investitions- und Betriebskosten (CAPEX, OPEX) für PV, Wind, Batterie
* Lebensdauern der Komponenten
* Diskontierungsrate (`discount_rate`)
* Batterie-Wirkungsgrad und Min/Max SoC
* Netzstrompreise (Bezug, Einspeisung)

## Ausgaben

Das Skript generiert nach erfolgreicher Optimierung:

1.  **Konsolenausgaben:** Detaillierte Ergebnisse zu optimalen Kapazitäten, Kostenaufschlüsselung, Jahresenergiebilanz, LCOE/LCOS, IRR, Autarkiegrad etc.
2.  **Diagramme (als `.png`-Dateien):**
    * `lastprofil_erzeugung_jahr_mit_batterie.png`: Jahresverlauf von Last, PV- und Winderzeugung.
    * `kumulierter_cashflow.png`: Kumulierter Cashflow über die Projektlaufzeit.
    * `batterie_soc_jahr.png`: Jahresverlauf des Batterieladezustands (SoC) in Prozent.
    * (Optional) `kostenlandschaft_optimierung_mit_batterie.png`: 2D-Kostenkontur für PV vs. Wind bei optimaler Batterie (sehr rechenintensiv).
3.  **Excel-Datei:**
    * `energiebilanz_15min_mit_batterie.xlsx`: Enthält die detaillierten Zeitreihen (15-Minuten-Werte) für alle relevanten Energieflüsse (Bedarf, Erzeugung, Netz, Batterie-Ladung/Entladung/SoC) für das gesamte Jahr.

## Anforderungen & Installation

* Python 3.x
* Benötigte Bibliotheken:
    * `pulp`: Für die lineare Optimierung
    * `numpy`: Für numerische Berechnungen
    * `pandas`: Für Zeitreihen und Excel-Export
    * `matplotlib`: Für Diagramme
    * `openpyxl`: Für das Schreiben von `.xlsx`-Dateien (Excel-Export)
    * `numpy-financial`: Für die IRR-Berechnung

    Installation über pip:
    ```bash
    pip install pulp numpy pandas matplotlib openpyxl numpy-financial
    ```
    PuLP benötigt zusätzlich einen installierten LP-Solver. CBC ist quelloffen und wird oft mit PuLP verwendet oder kann leicht nachinstalliert werden (Details siehe PuLP-Dokumentation).

## Benutzung

1.  **Parameter anpassen:** Öffne das Skript und passe bei Bedarf die Eingabeparameter in Abschnitt 1 an dein spezifisches Szenario an.
2.  **Ausführen:** Führe das Skript über die Kommandozeile aus:
    ```bash
    python dein_skriptname.py
    ```
3.  **Ergebnisse prüfen:** Analysiere die Konsolenausgaben, die generierten `.png`-Diagramme und die `energiebilanz_15min_mit_batterie.xlsx`-Datei im selben Verzeichnis wie das Skript.

## Limitationen & Annahmen

* **Erzeugungsprofile:** Basieren auf Monatsmitteln und einfacher Tag/Nacht-Logik; bilden keine realen Wetterextreme oder Dunkelflauten ab.
* **Lastprofil:** Aktuell als konstant angenommen; kann durch variable Profile ersetzt werden.
* **Perfekte Voraussicht:** Das Modell kennt die Erzeugung und Last für das gesamte Jahr im Voraus (typisch für LP-Planungsmodelle).
* **Vereinfachte Kosten:** Keine explizite Modellierung von Degradation, detaillierten Wartungsplänen oder Preisänderungen über die Zeit (außer Diskontierung).
* **Netz:** Keine Berücksichtigung von Netzengpässen oder Anschlussleistungsgrenzen.
* **Konstanter Wirkungsgrad:** Der Batteriewirkungsgrad wird als konstant angenommen.

## Zukünftige Erweiterungen (Ideen)

* Einlesen variabler Lastprofile aus Dateien.
* Verwendung hochaufgelöster, historischer Erzeugungszeitreihen.
* Implementierung von Degradationsmodellen für PV und Batterie.
* Berücksichtigung von Netzentgelten und Leistungspreisen.
* Modellierung von Unsicherheiten (z.B. stochastische Optimierung).
* Einbindung weiterer Technologien (z.B. Elektrolyseur, Wärmepumpe).
