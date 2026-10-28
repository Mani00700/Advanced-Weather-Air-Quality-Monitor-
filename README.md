# Weather App

A command-line Python app that shows the current weather and air quality for any city.
It uses [Open-Meteo](https://open-meteo.com/), which is free and needs no API key.

## Features

- Look up any city by name
- Current temperature, wind speed, and weather condition (with emoji)
- Air quality index (European AQI) and PM2.5, with a simple rating from Good to Very Poor
- Choose Celsius or Fahrenheit with an environment variable
- Saves each city's result to its own file
- Handles bad input, unknown cities, network failures, and missing data without crashing

## Requirements

- Python 3.8 or newer
- The `requests` library

```bash
pip install requests
```

## Usage

```bash
python weather.py
```

Then type a city name when asked.

Example:

```
Enter the name of the city: Berlin
Berlin, Germany: Partly cloudy ⛅, 14.2 °C, wind 11.0 km/h
Air Quality: Good 🟢 (AQI: 18, PM2.5: 6.2 μg/m³)
File Saved!
```

The numbers above are only an example. You will see the live values for your city.

## Changing the temperature unit

The unit is read from the `WEATHER_UNITS` environment variable.
Valid values are `celsius` (the default) and `fahrenheit`.

**Windows (PowerShell):**

```powershell
$env:WEATHER_UNITS="fahrenheit"
python weather.py
```

**macOS / Linux:**

```bash
WEATHER_UNITS=fahrenheit python weather.py
```

The variable only applies to the terminal window where you set it.
Any other value falls back to Celsius.

## Output files

Each city is saved to its own JSON file in the same folder as the script,
named after the city as the API reports it, for example `Berlin's weather.json`.
Looking up the same city again replaces its file with the latest data, and looking up
a different city creates a new file.

Characters that are not allowed in file names (such as `/` or `:`) are removed from the name.

Example contents:

```json
{
  "city": "Berlin",
  "country": "Germany",
  "condition": "Partly cloudy ⛅",
  "temperature": 14.2,
  "windspeed": 11.0,
  "time": "2026-10-28T14:00",
  "aqi": 18,
  "pm25": 6.2,
  "status": "Good 🟢"
}
```

## Air quality ratings

| European AQI | Rating |
|---|---|
| 0 to 20 | Good 🟢 |
| 21 to 40 | Fair 🟡 |
| 41 to 60 | Moderate 🟠 |
| 61 to 80 | Poor 🔴 |
| Above 80 | Very Poor 🟤 |

If a location has no air quality data, the app still shows the weather and skips that line.

## How it works

1. The city name is sent to the Open-Meteo geocoding API, which returns coordinates.
2. The coordinates are used to request the current weather.
3. The same coordinates are used to request air quality (this step is optional).
4. The results are printed and saved to the city's JSON file.

Every request has a timeout and error handling, so a failed connection or an unknown city gives a clear message instead of a crash.

## What I practiced

- Calling web APIs with `requests` (query parameters, timeouts, status codes)
- Reading and writing JSON
- Handling errors with `try/except`
- Reading settings from environment variables
- Splitting a program into small functions that each do one job
