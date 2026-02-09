#!/usr/bin/env python3
"""
Weather Console App
Fetches and displays current weather data using Open-Meteo API.
(Bash script 'weather-now-menu' provides a Zenity driven wrapper.)
"""

import argparse
import warnings
import requests

warnings.filterwarnings("ignore")

# Open-Meteo API endpoint
API_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather Code descriptions
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# ASCII Art representations for weather categories
WEATHER_ASCII_ART = {
    "clear": r"""
     \ | /
    -  O  -
     / | \
    """,
    "clear_night": r"""
       )\
       //
    .-"
    """,
    "partly_cloudy": r"""
     \ | /_
    -  o(  )_
     / (_____)
    """,
    "partly_cloudy_night": r"""
      )\   __
      //  (  )_
    .-"  (_____)
    """,
    "cloudy": r"""
      __
     (  )_
    (_____)
    """,
    "rain": r"""
      __
     (  )_
    (_____)
     \ \ \
    """,
    "snow": r"""
      __
     (  )_
    (_____)
     * * *
    """,
    "thunderstorm": r"""
      __
     (  )_
    (_____)
     /_ /_
      /  /
    """,
    "fog": r"""
     _______
    ( ~ ~ ~ )
    ( ~ ~ ~ )
    ( ~ ~ ~ )
    '-------'
    """
}

# Weather symbols represented by unicode characters
WEATHER_SYMBOLS = {
    "clear": u'\N{black sun with rays}',
    "clear_night": u'\N{crescent moon}',
    "partly_cloudy": u'\N{sun behind cloud}',
    "partly_cloudy_night": u'\N{crescent moon}\N{cloud}',
    "cloudy": u'\N{cloud}',
    "rain": u'\N{cloud with rain}',
    "snow": u'\N{cloud with snow}',
    "thunderstorm": u'\N{thunder cloud and rain}',
    "fog": u'\N{fog}'
}


def geocode(placename, country_code):
    '''Get location coordinates.'''
    params = f"name={placename}&countryCode={country_code}"
    result = requests.get(
        url=f"https://geocoding-api.open-meteo.com/v1/search?{params}")
    location = result.json()
    try:
        name = str(location['results'][0]['name'])
        latitude = str(location['results'][0]['latitude'])
        longitude = str(location['results'][0]['longitude'])
    except KeyError:
        raise RuntimeError(
            "Location not found. Did you forget to supply a valid " +
            "-l <country_code> option?")
    return name, latitude, longitude


def degrees_to_compass(degrees):
    """Convert wind direction in degrees to compass direction."""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]


def get_weather_description(code):
    """Convert weather code to human-readable description."""
    return WEATHER_CODES.get(code, f"Unknown ({code})")


def get_weather_category(code):
    """Map WMO weather code to ASCII art category."""
    if code in (0, 1):
        return "clear"
    elif code == 2:
        return "partly_cloudy"
    elif code == 3:
        return "cloudy"
    elif code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return "rain"
    elif code in (71, 73, 75, 77, 85, 86, 56, 57, 66, 67):
        return "snow"
    elif code in (95, 96, 99):
        return "thunderstorm"
    elif code in (45, 48):
        return "fog"
    else:
        return "cloudy"  # Default to cloudy for unknown codes


def get_weather_graphic(graphic_type, code, is_day):
    """Get character representation for a weather code."""
    category = get_weather_category(code)
    # if (not is_day) and category == "clear" or category == "partly_cloudy":
    if category == "clear" or category == "partly_cloudy" and not is_day:
        suffix = "_night"
    else:
        suffix = ""
    return graphic_type.get(f"{category}{suffix}", graphic_type["cloudy"])


def fetch_weather(latitude, longitude, units):
    """Fetch current weather data from Open-Meteo API."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": units["temperature"],
        "precipitation_unit": units["precipitation"],
        "wind_speed_unit": units["wind"],
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_gusts_10m",
            "wind_direction_10m",
            "weather_code",
            "cloud_cover",
            "precipitation",
            "pressure_msl",
            "visibility",
            "is_day"
        ],
        "timezone": "auto"
    }

    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()


def display_weather(location_name, data, output_type):
    """Format and display weather information."""
    current = data["current"]
    units = data["current_units"]

    latitude = data["latitude"]
    longitude = data["longitude"]
    time = current["time"]
    is_day = current["is_day"]
    temperature = current["temperature_2m"]
    feels_like = current["apparent_temperature"]
    humidity = current["relative_humidity_2m"]
    wind_speed = current["wind_speed_10m"]
    wind_gusts = current["wind_gusts_10m"]
    wind_direction = current["wind_direction_10m"]
    weather_code = current["weather_code"]
    cloud_cover = current["cloud_cover"]
    precipitation = current["precipitation"]
    pressure = current["pressure_msl"]
    visibility_unit = units['visibility']

    if visibility_unit == "ft" and current["visibility"] >= 5280:
        visibility = round(current["visibility"] / 5280, 2)
        visibility_unit = "miles"
    elif current["visibility"] >= 1000:
        visibility = round(current["visibility"] / 1000, 2)
        visibility_unit = "km"
    else:
        visibility = current["visibility"]

    compass = degrees_to_compass(wind_direction)
    conditions = get_weather_description(weather_code)

    if output_type == "classic":
        header = f"Weather for {location_name}, {latitude},{longitude} at {time}"
        print()
        print(header)
        print("=" * len(header))
        # Display ASCII art
        print(get_weather_graphic(WEATHER_ASCII_ART, weather_code, is_day))
    elif output_type == "data":
        # Display unicode characters for weather symbol
        symbol = get_weather_graphic(WEATHER_SYMBOLS, weather_code, is_day)
        print()
        print(f"Location: {location_name}")
        print(f"Coordinates: {latitude},{longitude}")
        print(f"Local time: {time}")
        print(f"Weather code: {weather_code}")
        print(f"Symbol: {symbol}")
    print(f"Temperature: {temperature}{units['temperature_2m']}")
    print(f"Feels like: {feels_like}{units['apparent_temperature']}")
    print(f"Humidity: {humidity}{units['relative_humidity_2m']}")
    print(f"Wind: {wind_speed} {units['wind_speed_10m']}")
    print(f"Gusts: {wind_gusts} {units['wind_gusts_10m']}")
    print(f"Direction: {compass}")
    print(f"Conditions: {conditions}")
    print(f"Cloud cover: {cloud_cover}{units['cloud_cover']}")
    print(f"Precipitation: {precipitation} {units['precipitation']}")
    print(f"Pressure: {pressure} {units['pressure_msl']}")
    print(f"Visibility: {visibility} {visibility_unit}")
    print()


def main(placename, country_code, output_type, units):
    """Main entry point."""
    try:
        location_name, latitude, longitude = geocode(placename, country_code)
        data = fetch_weather(latitude, longitude, units)
        display_weather(location_name, data, output_type)
    except requests.exceptions.RequestException as e:
        print(f"Error geocoding location or fetching weather data: {e}")
        return 1
    except (RuntimeError) as e:
        print(e)
        return 1
    except (KeyError, TypeError) as e:
        print(f"Error parsing weather data: {e}")
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "weather_now.py",
        usage=("%(prog)s [-l <placename>] [-c <country_code>]"
               f"\n{' ' * 22}[-t [celsius|fahrenheit]] "
               "[-p [mm|inch]] [-w [kmh|ms|mph|kn]]"
               f"\n{' ' * 22}[-o [classic|data]]")
    )
    parser.add_argument(
        "-l",
        help="location placename (defaults to London if omitted)",
        metavar="",
        required=False,
        default="london"
    )
    parser.add_argument(
        "-c",
        help="country code (defaults to GB if omitted)",
        metavar="",
        required=False,
        default="GB"
    )
    parser.add_argument(
        "-t",
        help="temperature unit: celsius or fahrenheit",
        metavar="",
        required=False,
        choices=["celsius", "fahrenheit"],
        default="celsius"
    )
    parser.add_argument(
        "-p",
        help="precipitation unit: mm or inch",
        metavar="",
        required=False,
        choices=["mm", "inch"],
        default="mm"
    )
    parser.add_argument(
        "-w",
        help="wind speed unit: kmh, ms, mph or kn",
        metavar="",
        required=False,
        choices=["kmh", "ms", "mph", "kn"],
        default="kmh"
    )
    parser.add_argument(
        "-o",
        help="output style: classic (heading, ascii art and data) \
                or data (just data)",
        metavar="",
        required=False,
        choices=["classic", "data"],
        default="classic"
    )
    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            parser.error(f"unrecognised argument(s): {' '.join(unknown)}")
    except SystemExit as err:
        parser.usage = argparse.SUPPRESS
        if err.args[0]:
            parser.print_help()
        raise
    args = {k: v.lstrip() for k, v in vars(args).items()}
    units = {
        'temperature': args["t"],
        'precipitation': args["p"],
        'wind': args["w"]
    }
    exit(main(args["l"], args["c"], args["o"], units))
