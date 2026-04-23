import os

import requests
from dotenv import load_dotenv

load_dotenv()

# Lấy key từ biến môi trường
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

OPEN_STREET_MAP_URL = "https://nominatim.openstreetmap.org/search"
OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_coordinates(city_name):
    params = {"q": city_name, "format": "json", "limit": 1}

    headers = {"User-Agent": "TDTTHCMUS_Project/1.0"}

    response = requests.get(
        url=OPEN_STREET_MAP_URL,
        params=params,
        headers=headers,
    )
    data = response.json()

    if len(data) > 0:
        data0 = data[0]
        lat = float(data0["lat"])
        lon = float(data0["lon"])
        return lat, lon

    else:
        return None, None


def get_weather(lat, lon):
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}

    response = requests.get(OPEN_WEATHER_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        temp = data["main"]["temp"]
        condition = data["weather"][0]["main"]
        description = data["weather"][0]["description"]

        return temp, condition, description
    else:
        print(f"Lỗi từ OpenWeather: {data}")
        return None, None, None


if __name__ == "__main__":
    city = "Ho Chi Minh"

    lat, lon = get_coordinates(city)
    print(f"Tọa độ của {city}: {lat}, {lon}")

    temp, condition, desc = get_weather(lat, lon)
    print(f"Nhiệt độ: {temp}")
    print(f"Thời tiết: {condition} - {desc}")
