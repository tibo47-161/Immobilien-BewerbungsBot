#!/usr/bin/env python3
"""
Hauptklasse für den Immobilien-Bewerbungsbot
Orchestriert die verschiedenen Scraper und Automatisierungsprozesse

Autor: Manus AI Assistant
Datum: 2025-07-03
"""

import logging
import schedule
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from immobilien_bot import (
    ImmobilienAngebot, BewerbungsConfig, DatabaseManager,
    ImmonetScraper, ImmobilienScout24Scraper
)


class ImmobilienBewerbungsBot:
    """Hauptklasse für den automatisierten Immobilien-Bewerbungsbot"""
    
    def __init__(self, config: BewerbungsConfig):
        self.config = config
        self.db_manager = DatabaseManager()
        self.scrapers = {
            'immonet': ImmonetScraper(config),
            'immobilienscout24': ImmobilienScout24Scraper(config)
        }
        
        # Logging konfigurieren
        self.setup_logging()
        
        # Statistiken
        self.stats = {
            'gefundene_angebote': 0,
            'neue_angebote': 0,
            'erfolgreiche_bewerbungen': 0,
            'fehlgeschlagene_bewerbungen': 0,
            'letzter_lauf': None
        }
        
        # Thread-Safety
        self.lock = threading.Lock()
        self.running = False
    
    def setup_logging(self):
        """Konfiguriert das Logging-System"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('immobilien_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def starte_automatischen_modus(self, intervall_minuten: int = 30):
        """Startet den Bot im automatischen Modus mit regelmäßigen Durchläufen"""
        self.logger.info(f"Starte automatischen Modus mit {intervall_minuten} Minuten Intervall")
        
        # Schedule konfigurieren
        schedule.every(intervall_minuten).minutes.do(self.durchlauf_ausfuehren)
        
        # Ersten Durchlauf sofort starten
        self.durchlauf_ausfuehren()
        
        # Scheduler in separatem Thread laufen lassen
        self.running = True
        scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        scheduler_thread.start()
        
        return scheduler_thread
    
    def _scheduler_loop(self):
        """Führt den Scheduler in einer Endlosschleife aus"""
        while self.running:
            schedule.run_pending()
            threading.Event().wait(60)  # Prüfe jede Minute
    
    def stoppe_automatischen_modus(self):
        """Stoppt den automatischen Modus"""
        self.running = False
        schedule.clear()
        self.logger.info("Automatischer Modus gestoppt")
    
    def durchlauf_ausfuehren(self):
        """Führt einen kompletten Durchlauf aus: Suchen und Bewerben"""
        with self.lock:
            if self.stats['letzter_lauf'] and \
               datetime.now() - self.stats['letzter_lauf'] < timedelta(minutes=10):
                self.logger.info("Letzter Durchlauf war vor weniger als 10 Minuten, überspringe...")
                return
            
            self.stats['letzter_lauf'] = datetime.now()
        
        self.logger.info("Starte neuen Durchlauf...")
        
        try:
            # Neue Angebote suchen
            alle_neuen_angebote = self.suche_alle_neuen_angebote()
            
            if not alle_neuen_angebote:
                self.logger.info("Keine neuen Angebote gefunden")
                return
            
            self.logger.info(f"{len(alle_neuen_angebote)} neue Angebote gefunden")
            
            # Auf neue Angebote bewerben
            self.bewerbe_auf_angebote(alle_neuen_angebote)
            
            # Statistiken aktualisieren
            self.stats['neue_angebote'] += len(alle_neuen_angebote)
            
            # E-Mail-Benachrichtigung senden
            self.sende_zusammenfassung_email(alle_neuen_angebote)
            
        except Exception as e:
            self.logger.error(f"Fehler im Durchlauf: {e}")
            self.db_manager.log_speichern("ERROR", f"Durchlauf-Fehler: {e}")
    
    def suche_alle_neuen_angebote(self) -> List[ImmobilienAngebot]:
        """Sucht auf allen konfigurierten Websites nach neuen Angeboten"""
        alle_angebote = []
        
        # Parallel auf allen Websites suchen
        with ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
            future_to_scraper = {}
            
            for website, scraper in self.scrapers.items():
                for stadt in self.config.suchstaedte:
                    future = executor.submit(scraper.suche_neue_angebote, stadt)
                    future_to_scraper[future] = (website, stadt, scraper)
            
            for future in as_completed(future_to_scraper):
                website, stadt, scraper = future_to_scraper[future]
                try:
                    angebote = future.result(timeout=60)  # 60 Sekunden Timeout
                    self.logger.info(f"{website} - {stadt}: {len(angebote)} Angebote gefunden")
                    alle_angebote.extend(angebote)
                    self.stats['gefundene_angebote'] += len(angebote)
                except Exception as e:
                    self.logger.error(f"Fehler beim Suchen auf {website} in {stadt}: {e}")
        
        # Nur wirklich neue Angebote zurückgeben
        neue_angebote = []
        for angebot in alle_angebote:
            if not self.db_manager.ist_bereits_beworben(angebot.id):
                neue_angebote.append(angebot)
        
        return neue_angebote
    
    def bewerbe_auf_angebote(self, angebote: List[ImmobilienAngebot]):
        """Bewirbt sich auf eine Liste von Angeboten"""
        self.logger.info(f"Starte Bewerbungen auf {len(angebote)} Angebote")
        
        for angebot in angebote:
            try:
                # Scraper für die entsprechende Website holen
                scraper = self.scrapers.get(angebot.website)
                if not scraper:
                    self.logger.error(f"Kein Scraper für Website {angebot.website} verfügbar")
                    continue
                
                self.logger.info(f"Bewerbe mich auf: {angebot.titel} - {angebot.preis}€")
                
                # Bewerbung durchführen
                erfolg = scraper.bewerbe_auf_angebot(angebot)
                
                # Ergebnis in Datenbank speichern
                self.db_manager.bewerbung_speichern(angebot, erfolg)
                
                if erfolg:
                    self.stats['erfolgreiche_bewerbungen'] += 1
                    self.logger.info(f"Bewerbung erfolgreich: {angebot.titel}")
                    self.db_manager.log_speichern("INFO", f"Bewerbung erfolgreich", angebot.id)
                else:
                    self.stats['fehlgeschlagene_bewerbungen'] += 1
                    self.logger.warning(f"Bewerbung fehlgeschlagen: {angebot.titel}")
                    self.db_manager.log_speichern("WARNING", f"Bewerbung fehlgeschlagen", angebot.id)
                
                # Pause zwischen Bewerbungen
                import time
                import random
                time.sleep(random.uniform(30, 60))  # 30-60 Sekunden Pause
                
            except Exception as e:
                self.logger.error(f"Fehler bei Bewerbung auf {angebot.titel}: {e}")
                self.db_manager.bewerbung_speichern(angebot, False)
                self.stats['fehlgeschlagene_bewerbungen'] += 1
    
    def sende_zusammenfassung_email(self, neue_angebote: List[ImmobilienAngebot]):
        """Sendet eine E-Mail-Zusammenfassung der neuen Bewerbungen"""
        if not self.config.smtp_username or not neue_angebote:
            return
        
        try:
            import smtplib
            from email.mime.text import MimeText
            from email.mime.multipart import MimeMultipart
            
            # E-Mail erstellen
            msg = MimeMultipart()
            msg['From'] = self.config.smtp_username
            msg['To'] = self.config.email
            msg['Subject'] = f"Immobilien-Bot: {len(neue_angebote)} neue Bewerbungen"
            
            # E-Mail-Inhalt
            body = f"""
Hallo {self.config.vorname},

der Immobilien-Bot hat {len(neue_angebote)} neue Bewerbungen versendet:

"""
            
            for angebot in neue_angebote:
                body += f"""
- {angebot.titel}
  Preis: {angebot.preis}€, Zimmer: {angebot.zimmer}, Größe: {angebot.groesse}m²
  Ort: {angebot.ort}
  URL: {angebot.url}
  Website: {angebot.website}

"""
            
            body += f"""
Statistiken:
- Gefundene Angebote heute: {self.stats['gefundene_angebote']}
- Neue Angebote heute: {self.stats['neue_angebote']}
- Erfolgreiche Bewerbungen: {self.stats['erfolgreiche_bewerbungen']}
- Fehlgeschlagene Bewerbungen: {self.stats['fehlgeschlagene_bewerbungen']}

Viel Erfolg bei der Wohnungssuche!

Ihr Immobilien-Bot
"""
            
            msg.attach(MimeText(body, 'plain'))
            
            # E-Mail senden
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.smtp_username, self.config.smtp_password)
            text = msg.as_string()
            server.sendmail(self.config.smtp_username, self.config.email, text)
            server.quit()
            
            self.logger.info("Zusammenfassungs-E-Mail gesendet")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Senden der E-Mail: {e}")
    
    def zeige_statistiken(self):
        """Zeigt aktuelle Statistiken an"""
        print("\n" + "="*50)
        print("IMMOBILIEN-BOT STATISTIKEN")
        print("="*50)
        print(f"Gefundene Angebote: {self.stats['gefundene_angebote']}")
        print(f"Neue Angebote: {self.stats['neue_angebote']}")
        print(f"Erfolgreiche Bewerbungen: {self.stats['erfolgreiche_bewerbungen']}")
        print(f"Fehlgeschlagene Bewerbungen: {self.stats['fehlgeschlagene_bewerbungen']}")
        
        if self.stats['letzter_lauf']:
            print(f"Letzter Durchlauf: {self.stats['letzter_lauf'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("="*50)
    
    def cleanup(self):
        """Räumt alle Ressourcen auf"""
        self.stoppe_automatischen_modus()
        for scraper in self.scrapers.values():
            scraper.cleanup()
        self.logger.info("Bot heruntergefahren")


def main():
    """Hauptfunktion für den direkten Aufruf"""
    # Beispiel-Konfiguration
    config = BewerbungsConfig(
        anrede="Herr",
        vorname="Max",
        nachname="Mustermann",
        email="max.mustermann@example.com",
        telefon="0123456789",
        strasse="Musterstraße 1",
        plz="12345",
        ort="Berlin",
        bewerbungstext="""Sehr geehrte Damen und Herren,

hiermit bewerbe ich mich um die ausgeschriebene Wohnung. Ich bin ein zuverlässiger Mieter mit festem Einkommen und kann alle erforderlichen Unterlagen vorlegen.

Über eine positive Rückmeldung würde ich mich sehr freuen.

Mit freundlichen Grüßen
Max Mustermann""",
        max_preis=1500.0,
        min_zimmer=2,
        max_zimmer=4,
        suchstaedte=["Berlin"],
        
        # E-Mail Konfiguration (optional)
        smtp_username="",  # Hier E-Mail eintragen
        smtp_password=""   # Hier App-Passwort eintragen
    )
    
    # Bot erstellen
    bot = ImmobilienBewerbungsBot(config)
    
    try:
        print("Immobilien-Bewerbungsbot gestartet!")
        print("Drücken Sie Ctrl+C zum Beenden")
        
        # Automatischen Modus starten (alle 30 Minuten)
        scheduler_thread = bot.starte_automatischen_modus(intervall_minuten=30)
        
        # Hauptthread am Leben halten
        while bot.running:
            import time
            time.sleep(10)
            
            # Statistiken alle 10 Minuten anzeigen
            if datetime.now().minute % 10 == 0:
                bot.zeige_statistiken()
    
    except KeyboardInterrupt:
        print("\nBot wird beendet...")
        bot.cleanup()
        print("Bot erfolgreich beendet.")


if __name__ == "__main__":
    main()

