package vayu;

public class RiskCategorizer {

    public static String getLabel(int aqi) {
        if (aqi <= 50)  return "Good";
        if (aqi <= 100) return "Satisfactory";
        if (aqi <= 200) return "Moderate";
        if (aqi <= 300) return "Poor";
        if (aqi <= 400) return "Very Poor";
        return "Severe";
    }

    public static String getColor(int aqi) {
        if (aqi <= 50)  return "#00b050";
        if (aqi <= 100) return "#92d050";
        if (aqi <= 200) return "#ffff00";
        if (aqi <= 300) return "#ff9900";
        if (aqi <= 400) return "#ff0000";
        return "#7030a0";
    }

    public static boolean needsAlert(int aqi) {
        return aqi > 100;
    }

    public static String getHealthMessage(int aqi) {
        if (aqi <= 50)  return "Air quality is good. Enjoy outdoor activities.";
        if (aqi <= 100) return "Acceptable. Sensitive groups take care.";
        if (aqi <= 200) return "Limit prolonged outdoor exposure.";
        if (aqi <= 300) return "Avoid outdoor activity. Health risk for all.";
        if (aqi <= 400) return "Stay indoors. Serious health effects likely.";
        return "Emergency conditions. Do not go outside.";
    }
}