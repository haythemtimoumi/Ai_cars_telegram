import os
import joblib
import numpy as np

# Load models with absolute paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, "car_price_predictor.pkl"))
brand_encoder = joblib.load(os.path.join(BASE_DIR, "brand_encoder.pkl"))
model_encoder = joblib.load(os.path.join(BASE_DIR, "model_encoder.pkl"))
fuel_encoder = joblib.load(os.path.join(BASE_DIR, "fuel_encoder.pkl"))
gearbox_encoder = joblib.load(os.path.join(BASE_DIR, "gearbox_encoder.pkl"))

def encode_features(car_data):
    car_data["brand"] = brand_encoder.transform([car_data["brand"]])[0]
    car_data["model"] = model_encoder.transform([car_data["model"]])[0]
    car_data["fuel_type"] = fuel_encoder.transform([car_data["fuel_type"]])[0]
    car_data["gearbox"] = gearbox_encoder.transform([car_data["gearbox"]])[0]
    return car_data

def is_good_deal(car_data):
    car_data = encode_features(car_data)
    input_data = np.array([[car_data["brand"], 
                            car_data["model"], 
                            car_data["year"], 
                            car_data["mileage"], 
                            car_data["fuel_type"], 
                            car_data["gearbox"], 
                            car_data["power_kw"]]])
    
    predicted_price = model.predict(input_data)[0]
    
    if car_data["price"] < predicted_price * 0.9:
        return f"✅ Good deal! Estimated market price: {predicted_price:.2f}€"
    else:
        return f"❌ Too expensive. Estimated market price: {predicted_price:.2f}€"
