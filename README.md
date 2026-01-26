<p align="center">
  <img src="frontend/assets/logo/png/logo-color.png" alt="VAYU Logo" width="180"/>
</p>

**Data-Driven Air Quality Analytics and Forecasting Dashboard**

VAYU is a mini-project focused on short-term air quality forecasting and early-warning alerts using historical AQI data. The system integrates machine learning predictions with a Java-based backend and a lightweight web dashboard for visualization.

The project emphasizes clean system architecture, separation of concerns, and practical feasibility as a solo academic project.

---

## Overview

Air quality information is often presented reactively, after pollution levels have already crossed unhealthy thresholds. VAYU explores a proactive approach by analyzing historical AQI data and presenting near-term insights through a simple, interactive dashboard.

The goal is to make air quality trends easier to interpret and act upon, without overwhelming users with technical complexity.

---

## Architecture (High-Level)

- **Prediction Layer**  
  Machine learning models trained on historical air quality data and exposed via a lightweight API.

- **Backend Layer**  
  Central application logic responsible for data handling, threshold evaluation, and aggregation of results.

- **Frontend Layer**  
  A single-page dashboard built with HTML, CSS, and JavaScript to visualize trends, predictions, and alerts.

Each layer is designed to remain loosely coupled to allow independent development and iteration.

---

## Repository Structure
frontend/ # Web dashboard (HTML, CSS, JavaScript)

## Current Status

This repository is under active development.  
Core structure and frontend setup are in place, with backend integration and prediction services being developed incrementally.

---

## License

This project is currently unlicensed.