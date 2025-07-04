# 🏠 Immobilien-Bewerbungsbot

Ein automatisierter Python-Bot, der neue Immobilienangebote von Immonet und ImmobilienScout24 überwacht und automatisch Bewerbungen mit vorgefertigtem Text versendet.

## 📋 Inhaltsverzeichnis

- [Überblick](#überblick)
- [Features](#features)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Verwendung](#verwendung)
- [Architektur](#architektur)
- [Rechtliche Hinweise](#rechtliche-hinweise)
- [Troubleshooting](#troubleshooting)
- [Beitragen](#beitragen)
- [Lizenz](#lizenz)

## 🎯 Überblick

Der Immobilien-Bewerbungsbot automatisiert den zeitaufwändigen Prozess der Wohnungssuche, indem er kontinuierlich nach neuen Angeboten sucht und automatisch qualitätsvolle Bewerbungen versendet. Das System wurde mit modernen Python-Technologien entwickelt und folgt objektorientierten Designprinzipien.

### Hauptfunktionen

- **Automatische Überwachung**: Kontinuierliche Suche nach neuen Immobilienangeboten
- **Intelligente Filterung**: Angebote werden nach konfigurierbaren Kriterien gefiltert
- **Automatische Bewerbung**: Formulare werden automatisch mit personalisierten Daten ausgefüllt
- **E-Mail-Benachrichtigungen**: Umfassende Benachrichtigungen über neue Bewerbungen
- **Datenbank-Tracking**: Verhindert Doppelbewerbungen durch intelligente Verfolgung
- **Anti-Detection**: Implementiert Techniken zur Umgehung von Bot-Erkennungssystemen

## ✨ Features

### 🔍 Web-Scraping
- **Multi-Website-Support**: Unterstützung für Immonet und ImmobilienScout24
- **Robuste Datenextraktion**: Zuverlässige Extraktion von Angebotsdaten
- **Anti-Bot-Maßnahmen**: User-Agent-Rotation und intelligente Verzögerungen
- **Fehlerbehandlung**: Umfassende Fehlerbehandlung und Wiederherstellung

### 🤖 Automatisierung
- **Formular-Ausfüllung**: Automatisches Ausfüllen von Bewerbungsformularen
- **Personalisierte Nachrichten**: Vorgefertigte, anpassbare Bewerbungstexte
- **Zeitgesteuerte Ausführung**: Konfigurierbare Intervalle für automatische Durchläufe
- **Rate Limiting**: Respektvolle Anfrage-Frequenz zum Schutz der Zielwebsites

### 📊 Datenmanagement
- **SQLite-Datenbank**: Lokale Speicherung aller Bewerbungsdaten
- **Duplikatserkennung**: Verhindert mehrfache Bewerbungen auf dasselbe Angebot
- **Statistiken**: Detaillierte Tracking- und Reporting-Funktionen
- **Backup-System**: Automatische Datensicherung

### 📧 Benachrichtigungen
- **E-Mail-Alerts**: Sofortige Benachrichtigungen über neue Bewerbungen
- **HTML-Templates**: Professionell gestaltete E-Mail-Vorlagen
- **Tages-/Wochenberichte**: Regelmäßige Zusammenfassungen der Bot-Aktivitäten
- **Fehler-Benachrichtigungen**: Automatische Meldung bei Problemen

## 🚀 Installation

### Systemanforderungen

- **Python**: Version 3.8 oder höher
- **Betriebssystem**: Windows, macOS, oder Linux
- **Browser**: Google Chrome (für Selenium WebDriver)
- **Speicher**: Mindestens 512 MB RAM
- **Festplatte**: 100 MB freier Speicherplatz

### Automatische Installation

1. **Repository klonen oder Dateien herunterladen**
   ```bash
   # Alle Dateien in einen Ordner kopieren
   mkdir immobilien-bot
   cd immobilien-bot
   ```

2. **Setup-Skript ausführen**
   ```bash
   python3 setup.py
   ```

Das Setup-Skript führt automatisch folgende Schritte aus:
- Überprüfung der Python-Version
- Installation aller erforderlichen Pakete
- Überprüfung des ChromeDrivers
- Erstellung der Verzeichnisstruktur
- Interaktive Konfiguration

### Manuelle Installation

Falls die automatische Installation nicht funktioniert:

1. **Python-Pakete installieren**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **ChromeDriver installieren**
   - **Ubuntu/Debian**: `sudo apt-get install chromium-chromedriver`
   - **macOS**: `brew install chromedriver`
   - **Windows**: Download von [ChromeDriver](https://chromedriver.chromium.org/)

3. **Verzeichnisse erstellen**
   ```bash
   mkdir logs templates backups data
   ```

## ⚙️ Konfiguration

### Grundkonfiguration

Die Hauptkonfiguration erfolgt über die Datei `config.yaml`. Eine Beispielkonfiguration wird beim Setup erstellt.

#### Persönliche Daten
```yaml
personal:
  anrede: "Herr"  # Herr, Frau, Divers
  vorname: "Max"
  nachname: "Mustermann"
  email: "max.mustermann@example.com"
  telefon: "0123456789"
  strasse: "Musterstraße 1"
  plz: "12345"
  ort: "Berlin"
```

#### Suchkriterien
```yaml
suchkriterien:
  max_preis: 1500.0      # Maximaler Mietpreis in Euro
  min_zimmer: 2          # Mindestanzahl Zimmer
  max_zimmer: 4          # Maximale Anzahl Zimmer
  suchstaedte:           # Liste der Suchstädte
    - "Berlin"
    - "München"
    - "Hamburg"
```

#### Bewerbungstext
```yaml
bewerbungstext: |
  Sehr geehrte Damen und Herren,
  
  hiermit bewerbe ich mich um die ausgeschriebene Wohnung. 
  Ich bin ein zuverlässiger Mieter mit festem Einkommen 
  und kann alle erforderlichen Unterlagen vorlegen.
  
  Über eine positive Rückmeldung würde ich mich sehr freuen.
  
  Mit freundlichen Grüßen
  Max Mustermann
```

### E-Mail-Konfiguration

Für E-Mail-Benachrichtigungen müssen SMTP-Einstellungen konfiguriert werden:

```yaml
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  smtp_username: "ihre-email@gmail.com"
  smtp_password: "ihr-app-passwort"
```

**Wichtig für Gmail-Nutzer:**
1. Aktivieren Sie die 2-Faktor-Authentifizierung
2. Erstellen Sie ein App-Passwort (nicht Ihr normales Passwort)
3. Verwenden Sie das App-Passwort in der Konfiguration

### Bot-Einstellungen

```yaml
bot:
  intervall_minuten: 30              # Suchintervall
  max_bewerbungen_pro_tag: 20        # Tägliches Limit
  pause_zwischen_bewerbungen:        # Pausen zwischen Bewerbungen
    min: 30
    max: 60
  
  aktive_websites:
    immonet: true
    immobilienscout24: false         # Aufgrund Bot-Erkennung
```

## 🎮 Verwendung

### Erster Start

1. **Konfiguration prüfen**
   ```bash
   # Konfigurationsdatei bearbeiten
   nano config.yaml
   ```

2. **Test durchführen**
   ```bash
   python3 test_bot.py
   ```

3. **Bot starten**
   ```bash
   # Linux/macOS
   ./start_bot.sh
   
   # Windows
   python immobilien_bot_main.py
   ```

### Automatischer Modus

Der Bot läuft standardmäßig im automatischen Modus:

- **Kontinuierliche Überwachung**: Sucht alle 30 Minuten nach neuen Angeboten
- **Automatische Bewerbungen**: Bewirbt sich sofort auf passende Angebote
- **E-Mail-Benachrichtigungen**: Sendet Berichte über neue Bewerbungen
- **Logging**: Protokolliert alle Aktivitäten in `immobilien_bot.log`

### Manueller Modus

Für einmalige Durchläufe:

```python
from immobilien_bot_main import ImmobilienBewerbungsBot
from immobilien_bot import BewerbungsConfig

# Konfiguration laden
config = BewerbungsConfig(...)

# Bot erstellen
bot = ImmobilienBewerbungsBot(config)

# Einmaligen Durchlauf ausführen
bot.durchlauf_ausfuehren()

# Statistiken anzeigen
bot.zeige_statistiken()
```

### Überwachung und Kontrolle

#### Log-Dateien
- **immobilien_bot.log**: Hauptprotokoll aller Aktivitäten
- **logs/**: Zusätzliche Log-Dateien nach Datum

#### Datenbank
- **immobilien_bot.db**: SQLite-Datenbank mit allen Bewerbungsdaten
- Tabellen: `bewerbungen`, `logs`

#### Statistiken
```bash
# Statistiken anzeigen
python3 -c "
from immobilien_bot_main import ImmobilienBewerbungsBot
from immobilien_bot import BewerbungsConfig
import yaml

with open('config.yaml') as f:
    config_data = yaml.safe_load(f)

# Konfiguration aus YAML laden
config = BewerbungsConfig(**config_data['personal'])
bot = ImmobilienBewerbungsBot(config)
bot.zeige_statistiken()
"
```

## 🏗️ Architektur

### Klassenstruktur

Das System folgt einer modularen, objektorientierten Architektur:

#### Kernklassen

**BewerbungsConfig**
- Zentrale Konfigurationsklasse
- Speichert alle Benutzereinstellungen
- Validierung der Eingabedaten

**ImmobilienAngebot**
- Datenklasse für Immobilienangebote
- Standardisierte Repräsentation aller Angebotsdaten
- Hash- und Gleichheitsfunktionen für Duplikatserkennung

**DatabaseManager**
- Verwaltung der SQLite-Datenbank
- CRUD-Operationen für Bewerbungen und Logs
- Duplikatserkennung und Statistiken

#### Web-Scraping

**WebScraperBase (Abstrakte Basisklasse)**
- Gemeinsame Funktionalitäten aller Scraper
- Session-Management und Anti-Detection
- WebDriver-Konfiguration

**ImmonetScraper**
- Spezialisierter Scraper für Immonet.de
- Angebots-Extraktion und Formular-Ausfüllung
- Robuste Fehlerbehandlung

**ImmobilienScout24Scraper**
- Scraper für ImmobilienScout24.de
- Erweiterte Anti-Detection-Techniken
- Derzeit eingeschränkt durch Bot-Erkennung

#### Automatisierung

**ImmobilienBewerbungsBot**
- Hauptorchestrator des Systems
- Thread-Management für parallele Ausführung
- Scheduler für automatische Durchläufe

**EmailManager**
- Verwaltung aller E-Mail-Funktionalitäten
- HTML-Template-System
- SMTP-Integration

**NotificationManager**
- Zentrale Benachrichtigungsverwaltung
- Multi-Channel-Support (E-Mail, zukünftig: Telegram, Webhooks)
- Rate-Limiting für Benachrichtigungen

### Datenfluss

1. **Initialisierung**: Konfiguration laden, Datenbank initialisieren
2. **Suche**: Parallele Suche auf allen konfigurierten Websites
3. **Filterung**: Anwendung der Suchkriterien und Duplikatsprüfung
4. **Bewerbung**: Automatisches Ausfüllen und Absenden der Formulare
5. **Protokollierung**: Speicherung in Datenbank und Log-Dateien
6. **Benachrichtigung**: E-Mail-Versand über neue Bewerbungen

### Sicherheitsfeatures

#### Anti-Detection
- **User-Agent-Rotation**: Zufällige Browser-Identifikation
- **Request-Delays**: Natürliche Pausen zwischen Anfragen
- **Session-Management**: Persistente HTTP-Sessions
- **Headless-Browser**: Unsichtbare Browser-Automatisierung

#### Datenschutz
- **Lokale Speicherung**: Alle Daten bleiben auf Ihrem System
- **Verschlüsselung**: Passwörter werden sicher gespeichert
- **Minimale Datensammlung**: Nur notwendige Informationen werden gespeichert

## ⚖️ Rechtliche Hinweise

### Nutzungsbedingungen

**Wichtige Warnung**: Die Verwendung dieses Bots kann gegen die Nutzungsbedingungen der Zielwebsites verstoßen. Benutzer sind selbst verantwortlich für die Einhaltung aller geltenden Gesetze und Bestimmungen.

### Empfohlene Praktiken

#### Respektvolle Nutzung
- **Rate Limiting**: Verwenden Sie angemessene Verzögerungen zwischen Anfragen
- **Qualitätsvolle Bewerbungen**: Senden Sie nur relevante, personalisierte Bewerbungen
- **Monitoring**: Überwachen Sie die Bot-Aktivitäten regelmäßig
- **Manuelle Überprüfung**: Prüfen Sie wichtige Angebote manuell nach

#### Rechtliche Compliance
- **Robots.txt**: Respektieren Sie die robots.txt-Dateien der Websites
- **Urheberrecht**: Verwenden Sie keine urheberrechtlich geschützten Inhalte
- **Datenschutz**: Sammeln Sie keine persönlichen Daten Dritter
- **Spam-Vermeidung**: Vermeiden Sie übermäßige oder irrelevante Bewerbungen

### Haftungsausschluss

Die Entwickler dieses Bots übernehmen keine Verantwortung für:
- Schäden durch unsachgemäße Verwendung
- Verstöße gegen Nutzungsbedingungen
- Rechtliche Konsequenzen der Nutzung
- Verlust von Daten oder Bewerbungschancen

**Verwendung auf eigene Gefahr**: Benutzer sind vollständig verantwortlich für die Verwendung dieses Tools und alle daraus resultierenden Konsequenzen.

## 🔧 Troubleshooting

### Häufige Probleme

#### ChromeDriver-Fehler
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Lösung:**
1. ChromeDriver installieren (siehe Installation)
2. Pfad zur PATH-Variable hinzufügen
3. Chrome-Browser aktualisieren

#### Import-Fehler
```
ImportError: No module named 'selenium'
```

**Lösung:**
```bash
pip3 install -r requirements.txt
```

#### Bot-Erkennung
```
Ich bin kein Roboter - Seite erscheint
```

**Lösung:**
1. Längere Pausen zwischen Anfragen konfigurieren
2. User-Agent-Rotation aktivieren
3. Proxy-Server verwenden (erweiterte Konfiguration)

#### E-Mail-Probleme
```
SMTPAuthenticationError: Username and Password not accepted
```

**Lösung für Gmail:**
1. 2-Faktor-Authentifizierung aktivieren
2. App-Passwort erstellen
3. App-Passwort in Konfiguration verwenden

### Debug-Modus

Für detaillierte Fehleranalyse:

```yaml
logging:
  level: "DEBUG"  # Statt "INFO"
```

### Log-Analyse

Wichtige Log-Nachrichten:
- `INFO`: Normale Operationen
- `WARNING`: Potentielle Probleme
- `ERROR`: Schwerwiegende Fehler
- `DEBUG`: Detaillierte Ausführungsinformationen

### Performance-Optimierung

#### Speicher-Optimierung
```yaml
bot:
  max_bewerbungen_pro_tag: 10  # Reduzieren bei Speicherproblemen
```

#### Netzwerk-Optimierung
```yaml
bot:
  pause_zwischen_bewerbungen:
    min: 60  # Längere Pausen
    max: 120
```

## 🤝 Beitragen

### Entwicklung

Das Projekt ist offen für Beiträge. Bereiche für Verbesserungen:

#### Neue Features
- **Zusätzliche Websites**: Integration weiterer Immobilienportale
- **Erweiterte Filterung**: Komplexere Suchkriterien
- **Machine Learning**: Intelligente Angebotsbewertung
- **Mobile App**: Smartphone-Integration

#### Verbesserungen
- **Anti-Detection**: Erweiterte Umgehungstechniken
- **Performance**: Optimierung der Scraping-Geschwindigkeit
- **UI/UX**: Grafische Benutzeroberfläche
- **Monitoring**: Erweiterte Überwachungstools

### Code-Struktur

```
immobilien-bot/
├── immobilien_bot.py          # Hauptklassen und Scraper
├── immobilien_bot_main.py     # Orchestrator und Hauptlogik
├── email_manager.py           # E-Mail-Funktionalitäten
├── config.yaml               # Konfigurationsdatei
├── setup.py                  # Installations-Skript
├── test_bot.py              # Test-Suite
├── requirements.txt         # Python-Abhängigkeiten
├── README.md               # Diese Dokumentation
├── logs/                   # Log-Dateien
├── templates/             # E-Mail-Templates
├── backups/              # Datenbank-Backups
└── data/                # Zusätzliche Daten
```

### Coding-Standards

- **PEP 8**: Python-Stil-Richtlinien befolgen
- **Type Hints**: Verwendung von Typ-Annotationen
- **Docstrings**: Umfassende Dokumentation aller Funktionen
- **Error Handling**: Robuste Fehlerbehandlung
- **Testing**: Unit-Tests für alle neuen Features

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe LICENSE-Datei für Details.

### MIT-Lizenz Zusammenfassung

- ✅ **Kommerzielle Nutzung**: Erlaubt
- ✅ **Modifikation**: Erlaubt
- ✅ **Distribution**: Erlaubt
- ✅ **Private Nutzung**: Erlaubt
- ❌ **Haftung**: Ausgeschlossen
- ❌ **Garantie**: Keine Gewährleistung

---

## 📞 Support

### Community

- **GitHub Issues**: Für Bug-Reports und Feature-Requests
- **Diskussionen**: Für allgemeine Fragen und Ideen
- **Wiki**: Für erweiterte Dokumentation und Tutorials

### Professioneller Support

Für Unternehmen und erweiterte Anpassungen:
- **Beratung**: Individuelle Implementierungsberatung
- **Anpassungen**: Maßgeschneiderte Entwicklung
- **Wartung**: Langfristige Unterstützung und Updates

---

**Entwickelt von tibo**

*Letzte Aktualisierung: 2025-07-03*

