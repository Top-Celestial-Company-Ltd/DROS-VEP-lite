package io.dros.tmc.baseline;

import android.content.Context;

import org.json.JSONObject;

final class RequestDispatcher {
    private RequestDispatcher() {}

    static void dispatch(Context context, JSONObject request) {
        String requestId = request.optString("request_id", "");
        long started = System.nanoTime();
        JSONObject dispatched = new JSONObject();
        JSONObject result = new JSONObject();
        try {
            dispatched.put("request_id", requestId);
            dispatched.put("event", "DISPATCHED");
            IngressFile.append(context, "dispatch_records.jsonl", dispatched.toString() + "\n");

            String action = request.optString("action", "");
            String capability = request.optString("capability", "");
            boolean allowed = "READ_CONTACTS".equals(action) && "CAP_CONTACTS".equals(capability);
            result.put("request_id", requestId);
            result.put("event", "RESULT");
            result.put("decision", allowed ? "ALLOW" : "DENY");
            result.put("execution_started", allowed);
            result.put("execution_completed", allowed);
            result.put("execution_effect", allowed ? "BOUNDED_FIXTURE" : "NONE");
            result.put("decision_latency_ns", System.nanoTime() - started);
            result.put("app_elapsed_ns", System.nanoTime() - started);
            IngressFile.append(context, "result_records.jsonl", result.toString() + "\n");
        } catch (Exception error) {
            JSONObject failure = new JSONObject();
            try {
                failure.put("request_id", requestId);
                failure.put("event", "RESULT");
                failure.put("decision", "ERROR");
                failure.put("decision_latency_ns", System.nanoTime() - started);
                failure.put("app_elapsed_ns", System.nanoTime() - started);
            } catch (Exception ignored) {
                // JSONObject.put above cannot fail for these primitive values.
            }
            IngressFile.append(context, "result_records.jsonl", failure.toString() + "\n");
        }
    }
}
