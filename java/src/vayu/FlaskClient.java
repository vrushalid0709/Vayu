package vayu;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class FlaskClient {

    private static final String FLASK = "http://localhost:5000";

    // Generic GET request to Flask
    public static String get(String endpoint) {
        try {
            URL url = new URL(FLASK + endpoint);
            HttpURLConnection con = (HttpURLConnection)
                url.openConnection();
            con.setRequestMethod("GET");
            con.setConnectTimeout(5000);
            con.setReadTimeout(5000);

            BufferedReader br = new BufferedReader(
                new InputStreamReader(con.getInputStream())
            );
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) {
                sb.append(line);
            }
            br.close();
            return sb.toString();

        } catch (Exception e) {
            System.out.println("Flask call failed: " + e.getMessage());
            return "{\"error\":\"Flask unavailable\"}";
        }
    }
}