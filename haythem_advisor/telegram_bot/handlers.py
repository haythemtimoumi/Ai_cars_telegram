from telegram import Update
from telegram.ext import ContextTypes
from ml.predictor import is_good_deal, brand_encoder, model_encoder, fuel_encoder, gearbox_encoder
from features.cars.models import CarListing
from core.database import SessionLocal

REQUIRED_FIELDS = ["brand", "model", "year", "mileage", "gearbox", "price"]
ALL_FIELDS = REQUIRED_FIELDS + ["fuel_type", "power_kw"]

FIELD_ORDER = [
    "brand", "model", "year", "mileage", "fuel_type", "gearbox", "power_kw", "price"
]

field_messages = {
    "brand": "Please enter brand:",
    "model": "Please enter model:",
    "year": "Please enter year:",
    "mileage": "Please enter mileage:",
    "fuel_type": "Please enter fuel type:",
    "gearbox": "Please enter gearbox:",
    "power_kw": "Please enter power kw:",
    "price": "Please enter price:"
}

encoder_suggestions = {
    "brand": list(brand_encoder.classes_),
    "model": list(model_encoder.classes_),
    "fuel_type": list(fuel_encoder.classes_),
    "gearbox": list(gearbox_encoder.classes_)
}

user_sessions = {}

def get_next_field(data):
    for field in FIELD_ORDER:
        if field not in data:
            return field
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = {}
    await update.message.reply_text("Welcome to IA-CARS 🧠🚗\nLet's evaluate your car.")
    await update.message.reply_text(field_messages["brand"])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    data = user_sessions[user_id]
    current_field = get_next_field(data)

    if not current_field:
        await update.message.reply_text("✅ All data received. Evaluating...")
        try:
            result = is_good_deal(data)
            await update.message.reply_text(f"📊 Prediction result:\n{result}")

            # Suggest similar cars from DB
            try:
                brand = int(data["brand"])
                model = int(data["model"])
                gearbox = int(data["gearbox"])
                mileage = int(data["mileage"])

                db = SessionLocal()
                query = (
                    db.query(CarListing)
                    .filter(
                        CarListing.brand == brand,
                        CarListing.model == model,
                        CarListing.gearbox == gearbox,
                        CarListing.mileage.between(int(mileage * 0.8), int(mileage * 1.2))
                    )
                    .limit(3)
                    .all()
                )

                if query:
                    await update.message.reply_text("🟡 Similar listings from our database:")
                    for car in query:
                        await update.message.reply_text(
                            f"🔗 {car.brand} {car.model} ({car.year})\n"
                            f"📍 {car.location} - 💰 {car.price} {car.currency}\n"
                            f"{car.url}"
                        )
                else:
                    await update.message.reply_text("ℹ️ No similar listings found.")
            except Exception:
                await update.message.reply_text("⚠️ Failed to fetch similar listings.")
        except Exception:
            await update.message.reply_text("❌ Failed to predict. Check if the values are valid.")
            for field in REQUIRED_FIELDS:
                if field not in encoder_suggestions:
                    continue
                if data.get(field) not in encoder_suggestions[field]:
                    await update.message.reply_text(
                        f"⚠️ Invalid {field}. Please re-enter.\n"
                        f"Suggestions: {', '.join(encoder_suggestions[field][:5])}..."
                    )
                    del data[field]
                    await update.message.reply_text(field_messages[field])
                    return

        user_sessions[user_id] = {}
        return

    # Input parsing
    value = text
    if current_field in ["year", "mileage", "power_kw", "price"]:
        if not value.isdigit():
            await update.message.reply_text(f"❌ {current_field} must be a number. Try again:")
            return
        value = int(value)
    else:
        value = value.lower()

    if current_field in encoder_suggestions:
        known_values = encoder_suggestions[current_field]
        if value not in known_values:
            await update.message.reply_text(
                f"❌ Unknown {current_field}. Did you mean: {', '.join(known_values[:5])}?"
            )
            return

    data[current_field] = value
    next_field = get_next_field(data)

    if next_field:
        await update.message.reply_text(field_messages[next_field])
    else:
        await update.message.reply_text("✅ All data received. Evaluating...")
        try:
            result = is_good_deal(data)
            await update.message.reply_text(f"📊 Prediction result:\n{result}")
        except Exception:
            await update.message.reply_text("❌ Failed to predict. Check if the values are valid.")
        user_sessions[user_id] = {}
