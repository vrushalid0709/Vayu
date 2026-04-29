package vayu;

import java.util.HashMap;

public class ActivityEvaluator {

    // HashMap of activity → intensity multiplier
    private static final HashMap<String, Double> INTENSITY = new HashMap<>();
    static {
        INTENSITY.put("walking",  1.0);
        INTENSITY.put("shopping", 1.0);
        INTENSITY.put("cycling",  1.5);
        INTENSITY.put("jogging",  1.5);
        INTENSITY.put("gym",      1.5);
        INTENSITY.put("running",  2.0);
        INTENSITY.put("football", 2.0);
        INTENSITY.put("cricket",  2.0);
    }

    public static String evaluate(String activity, int duration, int aqi) {
        double multiplier = INTENSITY.getOrDefault(
            activity.toLowerCase(), 1.5
        );
        double durationFactor = 1.0 +
            Math.max(0, (duration - 30) / 30.0) * 0.1;
        double score = aqi * multiplier * durationFactor;

        String recommendation;
        boolean safe;

        if (aqi <= 50) {
            recommendation = "Safe to proceed!";
            safe = true;
        } else if (aqi <= 100) {
            recommendation = "Generally safe. Sensitive groups take care.";
            safe = true;
        } else if (aqi <= 200) {
            if (multiplier >= 2.0) {
                recommendation = "Reduce intensity or limit to 20 mins.";
                safe = false;
            } else {
                recommendation = "Proceed with caution. Take breaks.";
                safe = true;
            }
        } else if (aqi <= 300) {
            recommendation = "Not recommended. Wear N95 if unavoidable.";
            safe = false;
        } else {
            recommendation = "Avoid outdoor activity entirely.";
            safe = false;
        }

        return String.format(
            "{\"activity\":\"%s\",\"duration\":%d,\"aqi\":%d," +
            "\"exposureScore\":%.1f,\"recommendation\":\"%s\",\"safe\":%b}",
            activity, duration, aqi, score, recommendation, safe
        );
    }
}