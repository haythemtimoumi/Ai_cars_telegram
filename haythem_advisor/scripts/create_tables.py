import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import engine
from features.cars.models import Base

if __name__ == "__main__":
    print("[⚙️] Creating tables in caradvisor_db...")
    Base.metadata.create_all(bind=engine)
    print("[✅] Tables created successfully.")
