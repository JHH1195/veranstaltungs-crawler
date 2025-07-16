from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    date = Column(String)
    location = Column(String)
    maps_url = Column(String)
    category = Column(String, default="Unbekannt")
    source_url = Column(String)
    source_name = Column(String)
    lat = Column(Float)  # 🆕 Latitude
    lon = Column(Float)  # 🆕 Longitude

class Quelle(Base):
    __tablename__ = "quellen"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String, unique=True)
    typ = Column(String)       # z. B. "playwright", "rss", "html"
    stadt = Column(String)     # z. B. "Aachen"
    aktiv = Column(Boolean)    # True = aktiv nutzen
    status = Column(String, default="pending")  # "pending", "success", "error"
    created_at = Column(DateTime, default=datetime.utcnow)

   
# DB-Verbindung (lokal, SQLite-Datei)
engine = create_engine("sqlite:///events.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
