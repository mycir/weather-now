#!/usr/bin/env python3
"""
Weather Console App
Fetches and displays current weather data using Open-Meteo API.
(Bash script 'weather-now-menu' provides a Zenity driven wrapper.)
"""

import sys
import argparse
import warnings
import requests

from textwrap import dedent

warnings.filterwarnings("ignore")

# Open-Meteo API endpoint
API_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_PARAMS_BASIC = [
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
]

WEATHER_PARAMS = [
    "temperature_2m",
    "dew_point_2m",
    "relative_humidity_2m",
    "precipitation_probability",
    "apparent_temperature",
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "snow_depth",
    "weather_code",
    "pressure_msl",
    "surface_pressure",
    "cloud_cover",
    "cloud_cover_low",
    "cloud_cover_mid",
    "cloud_cover_high",
    "visibility",
    "evapotranspiration",
    "et0_fao_evapotranspiration",
    "vapour_pressure_deficit",
    "wind_speed_10m",
    "wind_speed_80m",
    "wind_speed_120m",
    "wind_speed_180m",
    "wind_direction_10m",
    "wind_direction_80m",
    "wind_direction_120m",
    "wind_direction_180m",
    "wind_gusts_10m",
    "temperature_80m",
    "temperature_120m",
    "temperature_180m",
    "soil_temperature_0cm",
    "soil_temperature_6cm",
    "soil_temperature_18cm",
    "soil_temperature_54cm",
    "soil_moisture_0_to_1cm",
    "soil_moisture_3_to_9cm",
    "soil_moisture_9_to_27cm",
    "soil_moisture_27_to_81cm",
    "uv_index",
    "uv_index_clear_sky",
    "is_day",
    "sunshine_duration",
    "wet_bulb_temperature_2m",
    "total_column_integrated_water_vapour",
    "cape",
    "lifted_index",
    "freezing_level_height",
    "convective_inhibition",
    "boundary_layer_height",
    "temperature_1000hPa",
    "temperature_975hPa",
    "temperature_950hPa",
    "temperature_925hPa",
    "temperature_900hPa",
    "temperature_850hPa",
    "temperature_800hPa",
    "temperature_700hPa",
    "temperature_600hPa",
    "temperature_500hPa",
    "temperature_400hPa",
    "temperature_300hPa",
    "temperature_250hPa",
    "temperature_200hPa",
    "temperature_150hPa",
    "temperature_100hPa",
    "temperature_70hPa",
    "temperature_50hPa",
    "temperature_30hPa",
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "direct_normal_irradiance",
    "global_tilted_irradiance",
    "terrestrial_radiation",
    "shortwave_radiation_instant",
    "direct_radiation_instant",
    "diffuse_radiation_instant",
    "direct_normal_irradiance_instant",
    "global_tilted_irradiance_instant",
    "terrestrial_radiation_instant",
    "lightning_potential",
    "snowfall_height",
]

FRIENDLY_NAMES = {
    "time": "local_time",
    "temperature_2m": "temperature",
    "relative_humidity_2m": "humidity",
    "apparent_temperature": "feels_like",
    "wind_speed_10m": "wind",
    "wind_gusts_10m": "gusts",
    "wind_direction_10m": "direction",
    "weather_code": "conditions",
    "pressure_msl": "pressure",
    "cape": "CAPE",
    "total_column_integrated_water_vapour": "TCWV"
}

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
    if category == "clear" or category == "partly_cloudy" and not is_day:
        suffix = "_night"
    else:
        suffix = ""
    return graphic_type.get(f"{category}{suffix}", graphic_type["cloudy"])


def fetch_weather(latitude, longitude, params_extra, units):
    """Fetch current weather data from Open-Meteo API."""
    params = f"latitude={latitude}&longitude={longitude}" + \
        "&timezone=auto&current=is_day" + \
        "&temperature_unit=" + units["temperature"] + \
        "&wind_speed_unit=" + units["wind"] + \
        "&precipitation_unit=" + units["precipitation"] + "&"

    for param in params_extra:
        params += f"&current={param}"

    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()


def display_weather(location_name, data, wind_in_degrees, output_type):
    """Format and display weather information."""
    current = data["current"]
    units = data["current_units"]
    lat, lon = (data["latitude"], data["longitude"])
    units["time"] = ""
    if not wind_in_degrees:
        current["wind_direction_10m"] = \
            degrees_to_compass(current["wind_direction_10m"])
        units["wind_direction_10m"] = ""
    code = current["weather_code"]
    if output_type == "data-alt":
        current["weather_code"] = \
            f"{code}[{get_weather_description(code)}]"
    else:
        current["weather_code"] = get_weather_description(code)
    units["weather_code"] = ""
    if output_type == "classic":
        header = (
            f"Weather for {location_name}, {lat}, {lon} at {current['time']}"
        )
        del current["time"]
        print(header)
        print("=" * len(header))
        # Display ASCII art
        print(get_weather_graphic(
            WEATHER_ASCII_ART, current["weather_code"], current["is_day"]))
    else:
        symbol = get_weather_graphic(
                    WEATHER_SYMBOLS,
                    current["weather_code"],
                    current["is_day"])
    if units["visibility"] == "ft" and current["visibility"] >= 5280:
        current["visibility"] = round(current["visibility"] / 5280, 2)
        units["visibility"] = "miles"
    elif current["visibility"] >= 1000:
        current["visibility"] = round(current["visibility"] / 1000, 2)
        units["visibility"] = "km"
    del current["interval"]
    del current["is_day"]
    print(f"Coordinates: {lat},{lon}")

    for param in current:
        try:
            label = FRIENDLY_NAMES[param]
        except (KeyError):
            label = param
        value = current[param]
        unit = units[param]
        if value is None:
            value = "n/a"
            unit = ""
        if not label.isupper():
            label = label.replace('_', ' ').capitalize()
        print(f"{label}: {value}{unit}")

    if output_type != "classic":
        print(f"Weather symbol: {symbol}")


def main(placename, country_code, output_type, units, wind_degrees, stdin):
    """Main entry point."""
    try:
        location_name, latitude, longitude = geocode(placename, country_code)
        params = WEATHER_PARAMS_BASIC
        if stdin:
            params += [line.strip() for line in sys.stdin]
        data = fetch_weather(latitude, longitude, params, units)
        display_weather(location_name, data, wind_degrees, output_type)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return 1
    except (KeyError, TypeError) as e:
        print(f"Error parsing weather data: {e}")
        return 1
    except RuntimeError as e:
        print(e)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "weather_now.py",
        usage=("%(prog)s [-l <placename>] [-c <country_code>]"
               f"\n{' ' * 22}[-t [celsius|fahrenheit]] "
               "[-p [mm|inch]] [-w [kmh|ms|mph|kn]]"
               f"\n{' ' * 22}[-d] [-o [classic|data|data-alt]]"
               "\n\n       When - is appended, read additional "
               "weather parameters from standard input."),
        formatter_class=argparse.RawTextHelpFormatter
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
        "-d",
        help="wind direction: show in degrees",
        action='store_true'
    )
    parser.add_argument(
        "-o",
        help=dedent('''\
            output style: classic (heading, ascii art and data),
            data (just data) or data-alt (conditions code and description)'''),
        metavar="",
        required=False,
        choices=["classic", "data", "data-alt"],
        default="classic"
    )
    try:
        args, unknown = parser.parse_known_args()
        stdin = False
        index, index_last = 0, len(unknown) - 1
        for u in unknown:
            if u == '-':
                if index == index_last:
                    del unknown[index]
                    stdin = True
                    break
                else:
                    parser.error("improper use of '-'")
            index += 1
        if unknown:
            parser.error(f"unrecognised argument(s): {' '.join(unknown)}")
    except SystemExit as err:
        parser.usage = argparse.SUPPRESS
        if err.args[0]:
            parser.print_help()
        raise
    args = {
        k: (v.lstrip() if isinstance(v, str) else v)
        for k, v in vars(args).items()
    }

    units = {
        'temperature': args["t"],
        'precipitation': args["p"],
        'wind': args["w"]
    }

    wind_degrees = args["d"]
    args_count = len(sys.argv)
    exit(main(args["l"], args["c"], args["o"], units, wind_degrees, stdin))
