package vayu.handlers;
import com.sun.net.httpserver.*;
import vayu.*;
import java.io.IOException;

public class SeasonalHandler implements HttpHandler {
    @Override
    public void handle(HttpExchange ex) throws IOException {
        ex.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        ex.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, OPTIONS");
        ex.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type");
        if ("OPTIONS".equalsIgnoreCase(ex.getRequestMethod())) {
            ex.sendResponseHeaders(204, -1); return;
        }
        Main.sendJson(ex, 200, FlaskClient.get("/api/seasonal"));
    }
}