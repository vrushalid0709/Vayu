import requests  

WAQI_TOKEN = ""
WAQI_URL = "https://api.waqi.info/feed/A568189/"

def fetch_aqi_data():
    """
    Fetch AQI data for Chakala Andheri East from WAQI API.
    Returns a clean dictionary or None if failed.
    """
    try:
        print("Calling API...")
        response = requests.get(
            WAQI_URL,
            params={"token": WAQI_TOKEN},
            timeout=10
        )
        print("API responded")
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "ok":
            print("WAQI returned non-ok status:", data.get("status"))
            return None

        station_data = data.get("data", {})
        iaqi = station_data.get("iaqi", {})

        result = {
            "aqi":       station_data.get("aqi"),
            "station":   station_data.get("city", {}).get("name"),
            "timestamp": station_data.get("time", {}).get("s"),
            "pm25":      iaqi.get("pm25", {}).get("v"),
            "pm10":      iaqi.get("pm10", {}).get("v"),
            "no2":       iaqi.get("no2", {}).get("v"),
            "co":        iaqi.get("co", {}).get("v"),
        }

        return result

    except requests.exceptions.Timeout:
        print("Request timed out,WAQI may be slow")
        return None
    except requests.exceptions.ConnectionError:
        print("No internet connection")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# Test
if __name__ == "__main__":
    data = fetch_aqi_data()
    if data:
        print("Fetch successful!")
        print(data)
    else:
        print("Fetch failed,check token or internet")