from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# This allows your website to talk to this API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/weather")
def get_weather(city: str):
    # 1. Get Lat/Lon
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
    if "results" not in geo: return {"error": "Not found"}
    lat, lon = geo["results"][0]["latitude"], geo["results"][0]["longitude"]

    # 2. Get Weather + AQI + UV
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2023-01-01&end_date=2023-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    weather_data = requests.get(url).json()
    
    return {
        "location": geo["results"][0]["name"],
        "daily": weather_data["daily"]
    }