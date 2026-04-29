package vayu.handlers;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import vayu.DBManager;
import vayu.Main;

public class HistoryHandler implements HttpHandler {
    @Override
    public void handle(HttpExchange ex) throws IOException {
        ex.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        ex.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, OPTIONS");
        ex.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type");
        if ("OPTIONS".equalsIgnoreCase(ex.getRequestMethod())) {
            ex.sendResponseHeaders(204, -1);
            return;
        }

        List<Map<String, Object>> rows = DBManager.getLast24();
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < rows.size(); i++) {
            Map<String, Object> row = rows.get(i);
            sb.append(String.format(
                "{\"station\":\"%s\",\"timestamp\":\"%s\"," +
                "\"aqi\":%d,\"pm25\":%.1f,\"pm10\":%.1f,\"no2\":%.1f}",
                row.get("station"), row.get("timestamp"),
                row.get("aqi"), row.get("pm25"),
                row.get("pm10"), row.get("no2")
            ));
            if (i < rows.size() - 1) sb.append(",");
        }
        sb.append("]");
        Main.sendJson(ex, 200,
            "{\"count\":" + rows.size() + ",\"history\":" + sb + "}"
        );
    }
}