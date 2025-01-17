from datetime import datetime

import plotly.graph_objects as go
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from pymongo import MongoClient


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def about(request: HttpRequest) -> HttpResponse:
    return render(request, 'about.html')


def get_mongo_client(ip='mongodb://mongo-db:27017') -> MongoClient:
    """Initialize and return a MongoDB client."""
    return MongoClient(ip, username='admin', password='password')


def unix_timestamp_to_moscow_date(timestamp: int) -> str:
    """Convert a Unix timestamp to a human-readable date."""
    moscow_timezone = 3 * 60 * 60  # UTC+3
    return datetime.fromtimestamp(timestamp + moscow_timezone).strftime('%Y-%m-%d %H:%M:%S')


def weather_dashboard(request: HttpRequest) -> HttpResponse:
    # Connect to MongoDB
    client = get_mongo_client()
    db = client['weather_data']

    # Fetch data
    openweather_data = list(db['openweather_weather'].find().sort('timestamp', 1))
    yandex_weather = list(db['yandex_weather'].find().sort('timestamp', 1))

    # Handle empty datasets
    if not openweather_data or not yandex_weather:
        return render(request, 'weather_dashboard.html', {'error': 'No weather data available.'})

    # Prepare data for plotting
    openweather_timestamps = [
        unix_timestamp_to_moscow_date(int(entry.get('timestamp', 0))) for entry in openweather_data
    ]
    yandex_timestamps = [
        unix_timestamp_to_moscow_date(int(entry.get('timestamp', 0))) for entry in yandex_weather
    ]

    # Extract OpenWeather data
    openweather_temps = [entry['main'].get('temperature') for entry in openweather_data]
    openweather_temp_min = [entry['main'].get('temperature_min') for entry in openweather_data]
    openweather_temp_max = [entry['main'].get('temperature_max') for entry in openweather_data]
    openweather_visibility = [entry.get('visibility') for entry in openweather_data]
    openweather_wind_speed = [entry['wind'].get('speed') for entry in openweather_data]
    openweather_pressure = [entry['main'].get('pressure') for entry in openweather_data]

    # Extract Yandex Weather data
    yandex_temps = [entry['main'].get('temperature') for entry in yandex_weather]
    yandex_visibility = [entry['main'].get('visibility') for entry in yandex_weather]
    yandex_pressure = [entry['main'].get('pressure') for entry in yandex_weather]
    yandex_wind_speed = [entry['wind'].get('speed') for entry in yandex_weather]

    # Get the latest data for summary
    latest_openweather = openweather_data[-1]
    latest_yandex = yandex_weather[-1]
    latest_summary = {
        'openweather': {
            'temperature': latest_openweather['main']['temperature'],
            'visibility': latest_openweather['visibility'],
            'wind_speed': latest_openweather['wind']['speed'],
            'pressure': latest_openweather['main']['pressure'],
        },
        'yandex': {
            'temperature': latest_yandex['main']['temperature'],
            'visibility': latest_yandex['main']['visibility'],
            'wind_speed': latest_yandex['wind']['speed'],
            'pressure': latest_yandex['main']['pressure'],
        },
    }

    # Create separate graphs
    graphs = []

    # Temperature graph
    temp_fig = go.Figure()
    temp_fig.add_trace(
        go.Scatter(
            x=openweather_timestamps,
            y=openweather_temps,
            mode='lines+markers',
            name='OpenWeather Temperature',
        )
    )
    temp_fig.add_trace(
        go.Scatter(
            x=yandex_timestamps,
            y=yandex_temps,
            mode='lines+markers',
            name='Yandex Temperature',
        )
    )
    graphs.append(temp_fig.to_json())

    # Min/Max Temperature graph
    min_max_fig = go.Figure()
    min_max_fig.add_trace(
        go.Scatter(
            x=openweather_timestamps,
            y=openweather_temp_min,
            mode='lines',
            name='OpenWeather Min Temperature',
        )
    )
    min_max_fig.add_trace(
        go.Scatter(
            x=openweather_timestamps,
            y=openweather_temp_max,
            mode='lines',
            name='OpenWeather Max Temperature',
        )
    )
    graphs.append(min_max_fig.to_json())

    # Visibility graph
    visibility_fig = go.Figure()
    visibility_fig.add_trace(
        go.Bar(
            x=openweather_timestamps,
            y=openweather_visibility,
            name='OpenWeather Visibility',
        )
    )
    visibility_fig.add_trace(
        go.Bar(
            x=yandex_timestamps,
            y=yandex_visibility,
            name='Yandex Visibility',
        )
    )
    graphs.append(visibility_fig.to_json())

    # Wind Speed graph
    wind_speed_fig = go.Figure()
    wind_speed_fig.add_trace(
        go.Scatter(
            x=openweather_timestamps,
            y=openweather_wind_speed,
            mode='lines',
            name='OpenWeather Wind Speed',
        )
    )
    wind_speed_fig.add_trace(
        go.Scatter(
            x=yandex_timestamps,
            y=yandex_wind_speed,
            mode='lines',
            name='Yandex Wind Speed',
        )
    )
    graphs.append(wind_speed_fig.to_json())

    # Pressure graph
    pressure_fig = go.Figure()
    pressure_fig.add_trace(
        go.Scatter(
            x=openweather_timestamps,
            y=openweather_pressure,
            mode='lines+markers',
            name='OpenWeather Pressure',
        )
    )
    pressure_fig.add_trace(
        go.Scatter(
            x=yandex_timestamps,
            y=yandex_pressure,
            mode='lines+markers',
            name='Yandex Pressure',
        )
    )
    graphs.append(pressure_fig.to_json())

    return render(
        request,
        'weather_dashboard.html',
        {'graphs': graphs, 'latest_summary': latest_summary},
    )
