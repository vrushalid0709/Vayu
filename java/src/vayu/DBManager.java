package vayu;

import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DBManager {

    private static final String URL  =
        "jdbc:mysql://localhost:3306/vayudb";
    private static final String USER = "root";
    private static final String PASS = "vrushali"; 
    private static Connection conn;

    public static void init() {
        try {
            conn = DriverManager.getConnection(URL, USER, PASS);
            System.out.println("MySQL connected!");
        } catch (SQLException e) {
            System.out.println("DB connection failed: " + e.getMessage());
        }
    }

    // Insert a new AQI reading
    public static void insert(String station, String timestamp,
                               int aqi, double pm25,
                               double pm10, double no2, int hour) {
        String sql = "INSERT INTO aqi_readings " +
                     "(station, timestamp, aqi, pm25, pm10, no2, hour_of_day) " +
                     "VALUES (?, ?, ?, ?, ?, ?, ?)";
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, station);
            ps.setString(2, timestamp);
            ps.setInt(3, aqi);
            ps.setDouble(4, pm25);
            ps.setDouble(5, pm10);
            ps.setDouble(6, no2);
            ps.setInt(7, hour);
            ps.executeUpdate();
        } catch (SQLException e) {
            System.out.println("Insert failed: " + e.getMessage());
        }
    }

    // Get last 24 readings for history
    public static List<Map<String, Object>> getLast24() {
        List<Map<String, Object>> list = new ArrayList<>();
        String sql = "SELECT * FROM aqi_readings " +
                     "ORDER BY id DESC LIMIT 24";
        try (Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery(sql)) {
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                row.put("station",   rs.getString("station"));
                row.put("timestamp", rs.getString("timestamp"));
                row.put("aqi",       rs.getInt("aqi"));
                row.put("pm25",      rs.getDouble("pm25"));
                row.put("pm10",      rs.getDouble("pm10"));
                row.put("no2",       rs.getDouble("no2"));
                row.put("hour",      rs.getInt("hour_of_day"));
                list.add(row);
            }
        } catch (SQLException e) {
            System.out.println("Query failed: " + e.getMessage());
        }
        return list;
    }
}