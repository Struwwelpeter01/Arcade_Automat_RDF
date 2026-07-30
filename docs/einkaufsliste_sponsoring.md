# Einkaufsliste – Sponsoring Arcade-Automat

Diese Liste ist für Sponsoren gedacht: sie zeigt konkret, welche Bauteile für den Arcade-Automaten benötigt werden, in welcher Stückzahl und zu welchem ungefähren Preis. Das Holzgehäuse selbst ist bewusst nicht enthalten. Alle Preise sind **ca.-Angaben auf Basis deutscher Elektronik-Versender (BerryBase, reichelt, funduino, JLCPCB)**, Stand Sommer 2026 – die genannten Marken/Modelle sind Beispielprodukte und beliebig gegen gleichwertige Alternativen austauschbar. Vor dem Druck für Sponsoren empfiehlt sich ein kurzer Preis-Check, da sich Verfügbarkeit/Preise ändern können.

Ausgangslage: 1x Raspberry Pi 5 ist bereits aus einem Vorprojekt vorhanden, es wird nur **ein weiterer** benötigt. Die Controller kommunizieren per eigenem 2,4-GHz-Funkmodul (nRF24L01+) statt Bluetooth. Das Display ist ein Standard-Arcade-Monitor der 19–24-Zoll-Klasse.

---

## 1. Rechner & Steuerung

| Menge | Bauteil | Beispielprodukt | ca. Preis/Stk. | ca. Gesamt |
|---|---|---|---|---|
| 1x | Raspberry Pi 5, 8GB RAM | Raspberry Pi 5 B (reichelt/BerryBase) | 95 € | 95 € |
| 1x | Offizielles Netzteil, USB-C PD 27W | Raspberry Pi 27W USB-C Netzteil | 12 € | 12 € |
| 1x | Gehäuse mit aktiver Kühlung | Raspberry Pi 5 Active Cooler Case | 15 € | 15 € |
| 1x | microSD-Karte 64GB (A2, high endurance) | SanDisk Extreme / Endurance 64GB | 12 € | 12 € |

**Zwischensumme: ca. 134 €**

## 2. Display

| Menge | Bauteil | Beispielprodukt | ca. Preis/Stk. | ca. Gesamt |
|---|---|---|---|---|
| 1x | Open-Frame Arcade-Monitor, 19–24", HDMI, rahmenlos, JAMMA-tauglich | z.B. div. Arcade-Zubehör-Shops/AliExpress | 90–130 € | ~110 € |

*Alternative (günstiger): gebrauchter 22"-Monitor ausschlachten (Elektronik + Panel, ohne Gehäuse), ca. 30–50 €.*

**Zwischensumme: ca. 110 €**

## 3. Selbstgebaute Wireless-Controller (pro Stück, x2 Controller)

| Menge/Controller | Bauteil | Beispielprodukt | ca. Preis/Stk. | ca. Gesamt/Controller |
|---|---|---|---|---|
| 1x | Arcade-Joystick mit Mikroschaltern | Standard-Arcade-Joystick | 12 € | 12 € |
| 4x | LED-Arcade-Taster 30mm, beleuchtet (5V) | BerryBase AB30L5 | 2,50 € | 10 € |
| 1x | Mikrocontroller | Arduino Pro Mini 328, 3,3V/8MHz | 8 € | 8 € |
| 1x | Funkmodul 2,4GHz mit Antenne | nRF24L01+ PA/LNA | 5 € | 5 € |
| 1x | LiPo-Akku 3,7V, 1000–2000mAh, JST-Stecker | Standard-LiPo-Zelle | 8 € | 8 € |
| 1x | Lade-IC-Modul mit Schutzschaltung | TP4056 (Micro-USB/USB-C) | 3 € | 3 € |
| 1x | Ein/Aus-Kippschalter | Standard-Kippschalter | 1,50 € | 1,50 € |
| 1x | Status-LED + Vorwiderstand | Standard-LED 3mm | 0,50 € | 0,50 € |
| 1 Paar | Ladekontakte für Dockingstation | Pogo-Pin-Set, 2-polig | 4 € | 4 € |

**ca. 52 € pro Controller × 2 = ca. 104 €**

## 4. Empfänger am Raspberry Pi

| Menge | Bauteil | Beispielprodukt | ca. Preis/Stk. | ca. Gesamt |
|---|---|---|---|---|
| 1x | Funkmodul 2,4GHz mit Antenne | nRF24L01+ PA/LNA | 5 € | 5 € |
| 1x | USB-HID-Brücke (meldet sich als Gamepad an) | Arduino Pro Micro, ATmega32U4 | 10 € | 10 € |

**Zwischensumme: ca. 15 €**

## 5. Platinenfertigung (Custom-PCB für Controller)

| Menge | Posten | Beispielanbieter | ca. Preis | ca. Gesamt |
|---|---|---|---|---|
| 1 Bestellung | PCB-Prototypfertigung, 5x Custom-Platine | JLCPCB (ab ~2$/5 Stk. + Versand) | ~25 € | 25 € |
| Pauschal | Lötzinn, Flussmittel, ggf. SMD-Lötpaste | – | – | 15 € |
| Pauschal | Bauteil-Grundausstattung (Widerstände, Kondensatoren, Pfostenstecker, Dioden) | – | – | 15 € |

**Zwischensumme: ca. 55 €**

## 6. NFC-System (Statuenerkennung)

| Menge | Bauteil | Beispielprodukt | ca. Preis/Stk. | ca. Gesamt |
|---|---|---|---|---|
| 3x | NFC-Lesemodul (I2C/SPI/UART) | PN532 NFC-Modul | 9 € | 27 € |
| 20x | NFC-Tags zum Einbau in die Statuen | NTAG213-Sticker, 25mm | 0,70 € | 14 € |

*Anzahl der Lesemodule (Spiel-/Spieler-/KI-Fach) ist eine Annahme – bitte an die finale Anzahl Statuen-Fächer im Gehäuse anpassen.*

**Zwischensumme: ca. 41 €**

## 7. Beleuchtung / Leuchtmittel

Zwei Arten von Beleuchtung sind vorgesehen: einfache beleuchtete Taster (bereits unter Punkt 3 gelistet, per GPIO ein-/ausschaltbar) und **adressierbare RGB-LEDs** für alles, was farbig auf Spielereignisse reagieren soll (Highscore, Game-Over-Flackern, Marquee, Seitenverkleidung).

| Menge | Bauteil | Beispielprodukt | ca. Preis/Stk. | ca. Gesamt |
|---|---|---|---|---|
| 2x | Adressierbarer RGB-LED-Streifen, 5V, 5m/300 LEDs | WS2812B (reichelt OPT ST4492 / BerryBase NeoPixel) | 29 € | 58 € |
| 2x | Logic-Level-Shifter 3,3V→5V (für saubere Datenleitung) | 74AHCT125 | 3 € | 6 € |
| 3x | Einzelne WS2812B-Pixel als Statuen-Fach-Indikator | WS2812B Single LED | 1 € | 3 € |
| 1x | *(optional)* Dedizierter Licht-Controller, entlastet den Pi bei Effekten | ESP32 Dev-Board | 8 € | 8 € |

**Zwischensumme: ca. 75 €** (inkl. optionalem ESP32)

## 8. Stromversorgung, Verkabelung & Kleinteile

| Menge | Bauteil | ca. Preis/Stk. | ca. Gesamt |
|---|---|---|---|
| 1x | 5V-Hauptnetzteil für LED-Strecke (z.B. 5V/10A Schaltnetzteil) | 20 € | 20 € |
| 1x | Kaltgerätebuchse mit Schalter & Sicherung (230V-Zuleitung Gehäuse) | 10 € | 10 € |
| 1 Set | Dupont-Kabel-Set (M-M/M-F/F-F) | 8 € | 8 € |
| 1 Set | JST-PH 2-Pin Steckverbinder-Set | 6 € | 6 € |
| 1 Set | Schrumpfschlauch-Sortiment | 5 € | 5 € |
| 2x | Lochrasterplatine/Breadboard für Prototyping | 4 € | 8 € |
| Pauschal | Kabelbinder, Kabelkanal, Klemmen | – | 10 € |

**Zwischensumme: ca. 67 €**

## 9. Optional / Nice-to-have

| Menge | Bauteil | ca. Preis |
|---|---|---|
| 1 Set | Sound: 2x Mini-Lautsprecher + Verstärkerplatine (z.B. PAM8403) | 15 € |
| – | Ersatzteile-Puffer (Buttons, Mikroschalter für Reparaturen während Bau/Ausstellung) | 15 € |
| 1 Set | Werkzeug: Lötkolben-Set, Multimeter (falls noch nicht vorhanden) | 40 € |

---

## Gesamtübersicht

| Kategorie | ca. Kosten |
|---|---|
| 1. Rechner & Steuerung | 134 € |
| 2. Display | 110 € |
| 3. Wireless-Controller (2x) | 104 € |
| 4. Empfänger am Pi | 15 € |
| 5. Platinenfertigung | 55 € |
| 6. NFC-System | 41 € |
| 7. Beleuchtung | 75 € |
| 8. Strom/Verkabelung/Kleinteile | 67 € |
| **Summe (Kernliste)** | **≈ 601 €** |
| 9. Optional | + 70 € |
| **Summe inkl. Optional** | **≈ 670 €** |

---

## Hinweise für das Team

- Annahmen, die vor dem Druck geprüft/angepasst werden sollten: Anzahl NFC-Fächer (aktuell 3 angenommen), Länge/Menge der LED-Streifen je nach Gehäusegröße, Displaygröße innerhalb der 19–24"-Spanne.
- Sponsoren können auch **einzelne Positionen** statt der Gesamtsumme übernehmen (z.B. "wir sponsern den Raspberry Pi" oder "wir sponsern das Display") – die Tabellen sind dafür bewusst nach Baugruppen sortiert.
- Nicht enthalten: Holzgehäuse/Rahmen (laut Absprache außen vor gelassen) und 3D-Druck-Filament für die Statuen (separates Thema).
