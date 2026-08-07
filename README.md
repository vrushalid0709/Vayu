<p align="center">
  <img src="frontend/assets/logo/png/logo-color.png" alt="VAYU Logo" width="180"/>
</p>

# VAYU
### Data-Driven Air Quality Analytics and Forecasting

VAYU is an end-to-end air quality analytics and forecasting system that combines near-real-time pollution data, machine learning, and an interactive dashboard to provide predictive and actionable air quality insights.

The system retrieves AQI and pollutant data from the WAQI API, performs short-term and long-term forecasting, evaluates activity safety, generates threshold-based alerts, and presents the results through a web dashboard.

---

## Features

- Near-real-time AQI and pollutant monitoring using the WAQI API
- 1, 2, and 3-hour AQI forecasting using Random Forest
- 24-hour AQI forecasting using LSTM
- Seasonal air quality trend analysis
- Activity-based safety recommendations
- Threshold-based air quality alerts
- AI-generated health advisories
- Historical AQI data storage and retrieval
- Interactive dashboard for visualization

---

## Machine Learning

### Random Forest

Three Random Forest regression models are used to predict AQI at:

- +1 hour
- +2 hours
- +3 hours

The models were trained on approximately 87,000 hourly Mumbai air quality records using features including current AQI, PM2.5, PM10, NO2, and hour of day.

| Forecast | MAE |
|----------|-----|
| +1 Hour | 1.86 |
| +2 Hours | 3.00 |
| +3 Hours | 4.02 |

### LSTM

An LSTM neural network is used for 24-hour AQI forecasting to capture longer-term temporal and seasonal patterns.

The model uses 24-hour input sequences and produces AQI predictions for the following 24 hours.

**24-hour Forecast MAE:** 10.09 AQI units

---

## System Architecture

VAYU follows a layered architecture:

**Data Source → Python/ML Services → Java Backend → MySQL → Web Dashboard**

### Data Acquisition
The WAQI API provides near-real-time AQI, PM2.5, PM10, and NO2 readings.

### Python & Machine Learning Layer
Python handles data preprocessing, Random Forest and LSTM predictions, seasonal analysis, and AI advisory generation. Flask exposes these services through REST API endpoints.

### Java Backend
The Java backend handles application logic including risk categorization, activity evaluation, alert generation, risk-window identification, database operations, and communication with the Python services.

### Database
MySQL is used to store historical AQI and pollutant readings, with Java JDBC used for database communication.

### Frontend
The dashboard is built using HTML, CSS, JavaScript, and Chart.js to display current AQI, forecasts, pollutant information, seasonal trends, alerts, and health advisories.

---

## Tech Stack

**Machine Learning & Data**
- Python
- Pandas
- NumPy
- Scikit-learn
- TensorFlow / Keras

**Backend**
- Flask
- Java 17
- REST APIs
- JDBC

**Database**
- MySQL

**Frontend**
- HTML
- CSS
- JavaScript
- Chart.js

**APIs & AI**
- WAQI API
- Google Gemini

---

## Project Highlights

- Built an end-to-end ML system rather than a standalone prediction notebook
- Combined real-time API data with historical data for air quality analysis
- Implemented both short-term and 24-hour forecasting models
- Integrated Python ML services with a Java application layer
- Added activity-based risk evaluation and threshold alerts
- Developed an interactive dashboard for presenting predictions and air quality insights

---

## License

This project is currently unlicensed.
