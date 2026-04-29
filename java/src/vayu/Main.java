package vayu;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import vayu.handlers.*;

public class Main {

    public static void main(String[] args) throws IOException {
        DBManager.init();  // fixed — was getConnection()

        HttpServer server = HttpServer.create(
            new InetSocketAddress(8080), 0
        );

        server.createContext("/api/aqi",      new AQIHandler());
        server.createContext("/api/forecast", new ForecastHandler());
        server.createContext("/api/activity", new ActivityHandler());
        server.createContext("/api/alert",    new AlertHandler());
        server.createContext("/api/history",  new HistoryHandler());
        server.createContext("/api/advisory", new AdvisoryHandler());
        server.createContext("/api/forecast/lstm", new LSTMForecastHandler());
        server.createContext("/api/seasonal",      new SeasonalHandler());

        server.setExecutor(null);
        server.start();
        System.out.println("VAYU Java server on http://localhost:8080");
    }

    public static void sendJson(HttpExchange ex, int status, String json)
            throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json");
        ex.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        ex.getResponseHeaders().set("Access-Control-Allow-Methods",
            "GET, POST, OPTIONS");
        ex.getResponseHeaders().set("Access-Control-Allow-Headers",
            "Content-Type");
        ex.sendResponseHeaders(status, bytes.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(bytes);
        }
    }

    public static boolean handlePreflight(HttpExchange ex)
            throws IOException {
        if ("OPTIONS".equalsIgnoreCase(ex.getRequestMethod())) {
            ex.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
            ex.getResponseHeaders().set("Access-Control-Allow-Methods",
                "GET, POST, OPTIONS");
            ex.getResponseHeaders().set("Access-Control-Allow-Headers",
                "Content-Type");
            ex.sendResponseHeaders(204, -1);
            return true;
        }
        return false;
    }
}