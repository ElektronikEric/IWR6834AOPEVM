# IWR6843AOPEVM mmWave Radar – 3D People Tracking Visualizer

Ein Python-basiertes Live-Visualisierungssystem für die Texas Instruments IWR6843AOP mmWave Radar-Plattform zur Personenerkennung und Verfolgung in Innenräumen.

## Überblick

Dieses Projekt verbindet einen IWR6843AOP mmWave Radar mit Python, um:

- **Echtzeit-Personenerkennung**: Verfolgung von Personen im Raum mittels 3D-Tracking
- **Live-3D-Visualisierung**: Darstellung der erkannten Personen und Objekte in einer interaktiven 3D-Raumansicht
- **TLV-Datenverarbeitung**: Vollständige Dekodierung des TI mmWave-Ausgabedatenformats (TLV)
- **Presence-Detection**: Erkennung von Anwesenheit im konfigurierten Raumareal

**Anwendungsbeispiele:**
- Raumauslastungserkennung
- Personenzählung
- Bewegungsverfolgung in Innenräumen
- Sicherheitsanwendungen

---

## Hardware-Anforderungen

- **IWR6843AOP EVM** – Texas Instruments mmWave Radar
- **2× USB-zu-UART-Adapter** (oder FTDI-ähnliche Schnittstelle)
  - COM31: Datenstrom vom Radar (115200 baud, 8N1)
  - COM33: Konfiguration des Radars (921600 baud, 8N1)
- **PC/Laptop** mit Python 3.8+
- **USB-Stromversorgung** für das EVM

---

## Software-Anforderungen

```bash
python 3.8 oder höher
matplotlib >= 3.5.0
numpy >= 1.20.0
pyserial >= 3.5
