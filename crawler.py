import requests
from bs4 import BeautifulSoup
from models import Session, Quelle, Event
from datetime import datetime
import re
import dateparser

def extract_event_blocks(html):
    """
    Sucht potenzielle Event-Container auf der Seite.
    """
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all(["article", "section", "div"], recursive=True)

def extract_event_data(block, quelle):
    """
    Extrahiert Event-Daten aus einem HTML-Block.
    """
    title_tag = block.find(["h1", "h2", "h3"])
    title = title_tag.get_text(strip=True) if title_tag else None

    description = block.get_text(" ", strip=True)
    date_match = re.search(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b", description)

    parsed_date = None
    if date_match:
        raw_date = date_match.group(0)
        parsed_date = dateparser.parse(raw_date, languages=["de"])

    if not title or not parsed_date:
        return None

    return {
        "title": title,
        "description": description,
        "date": parsed_date.strftime("%Y-%m-%d"),
        "location": quelle.stadt,
        "source_url": quelle.url,
        "source_name": quelle.name
    }

def crawl_pending_quellen():
    session = Session()
    quellen = session.query(Quelle).filter_by(status='pending', aktiv=True).all()
    print(f"🔍 Starte Crawl für {len(quellen)} Quellen...")

    for quelle in quellen:
        try:
            print(f"🌐 Lade: {quelle.url}")
            response = requests.get(quelle.url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            html = response.text

            blocks = extract_event_blocks(html)
            print(f"🔎 {len(blocks)} potenzielle Blöcke auf Seite gefunden")

            events_gespeichert = 0
            übersprungen = 0

            for block in blocks:
                data = extract_event_data(block, quelle)
                if not data:
                    übersprungen += 1
                    continue

                already_exists = session.query(Event).filter_by(source_url=data["source_url"]).first()
                if not already_exists:
                    session.add(Event(**data))
                    events_gespeichert += 1

            quelle.status = "success"
            session.commit()

            if events_gespeichert:
                print(f"✅ {events_gespeichert} Event(s) gespeichert von {quelle.url}")
            else:
                print(f"⚠️ Keine neuen Eventdaten bei {quelle.url}")
            if übersprungen:
                print(f"↪️ {übersprungen} Blöcke übersprungen (unvollständig)")

        except Exception as e:
            print(f"❌ Fehler bei {quelle.url}: {e}")
            quelle.status = "error"

    session.commit()
    session.close()
    print("🏁 Crawl abgeschlossen.")

if __name__ == "__main__":
    crawl_pending_quellen()
