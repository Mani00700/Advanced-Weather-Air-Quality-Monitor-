# Weather App
# Asks for a city, then shows the current weather and air quality there.
# The result is saved to a file named after the city, for example "Berlin's weather.json".
# Data comes from Open-Meteo (free, no API key needed).

import requests
import json
import os

# Maps the weather codes the API returns (WMO codes) to readable text.
# Codes that are not in this table are shown as "Unknown".
weather_conditions = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Rime fog 🌫️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️",
    55: "Dense drizzle 🌦️",
    56: "Light freezing drizzle 🧊",
    57: "Dense freezing drizzle 🧊",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    66: "Light freezing rain 🧊",
    67: "Heavy freezing rain 🧊",
    71: "Slight snow ❄️",
    73: "Moderate snow ❄️",
    75: "Heavy snow ❄️",
    77: "Snow grains ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Violent rain showers 🌧️",
    85: "Slight snow showers 🌨️",
    86: "Heavy snow showers 🌨️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
}

def get_coordinates(city):
    # Turns a city name into coordinates using the geocoding API.
    # Returns (name, country, latitude, longitude),
    # or None if the city isn't found or the request fails.
    try:
        # params builds the URL for us (?name=...&count=1) and handles
        # special characters. timeout stops the program from waiting forever.
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10,
        )
        # Turns error status codes (404, 500, ...) into exceptions
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        # Catches every kind of request problem: no internet, timeout, bad status
        print(f"Request failed: {e}")
        return None

    # The city data is inside a "results" list. If the city doesn't exist,
    # the key is missing or the list is empty.
    results = data.get("results")
    if not results:
        print(f"Couldn't find a city called '{city}'.")
        return None

    # count=1 means we only asked for one match, so we take the first item
    place = results[0]
    return place["name"], place["country"], place["latitude"], place["longitude"]

def get_weather(latitude,longitude,unit):
    # Gets the current weather for a pair of coordinates.
    # unit is "celsius" or "fahrenheit".
    # Returns (temperature, windspeed, time, condition), or None on failure.
    try:
        api = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&temperature_unit={unit}"
        response = requests.get(api,timeout = 10)
        response.raise_for_status()
        # The values we need are inside the "current_weather" part of the reply
        data = response.json()["current_weather"]

        # Look up the weather code in our table, or use "Unknown" if it's missing
        code = data.get("weathercode")
        condition = weather_conditions.get(code, "Unknown")

        return data["temperature"],data["windspeed"],data["time"],condition
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def get_air_quality(latitude, longitude):
    # Gets the current air quality for a pair of coordinates.
    # Returns (aqi, pm25, status), or None on failure.
    # This is an extra feature, so the program still works if it fails.
    try:

        api = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={latitude}&longitude={longitude}&current=european_aqi,pm2_5"
        response = requests.get(api,timeout = 10)
        response.raise_for_status()
        data = response.json()["current"]
        
        # .get() returns None instead of crashing if a value is missing
        aqi = data.get("european_aqi")
        pm25 = data.get("pm2_5")

        # Turn the European Air Quality Index number into a label.
        # Some places have no data, so check for None first
        # (comparing None with a number would crash).
        if aqi is None:
            status = "No data"
        elif aqi <= 20:
            status = "Good 🟢"
        elif aqi <= 40:
            status = "Fair 🟡"
        elif aqi <= 60:
            status = "Moderate 🟠"
        elif aqi <= 80:
            status = "Poor 🔴"
        else:
            status = "Very Poor 🟤"
            
        return aqi, pm25, status
    except requests.exceptions.RequestException as e:
        print(f"Air Quality request failed: {e}")
        return None

def save_weather(name,country,temp,wind,time,condition,aqi,pm25,status):
    # Saves the results to a file named after the city, in the same folder
    # as this script. Building the path from __file__ means it works from any folder.
    base = os.path.dirname(os.path.abspath(__file__))

    # Remove characters that aren't allowed in file names
    # (for example the "/" in "Biel/Bienne"), so saving can't fail because of them.
    # The backslashes are doubled because "\" has a special meaning in Python strings.
    safe_name = "".join(c for c in name if c not in '\\/:*?"<>|')
    path = os.path.join(base, f"{safe_name}'s weather.json")

    # indent=2 makes the file readable, ensure_ascii=False keeps special
    # characters (like emojis) instead of turning them into \u codes.
    # Mode "w" replaces the file if it already exists, so checking the same
    # city again updates its file.
    with open(path,"w", encoding="utf-8") as f:
        json.dump({"city":name,"country":country,"condition":condition,"temperature":temp,"windspeed":wind,"time":time,"aqi":aqi,"pm25":pm25,"status":status},f,indent=2,ensure_ascii=False)
    print("File Saved!")

def main():
    # Ask for a city and stop if the input is empty
    city = input("Enter the name of the city: ").strip()
    if not city:
        print("Please enter a city name.")
        return

    # Read the unit from the WEATHER_UNITS environment variable.
    # It defaults to celsius, and any other value falls back to celsius too.
    unit = os.environ.get("WEATHER_UNITS", "celsius").lower()
    if unit not in ("celsius","fahrenheit"):
        unit = "celsius"
    symbol = "°F" if unit == "fahrenheit" else "°C"

    # Step 1: city name -> coordinates. Stop if it failed.
    place = get_coordinates(city)
    if place is None:
        return
    name,country,lat,lon = place

    # Step 2: coordinates -> weather. Stop if it failed.
    current = get_weather(lat,lon,unit)
    if current is None:
        return
    temp,wind,time,condition = current

    # Step 3: coordinates -> air quality. This part is optional:
    # if it fails, we continue with "No data" instead of stopping.
    quality = get_air_quality(lat,lon)
    if quality is None:
        aqi,pm25,status = None,None,"No data"
    else:
        aqi,pm25,status = quality

    # Show the results, then save them to a file
    print(f"{name}, {country}: {condition} , {temp} {symbol}, wind {wind} km/h")
    if aqi is not None:
        print(f"Air Quality: {status} (AQI: {aqi}, PM2.5: {pm25} μg/m³)")
    save_weather(name,country,temp,wind,time,condition,aqi,pm25,status)


# Runs main() only when this file is run directly,
# not when it is imported by another script.
if __name__ == "__main__":
    main()
