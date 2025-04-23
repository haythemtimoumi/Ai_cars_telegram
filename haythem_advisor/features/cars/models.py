from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CarListing(Base):
    __tablename__ = "car_listings"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String, unique=True, index=True)
    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Integer)
    fuel_type = Column(String)
    gearbox = Column(String)
    power_kw = Column(Integer)
    price = Column(Integer)
    currency = Column(String)
    location = Column(JSON)
    source = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    url = Column(String)
