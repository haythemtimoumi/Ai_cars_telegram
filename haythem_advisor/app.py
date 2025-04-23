from fastapi import FastAPI
from pydantic import BaseModel
from ml.predictor import is_good_deal

app = FastAPI(title="IA-CARS API", version="1.0")

class CarData(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int
    fuel_type: str
    gearbox: str
    power_kw: int
    price: int

@app.post("/predict")
def predict(car: CarData):
    car_data = car.dict()
    result = is_good_deal(car_data)
    return {"message": result}
