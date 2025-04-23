import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import create_engine

# Get DB URL from env
DB_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/caradvisor_db"
)

# Load data
engine = create_engine(DB_URL)
df = pd.read_sql("SELECT * FROM car_listings", engine)
print(f"[📊] Loaded {len(df)} listings")

# Clean & preprocess
df = df.dropna(subset=["brand", "model", "mileage", "year", "price"])
df["brand"] = df["brand"].str.lower()
df["model"] = df["model"].str.lower()
df["fuel_type"] = df["fuel_type"].str.lower()
df["gearbox"] = df["gearbox"].str.lower()
df["power_kw"] = df["power_kw"].fillna(0)

# Encode categories
brand_encoder = LabelEncoder()
df["brand"] = brand_encoder.fit_transform(df["brand"])

model_encoder = LabelEncoder()
df["model"] = model_encoder.fit_transform(df["model"])

fuel_encoder = LabelEncoder()
df["fuel_type"] = fuel_encoder.fit_transform(df["fuel_type"])

gearbox_encoder = LabelEncoder()
df["gearbox"] = gearbox_encoder.fit_transform(df["gearbox"])

# Train model
X = df[["brand", "model", "year", "mileage", "fuel_type", "gearbox", "power_kw"]]
y = df["price"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor()
model.fit(X_train, y_train)

# Save model & encoders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
joblib.dump(model, os.path.join(BASE_DIR, "car_price_predictor.pkl"))
joblib.dump(brand_encoder, os.path.join(BASE_DIR, "brand_encoder.pkl"))
joblib.dump(model_encoder, os.path.join(BASE_DIR, "model_encoder.pkl"))
joblib.dump(fuel_encoder, os.path.join(BASE_DIR, "fuel_encoder.pkl"))
joblib.dump(gearbox_encoder, os.path.join(BASE_DIR, "gearbox_encoder.pkl"))

print("[✅] Model and encoders saved successfully")
