#!/usr/bin/env python3
"""
E-Mail Manager für den Immobilien-Bewerbungsbot
Erweiterte E-Mail-Funktionalitäten und Benachrichtigungen

Autor: tibo
Datum: 2025-07-03
"""

import smtplib
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import json

from immobilien_bot import ImmobilienAngebot, BewerbungsConfig


class EmailManager:
    """Verwaltet alle E-Mail-Funktionalitäten des Bots"""
    
    def __init__(self, config: BewerbungsConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # E-Mail Templates
        self.templates = {
            'neue_angebote': self._load_template('neue_angebote'),
            'fehler_bericht': self._load_template('fehler_bericht'),
            'tages_zusammenfassung': self._load_template('tages_zusammenfassung'),
            'wochenbericht': self._load_template('wochenbericht')
        }
    
    def _load_template(self, template_name: str) -> str:
        """Lädt ein E-Mail-Template"""
        template_path = f"templates/{template_name}.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._get_default_template(template_name)
    
    def _get_default_template(self, template_name: str) -> str:
        """Gibt Standard-Templates zurück"""
        templates = {
            'neue_angebote': """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .angebot { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .angebot h3 { color: #4CAF50; margin-top: 0; }
        .details { background-color: #f9f9f9; padding: 10px; margin: 10px 0; }
        .footer { background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }
        .stats { background-color: #e7f3ff; padding: 15px; margin: 20px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 Immobilien-Bot Bericht</h1>
        <p>Neue Bewerbungen versendet</p>
    </div>
    
    <div class="content">
        <h2>Hallo {vorname},</h2>
        <p>der Immobilien-Bot hat <strong>{anzahl_angebote}</strong> neue Bewerbungen versendet:</p>
        
        {angebote_liste}
        
        <div class="stats">
            <h3>📊 Statistiken</h3>
            <ul>
                <li>Gefundene Angebote: {gefundene_angebote}</li>
                <li>Neue Angebote: {neue_angebote}</li>
                <li>Erfolgreiche Bewerbungen: {erfolgreiche_bewerbungen}</li>
                <li>Fehlgeschlagene Bewerbungen: {fehlgeschlagene_bewerbungen}</li>
            </ul>
        </div>
        
        <p>Viel Erfolg bei der Wohnungssuche! 🍀</p>
    </div>
    
    <div class="footer">
        <p>Immobilien-Bewerbungsbot | {datum}</p>
    </div>
</body>
</html>
            """,
            
            'fehler_bericht': """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f44336; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .error { background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 10px 0; }
        .footer { background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚠️ Immobilien-Bot Fehler</h1>
        <p>Probleme beim Ausführen</p>
    </div>
    
    <div class="content">
        <h2>Hallo {vorname},</h2>
        <p>beim Ausführen des Immobilien-Bots sind Fehler aufgetreten:</p>
        
        <div class="error">
            <h3>Fehlerdetails:</h3>
            <p><strong>Zeit:</strong> {fehler_zeit}</p>
            <p><strong>Typ:</strong> {fehler_typ}</p>
            <p><strong>Beschreibung:</strong> {fehler_beschreibung}</p>
        </div>
        
        <p>Bitte prüfen Sie die Konfiguration und Logs.</p>
    </div>
    
    <div class="footer">
        <p>Immobilien-Bewerbungsbot | {datum}</p>
    </div>
</body>
</html>
            """,
            
            'tages_zusammenfassung': """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #2196F3; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .summary { background-color: #e3f2fd; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .footer { background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 Tages-Zusammenfassung</h1>
        <p>Immobilien-Bot Aktivitäten</p>
    </div>
    
    <div class="content">
        <h2>Hallo {vorname},</h2>
        <p>hier ist die Zusammenfassung der heutigen Bot-Aktivitäten:</p>
        
        <div class="summary">
            <h3>Heute ({datum}):</h3>
            <ul>
                <li>🔍 Durchläufe: {anzahl_durchlaeufe}</li>
                <li>🏠 Gefundene Angebote: {gefundene_angebote}</li>
                <li>✨ Neue Angebote: {neue_angebote}</li>
                <li>✅ Erfolgreiche Bewerbungen: {erfolgreiche_bewerbungen}</li>
                <li>❌ Fehlgeschlagene Bewerbungen: {fehlgeschlagene_bewerbungen}</li>
            </ul>
        </div>
        
        {top_angebote}
    </div>
    
    <div class="footer">
        <p>Immobilien-Bewerbungsbot | {datum}</p>
    </div>
</body>
</html>
            """
        }
        return templates.get(template_name, "")
    
    def sende_neue_angebote_email(self, angebote: List[ImmobilienAngebot], stats: Dict[str, Any]):
        """Sendet E-Mail über neue Angebote"""
        if not self.config.smtp_username or not angebote:
            return
        
        try:
            # Angebote-Liste für Template erstellen
            angebote_html = ""
            for angebot in angebote:
                angebote_html += f"""
                <div class="angebot">
                    <h3>{angebot.titel}</h3>
                    <div class="details">
                        <p><strong>💰 Preis:</strong> {angebot.preis}€</p>
                        <p><strong>🏠 Zimmer:</strong> {angebot.zimmer}</p>
                        <p><strong>📐 Größe:</strong> {angebot.groesse}m²</p>
                        <p><strong>📍 Ort:</strong> {angebot.ort}</p>
                        <p><strong>🌐 Website:</strong> {angebot.website}</p>
                        <p><strong>🔗 URL:</strong> <a href="{angebot.url}">Angebot ansehen</a></p>
                    </div>
                </div>
                """
            
            # Template füllen
            html_content = self.templates['neue_angebote'].format(
                vorname=self.config.vorname,
                anzahl_angebote=len(angebote),
                angebote_liste=angebote_html,
                gefundene_angebote=stats.get('gefundene_angebote', 0),
                neue_angebote=stats.get('neue_angebote', 0),
                erfolgreiche_bewerbungen=stats.get('erfolgreiche_bewerbungen', 0),
                fehlgeschlagene_bewerbungen=stats.get('fehlgeschlagene_bewerbungen', 0),
                datum=datetime.now().strftime('%d.%m.%Y %H:%M')
            )
            
            # E-Mail senden
            self._sende_email(
                betreff=f"🏠 Immobilien-Bot: {len(angebote)} neue Bewerbungen",
                html_content=html_content
            )
            
            self.logger.info(f"E-Mail über {len(angebote)} neue Angebote gesendet")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Senden der Neue-Angebote-E-Mail: {e}")
    
    def sende_fehler_email(self, fehler_typ: str, fehler_beschreibung: str):
        """Sendet E-Mail bei Fehlern"""
        if not self.config.smtp_username:
            return
        
        try:
            html_content = self.templates['fehler_bericht'].format(
                vorname=self.config.vorname,
                fehler_zeit=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                fehler_typ=fehler_typ,
                fehler_beschreibung=fehler_beschreibung,
                datum=datetime.now().strftime('%d.%m.%Y %H:%M')
            )
            
            self._sende_email(
                betreff=f"⚠️ Immobilien-Bot Fehler: {fehler_typ}",
                html_content=html_content
            )
            
            self.logger.info("Fehler-E-Mail gesendet")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Senden der Fehler-E-Mail: {e}")
    
    def sende_tages_zusammenfassung(self, stats: Dict[str, Any], top_angebote: List[ImmobilienAngebot] = None):
        """Sendet tägliche Zusammenfassung"""
        if not self.config.smtp_username:
            return
        
        try:
            # Top-Angebote HTML erstellen
            top_angebote_html = ""
            if top_angebote:
                top_angebote_html = "<h3>🏆 Top-Angebote des Tages:</h3>"
                for angebot in top_angebote[:3]:  # Nur die ersten 3
                    top_angebote_html += f"""
                    <div class="angebot">
                        <h4>{angebot.titel}</h4>
                        <p>{angebot.preis}€ | {angebot.zimmer} Zimmer | {angebot.groesse}m² | {angebot.ort}</p>
                    </div>
                    """
            
            html_content = self.templates['tages_zusammenfassung'].format(
                vorname=self.config.vorname,
                datum=datetime.now().strftime('%d.%m.%Y'),
                anzahl_durchlaeufe=stats.get('anzahl_durchlaeufe', 0),
                gefundene_angebote=stats.get('gefundene_angebote', 0),
                neue_angebote=stats.get('neue_angebote', 0),
                erfolgreiche_bewerbungen=stats.get('erfolgreiche_bewerbungen', 0),
                fehlgeschlagene_bewerbungen=stats.get('fehlgeschlagene_bewerbungen', 0),
                top_angebote=top_angebote_html
            )
            
            self._sende_email(
                betreff=f"📈 Immobilien-Bot Tages-Zusammenfassung {datetime.now().strftime('%d.%m.%Y')}",
                html_content=html_content
            )
            
            self.logger.info("Tages-Zusammenfassung E-Mail gesendet")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Senden der Tages-Zusammenfassung: {e}")
    
    def _sende_email(self, betreff: str, html_content: str, anhang_pfad: Optional[str] = None):
        """Sendet eine E-Mail"""
        try:
            from email.mime.text import MimeText
            from email.mime.multipart import MimeMultipart
            from email.mime.base import MimeBase
            from email import encoders
            
            # E-Mail erstellen
            msg = MimeMultipart('alternative')
            msg['From'] = self.config.smtp_username
            msg['To'] = self.config.email
            msg['Subject'] = betreff
            
            # HTML-Inhalt hinzufügen
            html_part = MimeText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Anhang hinzufügen (falls vorhanden)
            if anhang_pfad and os.path.exists(anhang_pfad):
                with open(anhang_pfad, "rb") as attachment:
                    part = MimeBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(anhang_pfad)}'
                )
                msg.attach(part)
            
            # E-Mail senden
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.smtp_username, self.config.smtp_password)
            text = msg.as_string()
            server.sendmail(self.config.smtp_username, self.config.email, text)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Fehler beim Senden der E-Mail '{betreff}': {e}")
            raise


class NotificationManager:
    """Verwaltet verschiedene Benachrichtigungskanäle"""
    
    def __init__(self, config: BewerbungsConfig):
        self.config = config
        self.email_manager = EmailManager(config)
        self.logger = logging.getLogger(__name__)
        
        # Benachrichtigungseinstellungen
        self.einstellungen = {
            'email_bei_neuen_angeboten': True,
            'email_bei_fehlern': True,
            'tages_zusammenfassung': True,
            'wochen_zusammenfassung': True,
            'min_angebote_fuer_email': 1,
            'max_emails_pro_tag': 10
        }
        
        # Zähler für E-Mails pro Tag
        self.email_zaehler = {}
    
    def benachrichtige_neue_angebote(self, angebote: List[ImmobilienAngebot], stats: Dict[str, Any]):
        """Benachrichtigt über neue Angebote"""
        if not self.einstellungen['email_bei_neuen_angeboten']:
            return
        
        if len(angebote) < self.einstellungen['min_angebote_fuer_email']:
            return
        
        if self._email_limit_erreicht():
            self.logger.warning("Tägliches E-Mail-Limit erreicht")
            return
        
        self.email_manager.sende_neue_angebote_email(angebote, stats)
        self._email_zaehler_erhoehen()
    
    def benachrichtige_fehler(self, fehler_typ: str, fehler_beschreibung: str):
        """Benachrichtigt über Fehler"""
        if not self.einstellungen['email_bei_fehlern']:
            return
        
        if self._email_limit_erreicht():
            self.logger.warning("Tägliches E-Mail-Limit erreicht - Fehler-E-Mail nicht gesendet")
            return
        
        self.email_manager.sende_fehler_email(fehler_typ, fehler_beschreibung)
        self._email_zaehler_erhoehen()
    
    def sende_tages_zusammenfassung(self, stats: Dict[str, Any], top_angebote: List[ImmobilienAngebot] = None):
        """Sendet tägliche Zusammenfassung"""
        if not self.einstellungen['tages_zusammenfassung']:
            return
        
        self.email_manager.sende_tages_zusammenfassung(stats, top_angebote)
    
    def _email_limit_erreicht(self) -> bool:
        """Prüft, ob das tägliche E-Mail-Limit erreicht wurde"""
        heute = datetime.now().strftime('%Y-%m-%d')
        return self.email_zaehler.get(heute, 0) >= self.einstellungen['max_emails_pro_tag']
    
    def _email_zaehler_erhoehen(self):
        """Erhöht den E-Mail-Zähler für heute"""
        heute = datetime.now().strftime('%Y-%m-%d')
        self.email_zaehler[heute] = self.email_zaehler.get(heute, 0) + 1
    
    def aktualisiere_einstellungen(self, neue_einstellungen: Dict[str, Any]):
        """Aktualisiert die Benachrichtigungseinstellungen"""
        self.einstellungen.update(neue_einstellungen)
        self.logger.info("Benachrichtigungseinstellungen aktualisiert")


if __name__ == "__main__":
    # Test der E-Mail-Funktionalität
    from immobilien_bot import BewerbungsConfig, ImmobilienAngebot
    
    config = BewerbungsConfig(
        vorname="Max",
        email="test@example.com",
        smtp_username="",  # Hier echte E-Mail eintragen
        smtp_password=""   # Hier App-Passwort eintragen
    )
    
    # Test-Angebot erstellen
    test_angebot = ImmobilienAngebot(
        id="test123",
        titel="Schöne 3-Zimmer-Wohnung",
        preis=1200.0,
        groesse=75.0,
        zimmer=3,
        ort="Berlin",
        url="https://example.com/angebot/test123",
        anbieter="Test Makler",
        erstellt=datetime.now(),
        website="immonet"
    )
    
    # E-Mail Manager testen
    email_manager = EmailManager(config)
    
    print("E-Mail Manager erfolgreich initialisiert!")
    print("Bereit für E-Mail-Benachrichtigungen.")

