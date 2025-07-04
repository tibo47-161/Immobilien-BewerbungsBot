#!/usr/bin/env python3
"""
Setup-Skript für den Immobilien-Bewerbungsbot
Automatische Installation und Konfiguration

Autor: Manus AI Assistant
Datum: 2025-07-03
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path


def check_python_version():
    """Prüft die Python-Version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 oder höher ist erforderlich!")
        print(f"Aktuelle Version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python-Version: {sys.version}")


def install_requirements():
    """Installiert die erforderlichen Python-Pakete"""
    print("\n📦 Installiere erforderliche Pakete...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Alle Pakete erfolgreich installiert!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Installieren der Pakete: {e}")
        sys.exit(1)


def check_chrome_driver():
    """Prüft, ob ChromeDriver verfügbar ist"""
    print("\n🌐 Prüfe ChromeDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        print("✅ ChromeDriver ist verfügbar!")
        
    except Exception as e:
        print(f"⚠️ ChromeDriver-Problem: {e}")
        print("\n💡 Lösungsvorschläge:")
        print("1. Installieren Sie Google Chrome")
        print("2. Installieren Sie ChromeDriver:")
        print("   - Ubuntu/Debian: sudo apt-get install chromium-chromedriver")
        print("   - macOS: brew install chromedriver")
        print("   - Windows: Laden Sie ChromeDriver von https://chromedriver.chromium.org/ herunter")


def create_directories():
    """Erstellt erforderliche Verzeichnisse"""
    print("\n📁 Erstelle Verzeichnisse...")
    
    directories = [
        "logs",
        "templates",
        "backups",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Verzeichnis erstellt: {directory}")


def setup_config():
    """Hilft beim Einrichten der Konfiguration"""
    print("\n⚙️ Konfiguration einrichten...")
    
    config_file = "config.yaml"
    
    if os.path.exists(config_file):
        response = input(f"Konfigurationsdatei {config_file} existiert bereits. Überschreiben? (j/N): ")
        if response.lower() != 'j':
            print("Konfiguration beibehalten.")
            return
    
    print("\nBitte geben Sie Ihre Daten ein:")
    
    # Persönliche Daten abfragen
    print("\n👤 Persönliche Daten:")
    anrede = input("Anrede (Herr/Frau/Divers) [Herr]: ") or "Herr"
    vorname = input("Vorname: ")
    nachname = input("Nachname: ")
    email = input("E-Mail-Adresse: ")
    telefon = input("Telefonnummer (optional): ")
    strasse = input("Straße und Hausnummer: ")
    plz = input("Postleitzahl: ")
    ort = input("Ort: ")
    
    # Suchkriterien abfragen
    print("\n🔍 Suchkriterien:")
    max_preis = float(input("Maximaler Mietpreis in Euro [1500]: ") or "1500")
    min_zimmer = int(input("Mindestanzahl Zimmer [2]: ") or "2")
    max_zimmer = int(input("Maximale Anzahl Zimmer [4]: ") or "4")
    
    suchstaedte = []
    print("Suchstädte (Enter für Ende):")
    while True:
        stadt = input("Stadt: ")
        if not stadt:
            break
        suchstaedte.append(stadt)
    
    if not suchstaedte:
        suchstaedte = ["Berlin"]
    
    # E-Mail-Konfiguration
    print("\n📧 E-Mail-Konfiguration (für Benachrichtigungen):")
    smtp_username = input("E-Mail-Adresse für Benachrichtigungen (optional): ")
    smtp_password = ""
    if smtp_username:
        smtp_password = input("App-Passwort (nicht das normale Passwort!): ")
    
    # Bewerbungstext
    print("\n✍️ Bewerbungstext:")
    print("Geben Sie Ihren Standard-Bewerbungstext ein (Enter für Standard-Text):")
    bewerbungstext = input() or f"""Sehr geehrte Damen und Herren,

hiermit bewerbe ich mich um die ausgeschriebene Wohnung. Ich bin ein zuverlässiger Mieter mit festem Einkommen und kann alle erforderlichen Unterlagen vorlegen.

Über eine positive Rückmeldung würde ich mich sehr freuen.

Mit freundlichen Grüßen
{vorname} {nachname}"""
    
    # Konfiguration erstellen
    config = {
        'personal': {
            'anrede': anrede,
            'vorname': vorname,
            'nachname': nachname,
            'email': email,
            'telefon': telefon,
            'strasse': strasse,
            'plz': plz,
            'ort': ort
        },
        'bewerbungstext': bewerbungstext,
        'suchkriterien': {
            'max_preis': max_preis,
            'min_zimmer': min_zimmer,
            'max_zimmer': max_zimmer,
            'suchstaedte': suchstaedte
        },
        'email': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_username': smtp_username,
            'smtp_password': smtp_password,
            'benachrichtigungen': {
                'email_bei_neuen_angeboten': True,
                'email_bei_fehlern': True,
                'tages_zusammenfassung': True,
                'wochen_zusammenfassung': False,
                'min_angebote_fuer_email': 1,
                'max_emails_pro_tag': 10
            }
        },
        'bot': {
            'intervall_minuten': 30,
            'max_bewerbungen_pro_tag': 20,
            'pause_zwischen_bewerbungen': {
                'min': 30,
                'max': 60
            },
            'anti_detection': {
                'random_user_agents': True,
                'random_delays': True,
                'headless_browser': True
            },
            'aktive_websites': {
                'immonet': True,
                'immobilienscout24': False
            }
        },
        'database': {
            'pfad': 'immobilien_bot.db',
            'backup_intervall_tage': 7
        },
        'logging': {
            'level': 'INFO',
            'datei': 'immobilien_bot.log',
            'max_groesse_mb': 10,
            'backup_anzahl': 5
        }
    }
    
    # Konfiguration speichern
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Konfiguration gespeichert in {config_file}")


def create_start_script():
    """Erstellt ein Start-Skript"""
    print("\n🚀 Erstelle Start-Skript...")
    
    start_script = """#!/bin/bash
# Immobilien-Bot Starter

echo "🏠 Starte Immobilien-Bewerbungsbot..."

# Prüfe, ob Python verfügbar ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 ist nicht installiert!"
    exit 1
fi

# Prüfe, ob Konfiguration existiert
if [ ! -f "config.yaml" ]; then
    echo "❌ Konfigurationsdatei config.yaml nicht gefunden!"
    echo "Führen Sie zuerst 'python3 setup.py' aus."
    exit 1
fi

# Bot starten
python3 immobilien_bot_main.py

echo "Bot beendet."
"""
    
    with open("start_bot.sh", "w") as f:
        f.write(start_script)
    
    # Ausführbar machen
    os.chmod("start_bot.sh", 0o755)
    print("✅ Start-Skript erstellt: start_bot.sh")


def show_next_steps():
    """Zeigt die nächsten Schritte an"""
    print("\n" + "="*60)
    print("🎉 SETUP ABGESCHLOSSEN!")
    print("="*60)
    print("\n📋 Nächste Schritte:")
    print("1. Bearbeiten Sie config.yaml und tragen Sie Ihre echten Daten ein")
    print("2. Für E-Mail-Benachrichtigungen:")
    print("   - Gmail: Aktivieren Sie 2FA und erstellen Sie ein App-Passwort")
    print("   - Andere: Passen Sie SMTP-Einstellungen in config.yaml an")
    print("3. Starten Sie den Bot:")
    print("   - Linux/macOS: ./start_bot.sh")
    print("   - Windows: python immobilien_bot_main.py")
    print("   - Oder: python3 immobilien_bot_main.py")
    print("\n⚠️ WICHTIGE HINWEISE:")
    print("- Verwenden Sie den Bot verantwortungsvoll")
    print("- Respektieren Sie die Nutzungsbedingungen der Websites")
    print("- Prüfen Sie regelmäßig die Logs")
    print("- Der Bot läuft im Hintergrund - beenden Sie ihn mit Ctrl+C")
    print("\n📚 Weitere Informationen finden Sie in der README.md")
    print("="*60)


def main():
    """Hauptfunktion des Setup-Skripts"""
    print("🏠 Immobilien-Bewerbungsbot Setup")
    print("="*40)
    
    # Prüfungen
    check_python_version()
    
    # Installation
    install_requirements()
    check_chrome_driver()
    create_directories()
    
    # Konfiguration
    setup_config()
    create_start_script()
    
    # Abschluss
    show_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup abgebrochen.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        sys.exit(1)

