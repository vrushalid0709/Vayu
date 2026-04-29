from google import genai
import time
from datetime import datetime

GEMINI_API_KEY = ""
client = genai.Client(api_key=GEMINI_API_KEY)

# Seasonal AQI averages for Mumbai
SEASONAL_AQI = {
    1:167.2, 2:154.6, 3:114.1, 4:86.0,
    5:77.3,  6:68.4,  7:67.3,  8:69.2,
    9:72.6,  10:105.3,11:145.1,12:167.6
}

MONTH_NAMES = {
    1:"January",  2:"February", 3:"March",     4:"April",
    5:"May",      6:"June",     7:"July",       8:"August",
    9:"September",10:"October", 11:"November",  12:"December"
}

def get_health_advisory(aqi, label, pm25, pm10, no2, forecast):

    current_month = datetime.now().month
    month_name    = MONTH_NAMES[current_month]
    typical_aqi   = SEASONAL_AQI[current_month]
    is_winter     = current_month in [10, 11, 12, 1, 2]

    if aqi > typical_aqi + 20:
        seasonal_note = f"higher than usual for {month_name}"
    elif aqi < typical_aqi - 20:
        seasonal_note = f"better than usual for {month_name}"
    else:
        seasonal_note = f"typical for {month_name}"

    if is_winter:
        why_reason = (
            "Winter causes higher pollution in Mumbai because "
            "cold air traps pollutants near the ground "
            "(temperature inversion) and there is no rainfall "
            "to wash the air clean."
        )
    else:
        why_reason = (
            "Monsoon and summer months have cleaner air because "
            "rainfall washes pollutants away and warm air helps "
            "pollutants rise and disperse."
        )

    prompt = f"""
You are VAYU, Mumbai's practical air quality advisor.

Current data:
- AQI: {aqi} ({label})
- PM2.5: {pm25} µg/m³
- PM10: {pm10} µg/m³
- NO2: {no2} ppb
- Short-term forecast: {forecast}

Seasonal context:
- Month: {month_name}
- Typical AQI for {month_name} in Mumbai: {typical_aqi}
- Current AQI is {seasonal_note}
- Season explanation: {why_reason}

Write exactly 3 sentences:
1. What this AQI level means for health right now
2. Why AQI is at this level — mention the season naturally
3. One specific action to take

Rules:
- Natural Mumbai tone, not formal
- Mention if air is improving or worsening based on forecast
- No greetings, no emojis
- No generic phrases like "listen to your body"
- Be specific about PM2.5 or NO2 if they are high
Output only the 3 sentences, nothing else.
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model    = "gemini-2.0-flash",
                contents = prompt
            )
            text = response.text.replace("\n", " ").strip()
            return text
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                wait = 2 * (attempt + 1)
                print(f"Gemini busy, retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"Gemini error: {e}")
                return generate_fallback(aqi, label,
                                         month_name, is_winter)

def generate_fallback(aqi, label,
                       month_name="", is_winter=False):
    season_note = (
        "Winter traps pollution near the ground in Mumbai."
        if is_winter else
        "Air tends to be cleaner this time of year."
    )
    if aqi <= 50:
        return (f"Air quality is Good at AQI {aqi}. "
                f"{season_note} "
                f"Great time to be outdoors.")
    elif aqi <= 100:
        return (f"Air quality is satisfactory at AQI {aqi}. "
                f"{season_note} "
                f"Normal activity is fine, sensitive groups take care.")
    elif aqi <= 200:
        return (f"AQI is {aqi} — Moderate. "
                f"{season_note} "
                f"Avoid heavy outdoor workouts, keep windows closed.")
    else:
        return (f"AQI is {aqi} — Poor air quality. "
                f"{season_note} "
                f"Limit outdoor exposure and stay indoors.")

# Test 
if __name__ == "__main__":
    result = get_health_advisory(
        aqi=118, label="Moderate",
        pm25=118.0, pm10=75.0, no2=4.0,
        forecast="+1h: 120, +2h: 115, +3h: 110"
    )
    print("\nAdvisory:\n", result)