package vayu;

public class AlertEngine {

    public static String generateAlert(int aqi, double forecastMax) {
        StringBuilder alerts = new StringBuilder("[");
        boolean hasAlert = false;

        if (aqi > 300) {
            alerts.append("{\"level\":\"danger\"," +
                "\"message\":\"AQI " + aqi +
                " — Very Poor. Stay indoors immediately.\"},");
            hasAlert = true;
        } else if (aqi > 200) {
            alerts.append("{\"level\":\"danger\"," +
                "\"message\":\"AQI " + aqi +
                " — Poor. Avoid all outdoor activity.\"},");
            hasAlert = true;
        } else if (aqi > 150) {
            alerts.append("{\"level\":\"warning\"," +
                "\"message\":\"AQI " + aqi +
                " — Moderate risk. Limit outdoor time.\"},");
            hasAlert = true;
        } else if (aqi > 100) {
            alerts.append("{\"level\":\"info\"," +
                "\"message\":\"AQI " + aqi +
                " — Sensitive groups take precautions.\"},");
            hasAlert = true;
        }

        if (forecastMax > aqi + 50) {
            alerts.append("{\"level\":\"warning\"," +
                "\"message\":\"AQI rising to " +
                (int) forecastMax + " in next 3 hours.\"},");
            hasAlert = true;
        }

        if (aqi <= 50 && forecastMax <= 50) {
            alerts.append("{\"level\":\"success\"," +
                "\"message\":\"Great air quality for next 3 hours!\"},");
        }

        // Remove trailing comma
        String result = alerts.toString();
        if (result.endsWith(",")) {
            result = result.substring(0, result.length() - 1);
        }
        result += "]";

        return String.format(
            "{\"currentAqi\":%d,\"forecastMax\":%.1f," +
            "\"hasAlert\":%b,\"alerts\":%s}",
            aqi, forecastMax, hasAlert, result
        );
    }
}