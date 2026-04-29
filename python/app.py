from flask import Flask, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import threading
import time
import json
from datetime import datetime
from tensorflow.keras.models import load_model
import joblib
from collections import deque

from fetch_data import fetch_aqi_data
from cleaner import clean
from gemini_advisor import get_health_advisory


app = Flask(__name__)
CORS(app)

# Load all 3 models 
print("Loading models...")
model_1h = joblib.load("model_1h.pkl")
model_2h = joblib.load("model_2h.pkl")
model_3h = joblib.load("model_3h.pkl")
print("Loading LSTM model...")
lstm_model          = load_model("lstm_model.h5")
lstm_feature_scaler = joblib.load("lstm_feature_scaler.pkl")
lstm_target_scaler  = joblib.load("lstm_target_scaler.pkl")
print("LSTM loaded!")
print("All models loaded!")


latest = {}
lstm_buffer = deque(maxlen=24)

# Save reading to aqi 
def save_to_jsonl(data):
    try:
        with open("data/aqi_data.jsonl", "a") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        print(f"Save error: {e}")

# Background fetcher 
def background_fetch():
    global latest
    while True:
        try:
            raw     = fetch_aqi_data()
            cleaned = clean(raw)
            if cleaned:
                latest = cleaned
                lstm_buffer.append(cleaned)
                save_to_jsonl(cleaned)   # appending
                print(f"[{datetime.now().strftime('%H:%M')}] "
                      f"AQI: {cleaned['aqi']} "
                      f"PM2.5: {cleaned['pm25']} "
                      f"PM10: {cleaned['pm10']} "
                      f"NO2: {cleaned['no2']}")
        except Exception as e:
            print(f"Fetch error: {e}")
        time.sleep(900)  # 15 minutes

# Start background thread
thread = threading.Thread(target=background_fetch, daemon=True)
thread.start()

# build feature array for model 
def build_features(data):
    return np.array([[
        data.get("pm25",  0.0),
        data.get("pm10",  0.0),
        data.get("no2",   0.0),
        data.get("hour",  datetime.now().hour),
        data.get("aqi",   0.0),
    ]])

# AQI category label 
def aqi_label(aqi):
    if aqi <= 50:   return "Good"
    if aqi <= 100:  return "Satisfactory"
    if aqi <= 200:  return "Moderate"
    if aqi <= 300:  return "Poor"
    if aqi <= 400:  return "Very Poor"
    return "Severe"

# AQI color for frontend 
def aqi_color(aqi):
    if aqi <= 50:   return "#00b050"
    if aqi <= 100:  return "#92d050"
    if aqi <= 200:  return "#ffff00"
    if aqi <= 300:  return "#ff9900"
    if aqi <= 400:  return "#ff0000"
    return "#7030a0"

# ENDPOINTS

# /api/current
@app.route("/api/current")
def current():
    if not latest:
        return jsonify({"error": "No data yet, please wait"}), 503

    aqi = latest.get("aqi", 0)
    return jsonify({
        "aqi":       aqi,
        "label":     aqi_label(aqi),
        "color":     aqi_color(aqi),
        "pm25":      latest.get("pm25"),
        "pm10":      latest.get("pm10"),
        "no2":       latest.get("no2"),
        "station":   latest.get("station"),
        "timestamp": latest.get("timestamp"),
        "hour":      latest.get("hour"),
    })

# /api/forecast 
@app.route("/api/forecast")
def forecast():
    if not latest:
        return jsonify({"error": "No data yet, please wait"}), 503

    features     = build_features(latest)
    current_hour = latest.get("hour", datetime.now().hour)
    current_aqi  = latest.get("aqi", 0)

    pred_1h = round(float(model_1h.predict(features)[0]), 1)
    pred_2h = round(float(model_2h.predict(features)[0]), 1)
    pred_3h = round(float(model_3h.predict(features)[0]), 1)

    forecast_list = [
        {
            "hour":  f"{(current_hour + 1) % 24:02d}:00",
            "aqi":   pred_1h,
            "label": aqi_label(pred_1h),
            "color": aqi_color(pred_1h),
            "tag":   "+1h"
        },
        {
            "hour":  f"{(current_hour + 2) % 24:02d}:00",
            "aqi":   pred_2h,
            "label": aqi_label(pred_2h),
            "color": aqi_color(pred_2h),
            "tag":   "+2h"
        },
        {
            "hour":  f"{(current_hour + 3) % 24:02d}:00",
            "aqi":   pred_3h,
            "label": aqi_label(pred_3h),
            "color": aqi_color(pred_3h),
            "tag":   "+3h"
        },
    ]

    worst = max(forecast_list, key=lambda x: x["aqi"])

    return jsonify({
        "current_aqi":  current_aqi,
        "current_label": aqi_label(current_aqi),
        "forecast":     forecast_list,
        "worst_hour":   worst,
    })

# /api/history 
@app.route("/api/history")
def history():
    readings = []
    try:
        with open("aqi_data.jsonl", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    readings.append(json.loads(line))
    except FileNotFoundError:
        return jsonify({"error": "No history yet"}), 404

    # Return last 24 readings
    last24 = readings[-24:]

    return jsonify({
        "count":    len(last24),
        "history":  last24,
    })

#/api/activity
@app.route("/api/activity/<activity>/<int:duration>")
def activity(activity, duration):
    if not latest:
        return jsonify({"error": "No data yet"}), 503

    aqi      = latest.get("aqi", 0)
    features = build_features(latest)
    pred_1h  = round(float(model_1h.predict(features)[0]), 1)

    # Use whichever is higher current or predicted next hour
    effective_aqi = max(aqi, pred_1h)

    intensity_map = {
        "walking":  1.0,
        "shopping": 1.0,
        "cycling":  1.5,
        "jogging":  1.5,
        "gym":      1.5,
        "running":  2.0,
        "football": 2.0,
        "cricket":  2.0,
    }
    multiplier      = intensity_map.get(activity.lower(), 1.5)
    duration_factor = 1.0 + max(0, (duration - 30) / 30.0) * 0.1
    exposure_score  = round(effective_aqi * multiplier * duration_factor, 1)

    if effective_aqi <= 50:
        recommendation = "Safe to proceed. Enjoy your activity!"
        safe = True
    elif effective_aqi <= 100:
        recommendation = "Generally safe. Sensitive individuals take care."
        safe = True
    elif effective_aqi <= 200:
        if multiplier >= 2.0:
            recommendation = "Reduce intensity or limit to under 20 mins."
            safe = False
        else:
            recommendation = "Proceed with caution. Take breaks if uncomfortable."
            safe = True
    elif effective_aqi <= 300:
        recommendation = "Not recommended. Wear N95 mask if unavoidable."
        safe = False
    else:
        recommendation = "Avoid outdoor activity entirely. Stay indoors."
        safe = False

    return jsonify({
        "activity":        activity,
        "duration_mins":   duration,
        "current_aqi":     aqi,
        "predicted_aqi":   pred_1h,
        "effective_aqi":   effective_aqi,
        "exposure_score":  exposure_score,
        "recommendation":  recommendation,
        "safe":            safe,
        "label":           aqi_label(effective_aqi),
        "color":           aqi_color(effective_aqi),
    })

#/api/alert 
@app.route("/api/alert")
def alert():
    if not latest:
        return jsonify({"error": "No data yet"}), 503

    aqi      = latest.get("aqi", 0)
    features = build_features(latest)

    pred_1h  = round(float(model_1h.predict(features)[0]), 1)
    pred_2h  = round(float(model_2h.predict(features)[0]), 1)
    pred_3h  = round(float(model_3h.predict(features)[0]), 1)
    max_pred = max(pred_1h, pred_2h, pred_3h)

    alerts = []

    # Current AQI alerts
    if aqi > 300:
        alerts.append({
            "level":   "danger",
            "message": f"AQI is {aqi} — Very Poor. Stay indoors immediately."
        })
    elif aqi > 200:
        alerts.append({
            "level":   "danger",
            "message": f"AQI is {aqi} — Poor air quality. Avoid all outdoor activity."
        })
    elif aqi > 150:
        alerts.append({
            "level":   "warning",
            "message": f"AQI is {aqi} — Moderate risk. Limit outdoor time."
        })
    elif aqi > 100:
        alerts.append({
            "level":   "info",
            "message": f"AQI is {aqi} — Sensitive groups should take precautions."
        })

    # Rising trend alert
    if max_pred > aqi + 50:
        alerts.append({
            "level":   "warning",
            "message": f"AQI expected to rise to {round(max_pred)} "
                       f"in the next 3 hours. Plan accordingly."
        })

    # Good air quality positive message
    if aqi <= 50 and max_pred <= 50:
        alerts.append({
            "level":   "success",
            "message": "Air quality is good for the next 3 hours. Great time to go out!"
        })

    return jsonify({
        "current_aqi":  aqi,
        "current_label": aqi_label(aqi),
        "forecast_max": round(max_pred, 1),
        "alerts":       alerts,
        "has_alert":    any(a["level"] in ["warning", "danger"] for a in alerts),
    })

# /api/forecast/lstm — 24 hour LSTM prediction 
@app.route("/api/forecast/lstm")
def forecast_lstm():
    if len(lstm_buffer) < 24:
        return jsonify({
            "error": f"Need 24 readings, have {len(lstm_buffer)}",
            "tip":   "Keep app running — fills up over time"
        }), 503

    # Build feature matrix from last 24 readings
    rows = []
    for r in lstm_buffer:
        month       = int(r["timestamp"][5:7]) if r.get("timestamp") else 1
        is_winter   = 1 if month in [10,11,12,1,2] else 0
        rows.append([
            r.get("pm25",       0.0),
            r.get("pm10",       0.0),
            r.get("no2",        0.0),
            r.get("hour",       0),
            month,
            0,           
            is_winter,
            r.get("aqi",        0.0),   
        ])

    seq           = np.array(rows)
    seq_scaled    = lstm_feature_scaler.transform(seq)
    seq_input     = seq_scaled.reshape(1, 24, 8)

    pred_scaled   = lstm_model.predict(seq_input, verbose=0)
    pred_real     = lstm_target_scaler.inverse_transform(
                        pred_scaled.reshape(-1,1)
                    ).flatten()

    current_hour  = latest.get("hour", datetime.now().hour)
    forecast_24h  = []
    for i, aqi_val in enumerate(pred_real):
        hour_label = f"{(current_hour + i + 1) % 24:02d}:00"
        aqi_val    = max(0, round(float(aqi_val), 1))
        forecast_24h.append({
            "hour":  hour_label,
            "aqi":   aqi_val,
            "label": aqi_label(aqi_val),
            "color": aqi_color(aqi_val),
        })

    worst = max(forecast_24h, key=lambda x: x["aqi"])

    return jsonify({
        "type":        "lstm_24h",
        "current_aqi": latest.get("aqi"),
        "forecast":    forecast_24h,
        "worst_hour":  worst,
        "mae":         10.09
    })

# ── /api/seasonal — monthly AQI averages ─────────────────────
@app.route("/api/seasonal")
def seasonal():
    seasonal_data = [
        {"month": "Jan", "aqi": 167.2, "season": "Winter"},
        {"month": "Feb", "aqi": 154.6, "season": "Winter"},
        {"month": "Mar", "aqi": 114.1, "season": "Spring"},
        {"month": "Apr", "aqi": 86.0,  "season": "Spring"},
        {"month": "May", "aqi": 77.3,  "season": "Summer"},
        {"month": "Jun", "aqi": 68.4,  "season": "Monsoon"},
        {"month": "Jul", "aqi": 67.3,  "season": "Monsoon"},
        {"month": "Aug", "aqi": 69.2,  "season": "Monsoon"},
        {"month": "Sep", "aqi": 72.6,  "season": "Post-Monsoon"},
        {"month": "Oct", "aqi": 105.3, "season": "Post-Monsoon"},
        {"month": "Nov", "aqi": 145.1, "season": "Winter"},
        {"month": "Dec", "aqi": 167.6, "season": "Winter"},
    ]

    current_month = datetime.now().month
    current_data  = next(
        (d for i,d in enumerate(seasonal_data) if i+1 == current_month),
        None
    )

    return jsonify({
        "seasonal":      seasonal_data,
        "current_month": current_data,
        "insight":       "Winter months (Dec-Feb) show 2.5x higher AQI than monsoon season due to temperature inversion and absence of rainfall"
    })

@app.route("/api/advisory")
def advisory():
    if not latest:
        return jsonify({"error": "No data yet"}), 503

    features = build_features(latest)
    pred_1h  = round(float(model_1h.predict(features)[0]), 1)
    pred_2h  = round(float(model_2h.predict(features)[0]), 1)
    pred_3h  = round(float(model_3h.predict(features)[0]), 1)

    forecast_summary = f"+1h: {pred_1h}, +2h: {pred_2h}, +3h: {pred_3h}"

    advice = get_health_advisory(
        aqi      = latest.get("aqi"),
        label    = aqi_label(latest.get("aqi", 0)),
        pm25     = latest.get("pm25"),
        pm10     = latest.get("pm10"),
        no2      = latest.get("no2"),
        forecast = forecast_summary
    )

    # Also return seasonal context for frontend
    from datetime import datetime
    current_month = datetime.now().month
    typical_aqi   = {
        1:167.2, 2:154.6, 3:114.1, 4:86.0,
        5:77.3,  6:68.4,  7:67.3,  8:69.2,
        9:72.6,  10:105.3,11:145.1,12:167.6
    }[current_month]

    month_names = {
        1:"January",  2:"February", 3:"March",    4:"April",
        5:"May",      6:"June",     7:"July",      8:"August",
        9:"September",10:"October",11:"November", 12:"December"
    }

    return jsonify({
        "aqi":             latest.get("aqi"),
        "label":           aqi_label(latest.get("aqi", 0)),
        "advisory":        advice,
        "month":           month_names[current_month],
        "typical_aqi":     typical_aqi,
        "is_winter":       current_month in [10, 11, 12, 1, 2],
        "seasonal_insight": f"Avg AQI in {month_names[current_month]}: {typical_aqi}"
    })
# main function
if __name__ == "__main__":
    app.run(port=5000, debug=False)
