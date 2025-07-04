# Website-Analyse für Immobilien-Bewerbungsbot

## ImmobilienScout24 (immobilienscout24.de)

### Herausforderungen:
- **Bot-Erkennung**: Die Website hat eine aktive Bot-Erkennung implementiert ("Ich bin kein Roboter" Seite)
- **Anti-Scraping-Maßnahmen**: Direkter Zugriff auf Suchergebnisse wird blockiert
- **JavaScript-abhängig**: Viele Funktionen erfordern JavaScript-Ausführung

### Struktur:
- Hauptseite mit Suchformular (Ort, Mieten/Kaufen, Immobilientyp)
- Suchergebnisse-Seiten mit Angebotslisten
- Detailseiten für einzelne Immobilien
- Bewerbungsformulare (vermutlich ähnlich wie Immonet)

### Technische Anforderungen:
- User-Agent Rotation erforderlich
- Session-Management
- Möglicherweise CAPTCHA-Umgehung
- Verzögerungen zwischen Anfragen

## Immonet (immonet.de)

### Zugänglichkeit:
- **Weniger restriktiv**: Keine sofortige Bot-Erkennung
- **Funktionsfähiges Scraping**: Suchergebnisse sind zugänglich
- **Klare Struktur**: Gut strukturierte HTML-Elemente

### Website-Struktur:
- **Hauptseite**: https://www.immonet.de
- **Suchfunktion**: Tabs für Kaufen/Mieten/Bewerten
- **Suchergebnisse**: https://www.immonet.de/classified-search?distributionTypes=Rent&estateTypes=House,Apartment&locations=AD08DE8634
- **Angebots-URLs**: https://www.immonet.de/expose/[ID]

### Bewerbungsprozess:
1. **Angebot öffnen**: Klick auf Angebot in Suchergebnissen
2. **Kontakt-Button**: "Kontaktieren" Button auf Detailseite
3. **Formular-Felder**:
   - Anrede (Herr/Frau/Divers)
   - Vorname (Pflichtfeld)
   - Nachname (Pflichtfeld)
   - E-Mail (Pflichtfeld)
   - Telefon (Optional)
   - Straße/Hausnummer (Pflichtfeld)
   - PLZ (Pflichtfeld)
   - Ort (Pflichtfeld)
   - Nachricht (Optional - hier kann der vorgefertigte Text eingefügt werden)
   - Checkbox: "Ich bin Eigentümer einer Immobilie"

### API-Endpunkte (zu identifizieren):
- Suchfunktion: Wahrscheinlich AJAX-basiert
- Formular-Submission: POST-Request an Backend
- Neue Angebote: RSS/JSON Feed möglich

## Technische Implementierungsstrategie

### Web-Scraping-Ansatz:
1. **Selenium WebDriver**: Für JavaScript-schwere Seiten
2. **Requests + BeautifulSoup**: Für einfache HTTP-Anfragen
3. **Proxy-Rotation**: Um IP-Blockierungen zu vermeiden
4. **Rate Limiting**: Verzögerungen zwischen Anfragen

### Datenextraktion:
- **Angebots-IDs**: Eindeutige Identifikation neuer Angebote
- **Angebots-Details**: Preis, Größe, Lage für Filterung
- **Kontakt-URLs**: Direkte Links zu Bewerbungsformularen

### Automatisierung:
- **Formular-Ausfüllung**: Automatisches Befüllen der Kontaktformulare
- **E-Mail-Integration**: SMTP für Benachrichtigungen
- **Datenbank**: SQLite für Tracking bereits beworbener Angebote

## Rechtliche und Ethische Überlegungen

### Wichtige Hinweise:
- **Nutzungsbedingungen**: Beide Websites haben AGB, die automatisierte Zugriffe einschränken können
- **Rate Limiting**: Respektvolle Anfrage-Frequenz erforderlich
- **Datenschutz**: Keine Speicherung persönlicher Daten Dritter
- **Spam-Vermeidung**: Qualitätsvolle, relevante Bewerbungen

### Empfehlungen:
- Implementierung von Verzögerungen (2-5 Sekunden zwischen Anfragen)
- Verwendung realistischer User-Agents
- Respektierung von robots.txt
- Monitoring der eigenen Aktivitäten

