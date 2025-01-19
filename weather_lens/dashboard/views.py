from datetime import datetime

import plotly.graph_objects as go
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from pymongo import MongoClient


def get_mongo_client(ip='mongodb://mongo-db:27017') -> MongoClient:
    """Initialize and return a MongoDB client."""
    return MongoClient(ip, username='admin', password='password')


def unix_timestamp_to_moscow_date(timestamp: int) -> str:
    """Convert a Unix timestamp to a human-readable date."""
    moscow_timezone = 3 * 60 * 60  # UTC+3
    return datetime.fromtimestamp(timestamp + moscow_timezone).strftime('%Y-%m-%d %H:%M:%S')


def weather_dashboard(request: HttpRequest) -> HttpResponse:
    """Main dashboard view with graphs"""
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
    openweather_humidity = [entry['main'].get('humidity') for entry in openweather_data]

    # Extract Yandex Weather data
    yandex_temps = [entry['main'].get('temperature') for entry in yandex_weather]
    yandex_visibility = [entry['main'].get('visibility') for entry in yandex_weather]
    yandex_pressure = [entry['main'].get('pressure') for entry in yandex_weather]
    yandex_wind_speed = [entry['wind'].get('speed') for entry in yandex_weather]
    yandex_humidity = [entry['main'].get('humidity') for entry in yandex_weather]

    # Get the latest data for summary
    latest_openweather = openweather_data[-1]
    latest_yandex = yandex_weather[-1]
    latest_summary = {
        'openweather': {
            'temperature': latest_openweather['main']['temperature'],
            'visibility': latest_openweather['visibility'],
            'wind_speed': latest_openweather['wind']['speed'],
            'pressure': latest_openweather['main']['pressure'],
            'humidity': latest_openweather['main']['humidity'],
            'type': latest_openweather['weather']['main'],
        },
        'yandex': {
            'temperature': latest_yandex['main']['temperature'],
            'visibility': latest_yandex['main']['visibility'],
            'wind_speed': latest_yandex['wind']['speed'],
            'pressure': latest_yandex['main']['pressure'],
            'humidity': latest_yandex['main']['humidity'],
            'type': latest_yandex['condition'],
        },
    }

    # Style constants
    LINE_WIDTH = 2.5
    TITLE_FONT_SIZE = 20
    XAXIS_FONT_SIZE = 16
    YAXIS_FONT_SIZE = 16

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
            line=dict(width=LINE_WIDTH),
        )
    )
    temp_fig.add_trace(
        go.Scatter(
            x=yandex_timestamps,
            y=yandex_temps,
            mode='lines+markers',
            name='Yandex Temperature',
            line=dict(width=LINE_WIDTH),
        )
    )
    temp_fig.update_layout(
        title=dict(
            text='Temperature',
            font=dict(size=TITLE_FONT_SIZE),
            xanchor='center',
            x=0.5,
        ),
        xaxis=dict(title=dict(text='Datetime', font=dict(size=XAXIS_FONT_SIZE))),
        yaxis=dict(title=dict(text='Temperature (°C)', font=dict(size=YAXIS_FONT_SIZE))),
        legend=dict(orientation='h', xanchor='center', yanchor='top', x=0.5, y=1.15),
        # margin=dict(t=100),
    )
    graphs.append(temp_fig.to_json())

    # Min/Max Temperature graph
    min_max_fig = go.Figure()
    min_max_fig.add_trace(
        go.Scatter(
            x=openweather_timestamps,
            y=openweather_temp_min,
            mode='lines',
            name='Min Temperature',
            line=dict(width=LINE_WIDTH),
        )
    )
    min_max_fig.add_trace(
        go.Scatter(
            x=openweather_timestamps,
            y=openweather_temp_max,
            mode='lines',
            name='Max Temperature',
            line=dict(width=LINE_WIDTH),
        )
    )
    min_max_fig.update_layout(
        title=dict(
            text='OpenWeather Min/Max Temperature',
            font=dict(size=TITLE_FONT_SIZE),
            xanchor='center',
            x=0.5,
        ),
        xaxis=dict(title=dict(text='Datetime', font=dict(size=XAXIS_FONT_SIZE))),
        yaxis=dict(title=dict(text='Temperature (°C)', font=dict(size=YAXIS_FONT_SIZE))),
        legend=dict(orientation='h', xanchor='center', yanchor='top', x=0.5, y=1.15),
    )
    graphs.append(min_max_fig.to_json())

    # Visibility graph
    visibility_fig = go.Figure()
    visibility_fig.add_trace(
        go.Scatter(
            x=openweather_timestamps,
            y=openweather_visibility,
            mode='lines',
            name='OpenWeather Visibility',
            line=dict(width=LINE_WIDTH),
        )
    )
    visibility_fig.add_trace(
        go.Scatter(
            x=yandex_timestamps,
            y=yandex_visibility,
            mode='lines',
            name='Yandex Visibility',
            line=dict(width=LINE_WIDTH),
        )
    )
    visibility_fig.update_layout(
        title=dict(text='Visibility', font=dict(size=TITLE_FONT_SIZE), xanchor='center', x=0.5),
        xaxis=dict(title=dict(text='Datetime', font=dict(size=XAXIS_FONT_SIZE))),
        yaxis=dict(title=dict(text='Visibility (m)', font=dict(size=YAXIS_FONT_SIZE))),
        legend=dict(orientation='h', xanchor='center', yanchor='top', x=0.5, y=1.15),
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
            line=dict(width=LINE_WIDTH),
        )
    )
    wind_speed_fig.add_trace(
        go.Scatter(
            x=yandex_timestamps,
            y=yandex_wind_speed,
            mode='lines',
            name='Yandex Wind Speed',
            line=dict(width=LINE_WIDTH),
        )
    )
    wind_speed_fig.update_layout(
        title=dict(text='Wind Speed', font=dict(size=TITLE_FONT_SIZE), xanchor='center', x=0.5),
        xaxis=dict(title=dict(text='Datetime', font=dict(size=XAXIS_FONT_SIZE))),
        yaxis=dict(title=dict(text='Speed (m/s)', font=dict(size=YAXIS_FONT_SIZE))),
        legend=dict(orientation='h', xanchor='center', yanchor='top', x=0.5, y=1.15),
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
            line=dict(width=LINE_WIDTH),
        )
    )
    pressure_fig.add_trace(
        go.Scatter(
            x=yandex_timestamps,
            y=yandex_pressure,
            mode='lines+markers',
            name='Yandex Pressure',
            line=dict(width=LINE_WIDTH),
        )
    )
    pressure_fig.update_layout(
        title=dict(text='Pressure', font=dict(size=TITLE_FONT_SIZE), xanchor='center', x=0.5),
        xaxis=dict(title=dict(text='Datetime', font=dict(size=XAXIS_FONT_SIZE))),
        yaxis=dict(title=dict(text='Pressure (hPa)', font=dict(size=YAXIS_FONT_SIZE))),
        legend=dict(orientation='h', xanchor='center', yanchor='top', x=0.5, y=1.15),
    )
    graphs.append(pressure_fig.to_json())

    # Humiidity graph
    humidity_graph = go.Figure()
    humidity_graph.add_trace(
        go.Scatter(
            x=openweather_timestamps,
            y=openweather_humidity,
            mode='lines+markers',
            name='OpenWeather Humidity',
            line=dict(width=LINE_WIDTH),
        )
    )
    humidity_graph.add_trace(
        go.Scatter(
            x=yandex_timestamps,
            y=yandex_humidity,
            mode='lines+markers',
            name='Yandex Humidity',
            line=dict(width=LINE_WIDTH),
        )
    )
    humidity_graph.update_layout(
        title=dict(text='Humidity', font=dict(size=TITLE_FONT_SIZE), xanchor='center', x=0.5),
        xaxis=dict(title=dict(text='Datetime', font=dict(size=XAXIS_FONT_SIZE))),
        yaxis=dict(title=dict(text='Humidity (%)', font=dict(size=YAXIS_FONT_SIZE))),
        legend=dict(orientation='h', xanchor='center', yanchor='top', x=0.5, y=1.15),
    )
    graphs.append(humidity_graph.to_json())

    return render(
        request,
        'weather_dashboard.html',
        {'graphs': graphs, 'latest_summary': latest_summary},
    )
