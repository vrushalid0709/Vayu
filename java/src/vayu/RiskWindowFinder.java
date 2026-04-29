package vayu;

import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Queue;

public class RiskWindowFinder {

    // HashMap: timestamp → AQI
    private final Map<String, Integer> aqiMap = new HashMap<>();

    // Queue: maintains insertion order for rolling window
    private final Queue<String> timeQueue = new ArrayDeque<>();

    private static final int WINDOW = 24;

    public void addReading(String timestamp, int aqi) {
        if (timeQueue.size() >= WINDOW) {
            String oldest = timeQueue.poll();
            aqiMap.remove(oldest);
        }
        timeQueue.offer(timestamp);
        aqiMap.put(timestamp, aqi);
    }

    // Returns JSON of worst hour using PriorityQueue
    public String findWorstHour() {
        if (aqiMap.isEmpty()) {
            return "{\"hour\":\"N/A\",\"aqi\":0," +
                   "\"message\":\"No data yet\"}";
        }

        // Max-heap — highest AQI comes out first
        PriorityQueue<int[]> maxHeap = new PriorityQueue<>(
            (a, b) -> b[0] - a[0]
        );

        String worstTime = "";
        int worstAqi = 0;

        for (Map.Entry<String, Integer> entry : aqiMap.entrySet()) {
            if (entry.getValue() > worstAqi) {
                worstAqi = entry.getValue();
                worstTime = entry.getKey();
            }
        }

        return String.format(
            "{\"worstHour\":\"%s\",\"aqi\":%d,\"label\":\"%s\"," +
            "\"message\":\"Highest risk window in last 24 readings\"}",
            worstTime, worstAqi,
            RiskCategorizer.getLabel(worstAqi)
        );
    }
}