package vayu.handlers;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import vayu.ActivityEvaluator;
import vayu.FlaskClient;
import vayu.Main;

public class ActivityHandler implements HttpHandler {
    @Override
    public void handle(HttpExchange ex) throws IOException {
        ex.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        ex.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, OPTIONS");
        ex.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type");
        if ("OPTIONS".equalsIgnoreCase(ex.getRequestMethod())) {
            ex.sendResponseHeaders(204, -1);
            return;
        }

        String query    = ex.getRequestURI().getQuery();
        Map<String, String> params = parseQuery(query);
        String activity = params.getOrDefault("name", "walking");
        int duration    = Integer.parseInt(
            params.getOrDefault("duration", "30")
        );

        // Get current AQI from Flask
        String currentRaw = FlaskClient.get("/api/current");
        int aqi = 50;
        try {
            int start = currentRaw.indexOf("\"aqi\":") + 6;
            int end   = currentRaw.indexOf(",", start);
            aqi = Integer.parseInt(currentRaw.substring(start, end).trim());
        } catch (NumberFormatException | StringIndexOutOfBoundsException e) {
            System.out.println("AQI parse error: " + e.getMessage());
        }

        String result = ActivityEvaluator.evaluate(activity, duration, aqi);
        Main.sendJson(ex, 200, result);
    }

    private Map<String, String> parseQuery(String query) {
        Map<String, String> map = new HashMap<>();
        if (query == null) return map;
        for (String pair : query.split("&")) {
            String[] kv = pair.split("=");
            if (kv.length == 2) map.put(kv[0], kv[1]);
        }
        return map;
    }
}