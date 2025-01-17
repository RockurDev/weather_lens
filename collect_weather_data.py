import os
import time

import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_mongo_client(ip='mongodb://localhost:27017') -> MongoClient:
    """
    Initialize and return a MongoDB client.
    """
    return MongoClient(ip, username='admin', password='password')


def save_to_mongo(database: str, collection: str, data, ip='mongodb://localhost:27017') -> None:
    """
    Save data to a MongoDB collection.
    """
    client = get_mongo_client(ip)
    db = client[database]
    col = db[collection]
    if isinstance(data, list):
        col.insert_many(data)
    else:
        col.insert_one(data)
    print(f'Data saved to MongoDB collection "{collection}".')


def format_yandex_weather_data(data: dict) -> dict:
    """
    Format Yandex Weather API response to a standardized structure.
    """
    data = data['data']
    weather_data = data['weatherByPoint']['now']
    return {
        'timestamp': data['serverTimestamp'],
        'coordinates': data['weatherByPoint']['location'],
        'main': {
            'temperature': weather_data['temperature'],
            'humidity': weather_data['humidity'],
            'pressure': weather_data['pressure'],
            'cloudiness': weather_data['cloudiness'],
            'visibility': weather_data['visibility'],
        },
        'wind': {
            'speed': weather_data['windSpeed'],
            'direction': weather_data['windDirection'],
        },
        'precipitation': {
            'type': weather_data['precType'],
            'strength': weather_data['precStrength'],
        },
        'condition': weather_data['condition'],
    }


def format_openweather_data(data: dict) -> dict:
    """
    Format OpenWeather API response to a standardized structure.
    """
    return {
        'location': data['name'],
        'timestamp': data['dt'],
        'coordinates': data['coord'],
        'main': {
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'temperature_min': data['main']['temp_min'],
            'temperature_max': data['main']['temp_max'],
            'pressure': data['main']['pressure'],
            'humidity': data['main']['humidity'],
            'sea_level': data['main'].get('sea_level'),
            'ground_level': data['main'].get('grnd_level'),
        },
        'visibility': data.get('visibility', None),
        'wind': {
            'speed': data['wind']['speed'],
            'direction': data['wind']['deg'],
            'gust': data['wind'].get('gust'),
        },
        'clouds': data['clouds']['all'],
        'sun': {'sunrise': data['sys']['sunrise'], 'sunset': data['sys']['sunset']},
        'weather': {
            'main': data['weather'][0]['main'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
        },
    }


def fetch_yandex_weather(access_key: str, query: str) -> dict:
    """
    Fetch weather data from Yandex Weather API.
    """
    headers = {'X-Yandex-Weather-Key': access_key, 'Content-Type': 'application/json'}
    endpoint = 'https://api.weather.yandex.ru/graphql/query'
    response = requests.post(endpoint, headers=headers, json={'query': query})
    response.raise_for_status()
    return format_yandex_weather_data(response.json())


def fetch_openweather(params: dict, token: str) -> dict:
    """
    Fetch weather data from OpenWeather API.
    """
    endpoint = 'https://api.openweathermap.org/data/2.5/weather'
    params.update({'appid': token})
    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    return format_openweather_data(response.json())


def main() -> None:
    """
    Main function to fetch and store weather data from APIs.
    """
    UPDATE_TIME = 60 * 60  # 1 hour

    # MongoDB configuration
    mongo_ip = 'mongodb://localhost:27017'
    database = 'weather_data'
    yandex_collection = 'yandex_weather'
    openweather_collection = 'openweather_weather'

    # Yandex Weather API configuration
    token_yandex = os.getenv('YANDEX_TOKEN', '')
    query_yandex = """{
      serverTimestamp
      weatherByPoint(request: { lat: 43.6028, lon: 39.7342 }) {
        location {
            lat
            lon
        }
        now {
          cloudiness
          humidity
          precType
          precStrength
          pressure: pressure(unit: PASCAL)
          temperature
          windSpeed
          windDirection
          visibility
          condition
        }
      }
    }"""

    # OpenWeather API configuration
    token_openweather = os.getenv('OPENWEATHER_TOKEN', '')
    query_openweather = {
        'q': 'Sochi,ru',
        'units': 'metric',
        'lang': 'ru',
    }

    while True:
        # Fetch data from Yandex Weather API
        try:
            yandex_data = fetch_yandex_weather(token_yandex, query_yandex)
            save_to_mongo(database, yandex_collection, yandex_data, mongo_ip)
        except Exception as e:
            print(f'Error fetching or saving Yandex Weather data: {e}')

        # Fetch data from OpenWeather API
        try:
            openweather_data = fetch_openweather(query_openweather, token_openweather)
            save_to_mongo(database, openweather_collection, openweather_data, mongo_ip)
        except Exception as e:
            print(f'Error fetching or saving OpenWeather data: {e}')

        print(f'Weather data updated at {time.ctime()}. Sleeping...')

        time.sleep(UPDATE_TIME)  # Wait for the next update


if __name__ == '__main__':
    main()
