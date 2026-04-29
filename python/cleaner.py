from datetime import datetime

def clean(raw):
    """
    Takes raw dict from fetch_data.py and returns
    a cleaned, normalized dict ready for the model.
    """
    if raw is None:
        return None

    # Parse hour from timestamp
    try:
        hour = datetime.strptime(
            raw["timestamp"], "%Y-%m-%d %H:%M:%S"
        ).hour
    except Exception:
        hour = datetime.now().hour

    def safe_float(val, default=0.0):
        return float(val) if val is not None else default

    return {
        "aqi":       int(raw["aqi"]) if raw.get("aqi") is not None else 0,
        "station":   raw.get("station", "Unknown"),
        "timestamp": raw.get("timestamp", ""),
        "hour":      hour,
        "pm25":      safe_float(raw.get("pm25")),
        "pm10":      safe_float(raw.get("pm10")),
        "no2":       safe_float(raw.get("no2")),
        "co":        safe_float(raw.get("co")),
    }