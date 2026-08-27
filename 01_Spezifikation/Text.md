TECHNISCHE SPEZIFIKATION – IWR6843AOP MMWAVE RADAR 3D PEOPLE TRACKING VISUALIZER

Dokumentversion: 1.0
Datum: August 2026
Status: Aktiv

_______________________________________________________________________________

1. PROJEKTÜBERSICHT

1.1 Zielsetzung

Entwicklung eines Python-basierten Echtzeit-Visualisierungssystems zur Verfolgung und Zählung von Personen in Innenräumen mittels eines Texas Instruments IWR6843AOP mmWave Radars.

1.2 Hauptziele

• Echtzeit-Personenverfolgung mit Live-3D-Visualisierung
• Zuverlässige Datenübertragung über UART
• Vollständige TLV-Datenverarbeitung (mmWave SDK Format)
• Präzise Koordinatentransformation (sphärisch → kartesisch)
• Interactive 3D-Raumdarstellung
• Benutzerfreundliche Bedienung (Konsole + GUI)

1.3 Anwendungsfälle

• Raumbelegungserkennung (Büros, Meeting Rooms)
• Personenzählung (Einzelhandel, Museen)
• Bewegungsverfolgung (Sicherheit, Analyse)
• Präsenzdetection (Energie-Management)

_______________________________________________________________________________

2. SYSTEMARCHITEKTUR

2.1 Modulübersicht

Der folgende Tabelle zeigt die Verteilung der Aufgaben auf die verschiedenen Module:

| Modul | Verantwortung | Eingabe | Ausgabe |
|-------|---------------|---------|---------|
| uart.py | UART-Kommunikation | Sensor (UART) | Rohe Bytes (bytearray) |
| parser.py | Frame-Dekodierung | Rohe Bytes | Frame-Dict mit allen TLVs |
| cli.py | Radar-Konfiguration | CFG-Datei | UART-Befehle |
| visualizer.py | 3D-Darstellung | Frame-Dict | matplotlib 3D-Plot |
| main.py | Orchestrierung | Config + Sensor | Live-Visualisierung |

Das uart.py-Modul verwaltet die serielle Kommunikation mit dem Sensor und liefert die Rohdaten. Der parser.py dekodiert diese Daten nach dem TLV-Format des mmWave SDK. Das cli.py-Modul sendet Konfigurationsbefehle an das Radar. Der visualizer.py visualisiert die verarbeiteten Daten in 3D, und main.py orchestriert den gesamten Prozess.

_______________________________________________________________________________

3. HARDWARE-SPEZIFIKATION

3.1 Sensor

Die folgende Tabelle beschreibt die Haupteigenschaften des verwendeten Radar-Sensors:

| Eigenschaft | Wert |
|-------------|------|
| Gerät | Texas Instruments IWR6843AOP EVM |
| Sensor-Typ | 60 GHz Single-Chip Automotive Radar |
| Kanäle | 4 TX (Transmit) × 4 RX (Receive) |
| Reichweite | bis 6 m (konfigurierbar) |
| Update-Rate | 5–50 Hz (konfigurierbar) |
| Genauigkeit (Range) | ±5 cm |
| Genauigkeit (Azimuth) | ±2° |

Das Radar nutzt eine 60 GHz Frequenz und bietet 16 Kanäle (4 Transmitter × 4 Receiver) für hochaufgelöste 3D-Erfassung. Die maximale Reichweite von 6 Metern ist für Indoor-Personenerkennung ausreichend, und die Genauigkeit von ±5 cm ermöglicht präzise Positionsbestimmung.

3.2 Schnittstellen

Das System nutzt zwei separate UART-Schnittstellen:

UART Data Stream – für die Erfassung von Messdaten:

| Parameter | Wert |
|-----------|------|
| COM-Port | COM31 (konfigurierbar) |
| Baudrate | 115200 bps |
| Format | 8N1 |
| Datenbits | 8 |
| Parity | Keine |
| Stoppbit | 1 |
| Richtung | Sensor → PC (Eingabe) |
| Datenformat | mmWave SDK TLV Frames |

Diese Schnittstelle empfängt kontinuierlich die Messdaten vom Radar mit einer Baudrate von 115200 bps. Die Daten werden im TLV-Format (Type-Length-Value) übertragen.

UART Configuration – für die Konfiguration des Sensors:

| Parameter | Wert |
|-----------|------|
| COM-Port | COM33 (konfigurierbar) |
| Baudrate | 921600 bps |
| Format | 8N1 |
| Datenbits | 8 |
| Parity | Keine |
| Stoppbit | 1 |
| Richtung | PC → Sensor (Ausgabe) |
| Datenformat | *.cfg-Datei (ASCII-Text) |

Die Konfigurationsschnittstelle nutzt eine höhere Baudrate von 921600 bps und sendet ASCII-Text-Befehle aus einer CFG-Datei zum Sensor.

3.3 Stromversorgung

| Parameter | Wert |
|-----------|------|
| Spannung | 5V USB |
| Stromaufnahme | max. 1,5 A |
| Versorgung | Standard USB-Kabel |

Die Stromversorgung erfolgt direkt über USB mit 5V und einer maximalen Stromaufnahme von 1,5 A. Achten Sie darauf, dass der USB-Anschluss des Computers diese Stromaufnahme unterstützt.

_______________________________________________________________________________

4. DATENFORMAT-SPEZIFIKATION

4.1 Frame-Struktur

Jeder Frame vom Radar folgt einer standardisierten Struktur. Der Frame beginnt mit einem festdefinierten Magic Word und enthält einen Header von 40 Bytes gefolgt von variablen TLV-Payloads:

Byte  0-7:    Magic Word (0x02 0x01 0x04 0x03 0x06 0x05 0x08 0x07)
Byte  8-11:   Version (uint32, little-endian)
Byte  12-15:  Packet Length (uint32, little-endian) in Bytes
Byte  16-19:  Platform (uint32)
Byte  20-23:  Frame Number (uint32)
Byte  24-27:  CPU Cycles (uint32)
Byte  28-31:  Number of Detected Objects (uint32)
Byte  32-35:  Number of TLVs (uint32)
Byte  36-39:  Subframe Number (uint32)
Byte  40+:    TLV Payloads (variable Länge)

Die Gesamtgröße des Headers ist konstant 40 Bytes. Das Magic Word dient zur Identifikation und Re-Synchronisation bei Übertragungsfehlern. Die Packet Length gibt die Gesamtgröße des kompletten Frames an, und die Number of Detected Objects und Number of TLVs werden zur Validierung benötigt.

4.2 TLV-Struktur

Jedes TLV (Type-Length-Value) Element folgt einer einheitlichen Struktur:

| Offset | Feld | Typ | Bytes |
|--------|------|-----|-------|
| 0 | Type | uint32 | 4 |
| 4 | Length | uint32 | 4 |
| 8 | Payload | variant | L |

Die Gesamtgröße eines TLV ist Gesamtgröße TLV = 8 + Length Bytes.

**Wichtig:** Das Feld `Length` enthält nur die Größe der Payload, nicht die Größe des 8-Byte-Headers. Dies ist ein häufiger Fehler bei der Implementierung von Parsern.

4.3 Unterstützte TLV-Typen

Das System unterstützt fünf verschiedene TLV-Typen, die jeweils unterschiedliche Informationen enthalten:

TLV 1020 – Compressed Points (Punkt-Wolke)

Dieses TLV enthält die rohen Erkennungspunkte, also alle vom Radar erfassten Objekte.

Zweck:      Detektierte Objekt-Punkte
Länge:      20 + (NumPoints × 8) Bytes

Die Payload beginnt mit fünf Unit-Werten (je 4 Bytes float32):

| Bytes | Feld | Typ |
|-------|------|-----|
| 0-3 | Elevation Unit | float32 |
| 4-7 | Azimuth Unit | float32 |
| 8-11 | Doppler Unit | float32 |
| 12-15 | Range Unit | float32 |
| 16-19 | SNR Unit | float32 |

Danach folgen die Punkte (je 8 Byte):

| Byte | Feld | Typ |
|------|------|-----|
| 0 | Elevation | int8 |
| 1 | Azimuth | int8 |
| 2-3 | Doppler | int16 (little-endian) |
| 4-5 | Range | uint16 (little-endian) |
| 6-7 | SNR | uint16 (little-endian) |

Die Transformation von sphärischen zu kartesischen Koordinaten erfolgt wie folgt:

x = range × cos(elevation) × sin(azimuth)
y = range × cos(elevation) × cos(azimuth)
z = range × sin(elevation)
v = doppler × doppler_unit

_______________________________________________________________________________

TLV 1010 – 3D Target List (Verfolgte Personen)

Dieses TLV enthält die Ergebnisse des Tracking-Algorithms, also die verfolgten Personen mit ihren Positionen und Geschwindigkeiten.

Zweck:      Tracker-Ergebnisse
Länge:      112 × NumTracks Bytes

Jeder Track hat eine Größe von 112 Bytes und ist wie folgt strukturiert:

| Offset | Feld | Typ | Bytes |
|--------|------|-----|-------|
| 0 | Track ID | uint32 | 4 |
| 4 | Position X | float | 4 |
| 8 | Position Y | float | 4 |
| 12 | Position Z | float | 4 |
| 16 | Velocity X | float | 4 |
| 20 | Velocity Y | float | 4 |
| 24 | Velocity Z | float | 4 |
| 28 | Acceleration X | float | 4 |
| 32 | Acceleration Y | float | 4 |
| 36 | Acceleration Z | float | 4 |
| 40 | Error Covariance [16] | float | 64 |
| 104 | Gating Gain | float | 4 |
| 108 | Confidence Level | float | 4 |

Alle Koordinaten sind bereits im World Space (mit Ursprung auf dem Boden). Die Confidence Level gibt die Zuverlässigkeit des Tracks an (Wertebereich 0.0–1.0).

_______________________________________________________________________________

TLV 1011 – Target Index (Punkt-zu-Track-Zuordnung)

Dieses TLV ordnet jeden Punkt aus TLV 1020 einem Track aus TLV 1010 zu.

Zweck:      Verknüpfung: Welcher Punkt → Welcher Track?
Länge:      NumPoints Bytes (1 Byte pro Punkt aus TLV 1020)

Jedes Byte repräsentiert einen Punkt:

Byte i: Target ID des Punktes i

Mögliche Werte:
  0-253:  Track-ID (gültige Zuordnung)
  254:    Point liegt außerhalb der Gating-Area
  255:    Point nicht zugeordnet (Rauschen/Clutter)

Ein Wert von 255 bedeutet, dass der Punkt als Rauschen oder Clutter klassifiziert wurde und nicht zu einer Person gehört.

_______________________________________________________________________________

TLV 1012 – Target Height (Körpergröße)

Dieses TLV enthält die geschätzte Körpergröße jeder verfolgten Person.

Zweck:      Geschätzte Höhe pro Track
Länge:      12 × NumTracks Bytes

Jeder Track hat einen Eintrag von 12 Bytes:

| Offset | Feld | Typ | Bytes |
|--------|------|-----|-------|
| 0 | Target ID | uint32 | 4 |
| 4 | Max Z (Kopf) | float | 4 |
| 8 | Min Z (Füße) | float | 4 |

Die tatsächliche Körpergröße wird berechnet als: Höhe = MaxZ - MinZ

Diese Information ist nützlich zur Validierung von Tracks und zur Unterscheidung zwischen Personen und anderen Objekten.

_______________________________________________________________________________

TLV 1021 – Presence Indication

Dieses TLV gibt an, ob sich jemand im konfigurierten Raumbereich befindet.

Zweck:      Ist jemand im konfigurierten Raumbereich?
Länge:      4 Bytes

Die Payload besteht aus einem einzigen uint32-Wert:

Bytes 0-3: uint32
  0 = Keine Anwesenheit erkannt
  1 = Anwesenheit erkannt

Dies ist ein einfaches Ja/Nein-Flag basierend auf der presenceBoundaryBox-Konfiguration.

_______________________________________________________________________________

4.4 Frame-Validierung

Der Parser prüft jeden Frame auf Konsistenz:

1. Magic Word: Muss exakt 02 01 04 03 06 05 08 07 sein
2. Packet Length: ≥ 40 (Header-Mindestgröße)
3. TLV Boundaries: Jedes TLV muss vollständig im Frame liegen
4. TLV Type: Nur bekannte Typen (1020, 1010, 1011, 1012, 1021)
5. Object Count: Muss mit Punkt-Anzahl in TLV 1020 übereinstimmen
6. Payload Sizes: TLV 1020 = 20 + (Obj × 8), TLV 1010 = Tracks × 112, etc.

Falls eine Validierungsprüfung fehlschlägt, wird der Frame verworfen und der Parser versucht, das nächste Magic Word zu finden.

_______________________________________________________________________________

5. KOORDINATENSYSTEM-SPEZIFIKATION

5.1 World Coordinates (Raum)

Das System nutzt ein einheitliches Koordinatensystem mit Ursprung auf dem Fußboden:

Grenzen für 8×5×3m Raum:
  X: -4m bis +4m (Breite, von links nach rechts)
  Y: 0m bis +5m (Tiefe, von vorne nach hinten)
  Z: 0m bis +3m (Höhe, von Boden bis Decke)

Der Ursprung (0, 0, 0) liegt auf dem Fußboden an der Stelle, wo der Radar direkt über ihm montiert ist. Das X-Achse erstreckt sich nach links (negativ) und rechts (positiv). Die Y-Achse zeigt nach hinten (positiv). Die Z-Achse zeigt nach oben (positiv).

5.2 Sensor-Position

Das Radar wird konfiguriert mit: sensorPosition 1 0 0

Diese Parameter bedeuten:
  Höhe:               1m über Fußboden
  Azimuth-Tilt:       0° (keine seitliche Neigung)
  Elevation-Tilt:     0° (horizontal ausgerichtet)

Der Sensor-Ursprung im World Space liegt daher bei den Koordinaten (0, 0, 1). Bei dieser Konfiguration zeigt das Radar horizontal in den Raum.

5.3 Koordinatentransformation

Point Cloud (TLV 1020):

Die Punkte aus TLV 1020 werden relativ zum Sensor-Ursprung erfasst. Bei horizontaler Montage (Elevation-Tilt = 0) ist die Transformation zu World Coordinates einfach:

world_x = radar_x + point_x
world_y = radar_y + point_y
world_z = radar_z + point_z

Beispiel: Wenn RADAR_Z = 1.0 und ein Punkt hat point_z = 0.5 (relativ zum Sensor), dann ist world_z = 1.0 + 0.5 = 1.5m über dem Fußboden.

Tracks (TLV 1010):

Die Track-Positionen aus TLV 1010 sind bereits in World Coordinates. Der Tracker des Radars berücksichtigt die Sensor-Position automatisch. Daher ist keine zusätzliche Transformation erforderlich.

_______________________________________________________________________________

6. KONFIGURATIONS-SPEZIFIKATION

6.1 CFG-Datei-Format

Die Konfiguration erfolgt über eine ASCII-Text-Datei:

Datei:        AOP_6m_default.cfg
Format:       ASCII Text, eine Befehl pro Zeile
Kommentare:   Eine Zeile die mit % beginnt ist ein Kommentar

Die CFG-Datei enthält Befehle, die beim Start des Radars ausgeführt werden. Jeder Befehl ist auf einer separaten Zeile.

6.2 Kritische Parameter

Die folgenden Parameter müssen für Ihre Raumkonfiguration angepasst werden:

Raum-Grenzen

  boundaryBox -4 4 0 5 0 3

Dies definiert den Tracking-Bereich in World Coordinates. Der Parameter bedeutet:
  X: von -4m bis +4m (8m Breite)
  Y: von 0m bis +5m (5m Tiefe)
  Z: von 0m bis +3m (3m Höhe)

Sensor-Position

  sensorPosition 1 0 0

Dies definiert die Höhe und Ausrichtung des Sensors:
  1. Parameter: Höhe in Metern (1m)
  2. Parameter: Azimuth-Tilt in Grad (0° = keine Drehung)
  3. Parameter: Elevation-Tilt in Grad (0° = horizontal)

Presence-Detection-Zone

  presenceBoundaryBox -3 3 0.5 4.5 0 3

Dies definiert den Bereich, in dem die Presence-Detection aktiv ist. Dies ist üblicherweise ein etwas kleinerer Bereich als die gesamte boundaryBox, um Reflexionen an den Wänden auszuschließen.

Frame-Rate

  frameCfg 0 2 96 0 200.00 1 0

Das Parameter 200.00 ist die Frame-Periode in Millisekunden. 200ms bedeutet eine Frame-Rate von 5 Hz (1000ms / 200ms = 5 Frames pro Sekunde). Der typische Bereich liegt zwischen 50ms und 500ms.

Tracker-Parameter

  trackingCfg 1 2 800 30 46 96 55

Diese Parameter kontrollieren das Kalman-Filter-Verhalten des Trackers. Detaillierte Erklärungen finden Sie im TI People Tracking Tuning Guide.

_______________________________________________________________________________

7. SOFTWARE-ANFORDERUNGEN

7.1 Python-Version

Das Projekt erfordert Python in folgenden Versionen:

| Anforderung | Version |
|-------------|---------|
| Minimum | Python 3.8 |
| Empfohlen | Python 3.9 oder neuer |
| Getestet | Python 3.10 |

7.2 Abhängigkeiten

Das Projekt benötigt drei externe Python-Pakete:

| Paket | Version | Zweck |
|-------|---------|-------|
| matplotlib | ≥ 3.5.0 | 3D-Visualisierung und Live-Plotting |
| numpy | ≥ 1.20.0 | Numerische Berechnungen und Array-Operationen |
| pyserial | ≥ 3.5 | Serielle UART-Kommunikation |

Diese können mit pip installiert werden: pip install matplotlib numpy pyserial

7.3 Betriebssystem-Anforderungen

Das System läuft auf verschiedenen Betriebssystemen mit unterschiedlichen Anforderungen:

| OS | Version | Anmerkungen |
|----|---------|-------------|
| Windows | 10, 11 | FTDI/CH340 Treiber für USB-UART-Adapter erforderlich |
| Linux | Ubuntu 20.04+ | udev-Regeln für USB-Zugriff ohne sudo erforderlich |
| macOS | 10.14+ | Keine zusätzlichen Treiber notwendig |

Unter Linux müssen Sie wahrscheinlich die folgenden Treiber installieren:
  sudo apt-get install python3-serial

_______________________________________________________________________________

8. PERFORMANCE-ANFORDERUNGEN

8.1 Durchsatz

Das System muss folgende Performance-Ziele erfüllen:

| Metrik | Sollwert | Grenzwert |
|--------|----------|-----------|
| Frame-Rate (Parser) | 10–20 fps | min. 5 fps |
| Frame-Rate (Visualizer) | 5–10 fps | min. 2 fps |
| Latenz (Sensor → Display) | < 1 Sekunde | < 5 Sekunden |
| CPU-Auslastung (Parser) | < 20% | < 40% |
| Speicher (RAM) | < 200 MB | < 500 MB |

Bei einer Radar-Framerate von 5 Hz (200ms zwischen Frames) und einem optimierten Parser sollte die Latenz unter 1 Sekunde liegen. Falls die Latenz 10 Sekunden überschreitet, deutet dies auf einen Engpass hin (zu viele Debug-Ausgaben, zu häufiges Redraw der Visualisierung, etc.).

8.2 Buffer-Management

Das System verwaltet verschiedene Buffer-Arten:

| Komponente | Spezifikation |
|------------|---------------|
| UART-Puffer | Betriebssystem-verwaltet (typisch 4–64 KB) |
| Frame-Parser-Buffer | Dynamisch (max. 2× Packet Size) |
| Punkt-Cloud | ~150 Punkte max. = ~1.2 KB pro Frame |
| Visualisierung | ~50 Plot-Objekte = ~2 MB RAM |

Der Frame-Parser-Buffer wächst dynamisch mit eingehenden Daten, wird aber begrenzt, um Speicherprobleme zu verhindern. Die Punkt-Cloud braucht wenig Speicher, da die Visualisierung nur die Coordinate speichert (3 float × 150 Punkte = ~1.8 KB).

_______________________________________________________________________________

9. FEHLERBEHANDLUNG UND ROBUSTHEIT

9.1 Error-Kategorien

Das System behandelt verschiedene Fehlertypen:

| Fehlertyp | Beschreibung | Behandlung |
|-----------|-------------|-----------|
| Magic Word Error | Frame korrupt | Frame verwerfen, Buffer re-sync |
| TLV Boundary Error | TLV überschreitet Paketgröße | Frame verwerfen |
| Serial Timeout | Keine Daten auf UART | Warnung ausgeben, weiterwarten |
| Configuration Error | CFG-Datei falsch | Programm beenden, Fehler anzeigen |
| Parser Crash | Unerwartete Daten | Try-Catch, Fehler in Log schreiben |

Bei einem Magic Word Error wird der Parser den Buffer scannen, um das nächste gültige Magic Word zu finden. Dies kann bis zu einen Frame Datenverlust verursachen, aber das System bleibt synchronisiert.

9.2 Magic Word Re-Synchronisation

Wenn der Parser die Synchronisation mit dem Datenstrom verliert (z.B. wegen beschädigter Daten):

1. Der Buffer wird Byte für Byte durchsucht nach dem Magic Word
2. Alle Bytes vor dem Magic Word werden verworfen
3. Die letzten 7 Bytes bleiben im Buffer (für grenzüberschreitende Erkennung)

Maximaler Datenverlust: Ein einzelner fehlerhafter Frame (typisch 1–3 KB)

Das System kann sich automatisch von Übertragungsfehlern erholen, benötigt aber möglicherweise 1–2 Sekunden zum Resynchronisieren.

_______________________________________________________________________________

10. VISUALISIERUNGS-SPEZIFIKATION

10.1 Punkt-Färbung

Die erkannten Objekte werden farbcodiert nach ihrer SNR (Signal-to-Noise Ratio):

  Farbraum:     "Plasma" Colormap (matplotlib, von dunkel zu hell)
  Achse:        SNR (Signal-to-Noise Ratio) in dB
  Min:          Dunkles Lila (niedriges SNR, schlecht erkannte Punkte)
  Max:          Helles Gelb (hohes SNR, gut erkannte Punkte)

Dies ermöglicht es, auf einen Blick zu sehen, welche Punkte zuverlässig erkannt wurden. Punkte mit niedrigem SNR sind weniger zuverlässig.

10.2 Interaktivität

Der 3D-Plot ist interaktiv und unterstützt verschiedene Mausoperationen:

| Aktion | Funktion |
|--------|----------|
| Linke Maustaste + Ziehen | 3D rotieren (Kamera-Winkel ändern) |
| Mausrad | Zoom (herein und heraus) |
| Rechte Maustaste + Ziehen | Pan (Ansicht verschieben) |
| Home Button (in der Toolbar) | Zurücksetzen auf Standard-Ansicht |

10.3 Update-Frequenz

Die Aktualisierungsraten sind auf verschiedenen Ebenen unterschiedlich:

  Parser:       Verarbeitet alle verfügbaren Frames
                Bei 200ms Periode = 5 fps vom Radar
                Tatsächlich 18–20 fps in unseren Tests möglich

  Plot:         Begrenzt auf 10 fps durch _draw_interval = 0.1
                Reduziert die Rendering-Last

  Titel:        Aktualisiert mit jedem Plot-Update
                Zeigt aktuelle Frame-Nummer, Personenzahl, etc.

Diese Entkopplung verhindert, dass schnelle Parser zu häufigen Re-Renderings führen.

_______________________________________________________________________________

11. SICHERHEIT UND ZUVERLÄSSIGKEIT

11.1 Eingabe-Validierung

Das System validiert alle Eingaben:

  • UART-Daten: Nur Bytes akzeptieren, keine Text-Interpretation
  • CFG-Befehle: ASCII-Text mit Max. 255 Zeichen pro Zeile
  • Frame-Header: Alle Werte gegen Grenzen prüfen
  • TLV-Längen: Sicherstellen, dass TLVs nicht über Frame-Grenzen gehen

11.2 Exception-Handling

Das Hauptprogramm nutzt umfassendes Exception-Handling:

  try:
    frame = parser.get_frame()
    if frame:
      visualizer.update(frame)
  except KeyboardInterrupt:
    # Benutzer drückt Ctrl+C
    visualizer.close()
    uart.close()
  except Exception as e:
    # Unerwartete Fehler
    logger.error(f"Unexpected error: {e}")
    visualizer.close()

Dies stellt sicher, dass das Programm ordnungsgemäß beendet wird und Ressourcen freigegeben werden.

11.3 Ressourcen-Limits

Das System hat harte Grenzen zum Schutz vor Ressourcenerschöpfung:

  Max. Framesize:       64 KB (UART-Puffer)
  Max. Objekte:         200 Punkte pro Frame
  Max. Tracks:          20 verfolgte Personen
  Max. Speicher:        500 MB RAM

Falls diese Grenzen überschritten werden, gibt das System eine Warnung aus und verwirft Daten.

_______________________________________________________________________________

12. TESTANFORDERUNGEN

12.1 Modul-Tests

Jedes Modul hat spezifische Testanforderungen:

| Test | Beschreibung | Grenzwerte |
|------|-------------|-----------|
| Magic Word Detection | Findet korrekte Frames im Datenstrom | 100% Erkennungsrate |
| TLV Parsing | Dekodiert alle TLV-Typen korrekt | Keine Abweichungen |
| Coord Transform | Konvertiert sphärisch zu kartesisch | ±1 cm Genauigkeit |
| UART Sync | Erholt sich von Frame-Fehlern | < 1 Frame Datenverlust |

Diese Tests sollten mit verschiedenen CFG-Dateien durchgeführt werden, um sicherzustellen, dass der Parser robust ist.

12.2 Integrations-Tests

End-to-End Tests des gesamten Systems:

  • End-to-End: Sensor → Parser → Visualizer
  • Realtime-Performance unter Last (viele Punkte)
  • Memory Leak-Prüfung (30 Min. kontinuierlicher Betrieb)

12.3 User-Acceptance-Tests

Tests mit echten Benutzern und echten Räumen:

  • Korrekte Personenzählung (vs. manuelles Zählen)
  • Raum-Rendering (vs. physische Dimensionen)
  • Personen-Verfolgung über Zeit (Konsistenz)

_______________________________________________________________________________

13. WARTUNG UND SUPPORT

13.1 Logging

Alle wichtigen Ereignisse werden geloggt:

Struktur:
  [TIMESTAMP] [LEVEL] [MODULE] Message

Beispiel:
  2026-08-27 14:23:45.123 INFO parser Frame 1116: 150 objects, 3 tracks
  2026-08-27 14:23:45.234 WARN visualizer Persons confidence filter: 0.5

13.2 Known Limitations

Das System hat folgende bekannte Einschränkungen:

1. Reichweite: Max. 6m (Sensor-Limitation)
2. Metallische Objekte: Können Signale stark beeinflussen oder blockieren
3. Zu schnelle Bewegungen: >2 m/s können zu Tracking-Verlust führen
4. Rauschignoranz: 255-markierte Punkte deuten auf Rausch- oder Clutter-Probleme
5. Framerate: < 20 fps bei sehr hohem Objekt-Aufkommen (>150 Punkte)

Diese Limitationen sind teilweise sensor-spezifisch und können nicht durch Software überwunden werden.

13.3 Changelog

v1.0 (August 2026)

  • Initial Release
  • Unterstützt TLV 1020 (Punkt-Wolke), 1010 (Targets), 1011 (Indizes), 1012 (Höhen), 1021 (Presence)
  • 3D-Visualisierung mit matplotlib und interaktiven Kontrollen
  • Live-Personenzählung mit Confidence-Filter
  • UART-Datenstrom und Konfiguration auf separaten Ports
  • Robuste Fehlerbehandlung und Re-Synchronisation

_______________________________________________________________________________

14. GLOSSAR

| Begriff | Erklärung |
|---------|-----------|
| TLV | Type-Length-Value. Datenformat des mmWave SDK für strukturierte Daten |
| UART | Universal Asynchronous Receiver-Transmitter. Serielle Kommunikationsschnittstelle |
| Track | Verfolgte Entität (typisch eine Person) mit Kalman-Filter Position und Velocity |
| SNR | Signal-to-Noise Ratio. Verhältnis der Signalstärke zum Rauschpegel in dB |
| World Space | Koordinatensystem mit Ursprung auf dem Boden in Sensor-Projektion |
| Sensor Space | Koordinatensystem mit Ursprung am Radar-Sensor selbst |
| Doppler | Radialgeschwindigkeit des Objekts (Bewegung zum oder vom Sensor) |
| Confidence | Tracking-Zuverlässigkeit des Filters (Wertebereich 0.0–1.0) |
| Presence | Erkennung von Anwesenheit mindestens einer Person im Raumareal |
| Gating | Bereich um einen Track, in dem Punkte diesem Track zugeordnet werden |
| Clutter | Rauschen oder falsche Erkennungen, typischerweise an Wänden oder Hindernissen |

_______________________________________________________________________________

15. REFERENZEN UND NORMEN

Weitere Informationen finden Sie in den offiziellen Dokumenten:

• TI IWR6843AOP Datenblatt
  https://www.ti.com/product/IWR6843AOP
  Technische Spezifikation des Sensors

• mmWave SDK User Guide v4.0
  https://www.ti.com/tool/MMWAVE_SDK
  Kompletter Leitfaden für das Software-Entwicklungskit

• 3D People Tracking Detection Layer Tuning Guide
  https://www.ti.com/lit/pdf/SLUA213
  Detaillierte Anleitung zur Optimierung der Erkennungsparameter

_______________________________________________________________________________

DOKUMENT-KONTROLLE

| Version | Datum | Autor | Änderungen |
|---------|-------|-------|-----------|
| 1.0 | 2026-08-27 | ezuehlke | Initial |

Gültig ab: 27.08.2026
Nächste Überprüfung: 27.02.2027

_______________________________________________________________________________