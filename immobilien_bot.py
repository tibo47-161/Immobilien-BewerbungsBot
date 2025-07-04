#!/usr/bin/env python3
"""
Immobilien-Bewerbungsbot
Automatisierte Bewerbung auf neue Immobilienangebote von Immonet und ImmobilienScout24

Autor: Manus AI Assistant
Datum: 2025-07-03
"""

import time
import random
import sqlite3
import smtplib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Konfiguration und Datenstrukturen
@dataclass
class ImmobilienAngebot:
    """Datenklasse für ein Immobilienangebot"""
    id: str
    titel: str
    preis: float
    groesse: float
    zimmer: int
    ort: str
    url: str
    anbieter: str
    erstellt: datetime
    website: str  # 'immonet' oder 'immobilienscout24'
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, ImmobilienAngebot):
            return self.id == other.id
        return False


@dataclass
class BewerbungsConfig:
    """Konfiguration für Bewerbungen"""
    anrede: str = "Herr"  # Herr, Frau, Divers
    vorname: str = ""
    nachname: str = ""
    email: str = ""
    telefon: str = ""
    strasse: str = ""
    plz: str = ""
    ort: str = ""
    bewerbungstext: str = ""
    
    # E-Mail Konfiguration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    
    # Suchkriterien
    max_preis: float = 2000.0
    min_zimmer: int = 1
    max_zimmer: int = 5
    suchstaedte: List[str] = None
    
    def __post_init__(self):
        if self.suchstaedte is None:
            self.suchstaedte = ["Berlin", "München", "Hamburg"]


class DatabaseManager:
    """Verwaltet die SQLite-Datenbank für bereits beworbene Angebote"""
    
    def __init__(self, db_path: str = "immobilien_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialisiert die Datenbank-Tabellen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bewerbungen (
                    id TEXT PRIMARY KEY,
                    titel TEXT,
                    preis REAL,
                    groesse REAL,
                    zimmer INTEGER,
                    ort TEXT,
                    url TEXT,
                    anbieter TEXT,
                    website TEXT,
                    beworben_am TIMESTAMP,
                    erfolgreich BOOLEAN
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    angebot_id TEXT
                )
            ''')
            conn.commit()
    
    def ist_bereits_beworben(self, angebot_id: str) -> bool:
        """Prüft, ob bereits eine Bewerbung für dieses Angebot existiert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM bewerbungen WHERE id = ?", (angebot_id,))
            return cursor.fetchone() is not None
    
    def bewerbung_speichern(self, angebot: ImmobilienAngebot, erfolgreich: bool):
        """Speichert eine Bewerbung in der Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO bewerbungen 
                (id, titel, preis, groesse, zimmer, ort, url, anbieter, website, beworben_am, erfolgreich)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                angebot.id, angebot.titel, angebot.preis, angebot.groesse,
                angebot.zimmer, angebot.ort, angebot.url, angebot.anbieter,
                angebot.website, datetime.now(), erfolgreich
            ))
            conn.commit()
    
    def log_speichern(self, level: str, message: str, angebot_id: str = None):
        """Speichert einen Log-Eintrag"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (timestamp, level, message, angebot_id)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now(), level, message, angebot_id))
            conn.commit()


class WebScraperBase(ABC):
    """Abstrakte Basisklasse für Website-spezifische Scraper"""
    
    def __init__(self, config: BewerbungsConfig):
        self.config = config
        self.session = requests.Session()
        self.setup_session()
        
        # Selenium WebDriver Setup
        self.driver = None
        self.setup_webdriver()
    
    def setup_session(self):
        """Konfiguriert die HTTP-Session"""
        self.session.headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def setup_webdriver(self):
        """Konfiguriert den Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Für Server-Betrieb
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={self.get_random_user_agent()}')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            logging.error(f"Fehler beim Initialisieren des WebDrivers: {e}")
            self.driver = None
    
    def get_random_user_agent(self) -> str:
        """Gibt einen zufälligen User-Agent zurück"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        return random.choice(user_agents)
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Fügt eine zufällige Verzögerung hinzu"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    @abstractmethod
    def suche_neue_angebote(self, stadt: str) -> List[ImmobilienAngebot]:
        """Sucht nach neuen Angeboten in einer Stadt"""
        pass
    
    @abstractmethod
    def bewerbe_auf_angebot(self, angebot: ImmobilienAngebot) -> bool:
        """Bewirbt sich auf ein spezifisches Angebot"""
        pass
    
    def cleanup(self):
        """Räumt Ressourcen auf"""
        if self.driver:
            self.driver.quit()
        self.session.close()


class ImmonetScraper(WebScraperBase):
    """Scraper für Immonet.de"""
    
    BASE_URL = "https://www.immonet.de"
    SEARCH_URL = "https://www.immonet.de/classified-search"
    
    def suche_neue_angebote(self, stadt: str) -> List[ImmobilienAngebot]:
        """Sucht nach neuen Angeboten auf Immonet"""
        angebote = []
        
        try:
            # Suchparameter für Immonet
            params = {
                'distributionTypes': 'Rent',
                'estateTypes': 'House,Apartment',
                'locations': self._get_location_id(stadt),
                'order': 'Default'
            }
            
            response = self.session.get(self.SEARCH_URL, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Angebote extrahieren
            angebot_elements = soup.find_all('div', class_='classified-item')
            
            for element in angebot_elements:
                try:
                    angebot = self._parse_angebot_element(element, stadt)
                    if angebot and self._erfuellt_kriterien(angebot):
                        angebote.append(angebot)
                except Exception as e:
                    logging.warning(f"Fehler beim Parsen eines Angebots: {e}")
                    continue
            
            self.random_delay()
            
        except Exception as e:
            logging.error(f"Fehler beim Suchen auf Immonet für {stadt}: {e}")
        
        return angebote
    
    def _get_location_id(self, stadt: str) -> str:
        """Ermittelt die Location-ID für eine Stadt (vereinfacht)"""
        # In einer echten Implementierung würde man die Location-IDs 
        # durch eine separate API-Anfrage oder Mapping-Tabelle ermitteln
        location_mapping = {
            'Berlin': 'AD08DE8634',
            'München': 'AD08DE8635',
            'Hamburg': 'AD08DE8636'
        }
        return location_mapping.get(stadt, 'AD08DE8634')  # Default: Berlin
    
    def _parse_angebot_element(self, element, stadt: str) -> Optional[ImmobilienAngebot]:
        """Parst ein einzelnes Angebot-Element"""
        try:
            # URL extrahieren
            link_element = element.find('a', href=True)
            if not link_element:
                return None
            
            url = self.BASE_URL + link_element['href']
            angebot_id = self._extract_id_from_url(url)
            
            # Titel extrahieren
            titel_element = element.find('h2') or element.find('h3')
            titel = titel_element.get_text(strip=True) if titel_element else "Unbekannt"
            
            # Preis extrahieren
            preis_element = element.find('span', class_='price')
            preis_text = preis_element.get_text(strip=True) if preis_element else "0"
            preis = self._parse_preis(preis_text)
            
            # Weitere Details extrahieren (vereinfacht)
            details = element.find('div', class_='details')
            zimmer = 2  # Default-Wert
            groesse = 50.0  # Default-Wert
            
            if details:
                detail_text = details.get_text()
                zimmer = self._extract_zimmer(detail_text)
                groesse = self._extract_groesse(detail_text)
            
            return ImmobilienAngebot(
                id=angebot_id,
                titel=titel,
                preis=preis,
                groesse=groesse,
                zimmer=zimmer,
                ort=stadt,
                url=url,
                anbieter="Unbekannt",
                erstellt=datetime.now(),
                website="immonet"
            )
            
        except Exception as e:
            logging.warning(f"Fehler beim Parsen eines Angebot-Elements: {e}")
            return None
    
    def _extract_id_from_url(self, url: str) -> str:
        """Extrahiert die Angebots-ID aus der URL"""
        # Beispiel: https://www.immonet.de/expose/3814ec52-e485-45f0-8d7e-512e039d9c66
        parts = url.split('/')
        for part in parts:
            if len(part) == 36 and part.count('-') == 4:  # UUID Format
                return part
        return url.split('/')[-1]  # Fallback
    
    def _parse_preis(self, preis_text: str) -> float:
        """Parst den Preis aus dem Text"""
        import re
        # Extrahiert Zahlen aus Text wie "1.472 € Kaltmiete"
        numbers = re.findall(r'[\d.,]+', preis_text.replace('.', '').replace(',', '.'))
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        return 0.0
    
    def _extract_zimmer(self, text: str) -> int:
        """Extrahiert die Anzahl der Zimmer"""
        import re
        zimmer_match = re.search(r'(\d+)\s*Zimmer', text)
        if zimmer_match:
            return int(zimmer_match.group(1))
        return 2  # Default
    
    def _extract_groesse(self, text: str) -> float:
        """Extrahiert die Wohnfläche"""
        import re
        groesse_match = re.search(r'(\d+(?:[.,]\d+)?)\s*m²', text)
        if groesse_match:
            return float(groesse_match.group(1).replace(',', '.'))
        return 50.0  # Default
    
    def _erfuellt_kriterien(self, angebot: ImmobilienAngebot) -> bool:
        """Prüft, ob ein Angebot die Suchkriterien erfüllt"""
        if angebot.preis > self.config.max_preis:
            return False
        if angebot.zimmer < self.config.min_zimmer or angebot.zimmer > self.config.max_zimmer:
            return False
        return True
    
    def bewerbe_auf_angebot(self, angebot: ImmobilienAngebot) -> bool:
        """Bewirbt sich auf ein Angebot bei Immonet"""
        if not self.driver:
            logging.error("WebDriver nicht verfügbar")
            return False
        
        try:
            # Angebot-Seite öffnen
            self.driver.get(angebot.url)
            self.random_delay(2, 4)
            
            # Kontaktieren-Button finden und klicken
            kontakt_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Kontaktieren')]"))
            )
            kontakt_button.click()
            self.random_delay(1, 2)
            
            # Formular ausfüllen
            return self._fulle_kontaktformular()
            
        except TimeoutException:
            logging.error(f"Timeout beim Laden der Seite: {angebot.url}")
            return False
        except Exception as e:
            logging.error(f"Fehler beim Bewerben auf {angebot.url}: {e}")
            return False
    
    def _fulle_kontaktformular(self) -> bool:
        """Füllt das Kontaktformular aus"""
        try:
            # Anrede auswählen
            if self.config.anrede == "Herr":
                anrede_radio = self.driver.find_element(By.XPATH, "//label[text()='Herr']")
                anrede_radio.click()
            elif self.config.anrede == "Frau":
                anrede_radio = self.driver.find_element(By.XPATH, "//label[text()='Frau']")
                anrede_radio.click()
            
            # Formularfelder ausfüllen
            felder = {
                "Vorname": self.config.vorname,
                "Nachname": self.config.nachname,
                "E-Mail": self.config.email,
                "Telefon": self.config.telefon,
                "Straße / Hausnummer": self.config.strasse,
                "PLZ": self.config.plz,
                "Ort": self.config.ort
            }
            
            for label, wert in felder.items():
                if wert:  # Nur ausfüllen wenn Wert vorhanden
                    try:
                        input_element = self.driver.find_element(
                            By.XPATH, f"//label[text()='{label}']/following-sibling::input"
                        )
                        input_element.clear()
                        input_element.send_keys(wert)
                        self.random_delay(0.5, 1.0)
                    except NoSuchElementException:
                        logging.warning(f"Feld '{label}' nicht gefunden")
            
            # Nachricht hinzufügen
            if self.config.bewerbungstext:
                try:
                    nachricht_textarea = self.driver.find_element(
                        By.XPATH, "//textarea[contains(@placeholder, 'Nachricht')]"
                    )
                    nachricht_textarea.clear()
                    nachricht_textarea.send_keys(self.config.bewerbungstext)
                    self.random_delay(1, 2)
                except NoSuchElementException:
                    logging.warning("Nachricht-Feld nicht gefunden")
            
            # Formular absenden
            submit_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Kontaktanfrage senden')]"
            )
            submit_button.click()
            
            # Warten auf Bestätigung
            self.random_delay(3, 5)
            
            # Erfolg prüfen (vereinfacht)
            # In einer echten Implementierung würde man nach Erfolgs-/Fehlermeldungen suchen
            return True
            
        except Exception as e:
            logging.error(f"Fehler beim Ausfüllen des Kontaktformulars: {e}")
            return False


class ImmobilienScout24Scraper(WebScraperBase):
    """Scraper für ImmobilienScout24.de (mit Bot-Erkennung)"""
    
    BASE_URL = "https://www.immobilienscout24.de"
    
    def suche_neue_angebote(self, stadt: str) -> List[ImmobilienAngebot]:
        """Sucht nach neuen Angeboten auf ImmobilienScout24"""
        # Aufgrund der Bot-Erkennung ist dies komplexer zu implementieren
        # Hier würde man erweiterte Anti-Detection-Techniken benötigen
        
        logging.warning("ImmobilienScout24 hat Bot-Erkennung aktiviert. Implementierung erfordert erweiterte Techniken.")
        return []
    
    def bewerbe_auf_angebot(self, angebot: ImmobilienAngebot) -> bool:
        """Bewirbt sich auf ein Angebot bei ImmobilienScout24"""
        logging.warning("ImmobilienScout24 Bewerbung noch nicht implementiert")
        return False


if __name__ == "__main__":
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
        bewerbungstext="Sehr geehrte Damen und Herren,\n\nhiermit bewerbe ich mich um die ausgeschriebene Wohnung...",
        max_preis=1500.0,
        min_zimmer=2,
        max_zimmer=4,
        suchstaedte=["Berlin"]
    )
    
    print("Immobilien-Bewerbungsbot initialisiert.")
    print("Konfiguration geladen.")
    print("Bereit für automatische Bewerbungen.")

