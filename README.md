# Weather Data Monitoring and Analysis Project

## Project Description
This project provides a comprehensive solution for collecting, storing, and analyzing weather data using reliable sources like OpenWeatherMap and Yandex Weather APIs. It enables real-time weather monitoring and supports advanced analysis capabilities. The system is containerized using Docker for easy deployment and ensures data persistence through local storage volumes.

---

## Features and Capabilities

1. **Data Collection**
   - Retrieves weather data every hour from OpenWeatherMap and Yandex Weather APIs.
   - Supports configurable update intervals (default: 1 hour) through the `UPDATE_TIME` parameter.

2. **Data Storage**
   - Data is stored in MongoDB using dedicated collections for each API source.
   - Persistent storage enabled via Docker volumes to ensure data retention across container restarts.

3. **Data Standardization**
   - API responses are normalized into a unified format for ease of analysis.

4. **Dashboard Interface**
   - User-friendly dashboard accessible at [http://localhost:8000](http://localhost:8000) for real-time data visualization.

5. **Administrative Tools**
   - Mongo Express available at [http://localhost:8081](http://localhost:8081) for managing and querying the database.

---

## Technologies Used
- **Docker Compose**: Simplifies deployment and service orchestration.
- **MongoDB**: High-performance NoSQL database for data storage.
- **Mongo Express**: Web-based interface for MongoDB.
- **Python**: Core programming language for API integration and data processing.
- **Requests**: Handles API interactions.
- **Django**: Framework for building the dashboard and backend services.
- **Plotly**: Library for creating interactive and visually appealing charts and graphs.

---

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) installed on your machine.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/RockurDev/weather_lens
   cd weather_lens
   ```

2. Build and run the project:
   ```bash
   docker-compose up --build
   ```

### Accessing Services
- **Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Mongo Express**: [http://localhost:8081](http://localhost:8081)
- **MongoDB**: Runs on `localhost:27017`

---

## Configuration
### Environment Variables
Environment variables are configured directly in the `.env.example` file, which contains detailed instructions for proper setup.

### Modifying Update Interval
To change the data collection frequency, adjust the `UPDATE_TIME` value in the `weather_collect_data.py` script:
```python
UPDATE_TIME = <desired-interval-in-seconds>
```
**Note**: Be mindful of API rate limits and restrictions.

---

## Data Structure
### MongoDB Collections
- **Yandex Weather Data**:
  - Fields: `timestamp`, `coordinates`, `main`, `wind`, `precipitation`, `condition`
- **OpenWeather Data**:
  - Fields: `timestamp`, `location`, `coordinates`, `main`, `visibility`, `wind`, `clouds`, `sun`, `weather`

---

## Contributors
- [RockurDev](https://github.com/RockurDev)
- [NilsCoy](https://github.com/NilsCoy)

