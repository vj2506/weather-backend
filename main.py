import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from supabase import create_client, Client

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 1. Connect to Supabase (We will set these on Render later)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.get("/weather")
def get_weather(city: str):
    city = city.lower().strip()

    # STEP 1: Check Supabase Cache
    cached_data = supabase.table("weather_cache").select("*").eq("city_name", city).execute()
    
    if cached_data.data:
        print(f"--- Serving {city} from CACHE ---")
        return cached_data.data[0]["weather_json"]

    # STEP 2: If not in cache, fetch from Open-Meteo
    print(f"--- Fetching {city} from API ---")
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
    if "results" not in geo: return {"error": "Not found"}
    
    loc = geo["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]
    
    w_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2023-01-01&end_date=2023-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    weather_data = requests.get(w_url).json()
    
    final_payload = {
        "location": loc["name"],
        "daily": weather_data["daily"]
    }

    # STEP 3: Save to Supabase for the next user
    supabase.table("weather_cache").insert({"city_name": city, "weather_json": final_payload}).execute()

    return final_payload