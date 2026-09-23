package io.dros.tmc.permissionbaseline;

import android.Manifest;
import android.app.Activity;
import android.content.ContentResolver;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.util.Base64;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;

public final class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(new TextView(this));
        String encoded = getIntent().getStringExtra("request_b64");
        String raw = encoded == null ? "{}" : new String(
                Base64.decode(encoded, Base64.DEFAULT), StandardCharsets.UTF_8);
        JSONObject result = evaluate(raw);
        String requestId = result.optString("request_id", "");
        writeFile(resultFileName(requestId), result.toString());
        finish();
    }

    private JSONObject evaluate(String raw) {
        JSONObject result = new JSONObject();
        long started = System.nanoTime();
        try {
            JSONObject request = new JSONObject(raw);
            String requestId = request.optString("request_id", "");
            result.put("request_id", requestId);
            result.put("authority", "ANDROID_PERMISSION_READ_CONTACTS");

            if (checkSelfPermission(Manifest.permission.READ_CONTACTS)
                    != PackageManager.PERMISSION_GRANTED) {
                return finishResult(result, "DENY", false, false, "NONE",
                        "ANDROID_PERMISSION_DENIED", started);
            }

            result.put("decision", "ALLOW");
            result.put("execution_started", true);
            int rows = queryContacts();
            result.put("execution_completed", true);
            result.put("execution_effect", "BOUNDED_PERMISSION_FIXTURE");
            result.put("reason", "ANDROID_PERMISSION_GRANTED");
            result.put("fixture_rows_observed", rows);
            appendEffect(new JSONObject()
                    .put("request_id", requestId)
                    .put("effect", "CONTACTS_PROVIDER_QUERY")
                    .put("rows_observed", rows)
                    .toString() + "\n");
        } catch (Exception error) {
            try {
                result.put("decision", "DENY");
                result.put("execution_started", false);
                result.put("execution_completed", false);
                result.put("execution_effect", "NONE");
                result.put("reason", "BASELINE_EXCEPTION");
            } catch (Exception ignored) {
                // Primitive JSONObject writes above are not expected to fail.
            }
        }
        try {
            result.put("decision_latency_ns", System.nanoTime() - started);
            result.put("app_elapsed_ns", System.nanoTime() - started);
        } catch (Exception ignored) {
            // Diagnostic fields are best effort.
        }
        return result;
    }

    private JSONObject finishResult(JSONObject result, String decision,
                                    boolean executionStarted,
                                    boolean executionCompleted,
                                    String effect, String reason,
                                    long started) throws Exception {
        result.put("decision", decision);
        result.put("execution_started", executionStarted);
        result.put("execution_completed", executionCompleted);
        result.put("execution_effect", effect);
        result.put("reason", reason);
        result.put("decision_latency_ns", System.nanoTime() - started);
        result.put("app_elapsed_ns", System.nanoTime() - started);
        return result;
    }

    private int queryContacts() {
        ContentResolver resolver = getContentResolver();
        Uri uri = Uri.parse("content://com.android.contacts/contacts");
        int rows = 0;
        try (Cursor cursor = resolver.query(uri, new String[]{"_id"}, null, null, null)) {
            if (cursor != null) {
                rows = cursor.getCount();
            }
        }
        return rows;
    }

    private void appendEffect(String content) throws Exception {
        File target = new File(getFilesDir(), "effects.jsonl");
        try (FileOutputStream output = new FileOutputStream(target, true)) {
            output.write(content.getBytes(StandardCharsets.UTF_8));
        }
    }

    private void writeFile(String name, String content) {
        try (FileOutputStream output = new FileOutputStream(new File(getFilesDir(), name))) {
            output.write(content.getBytes(StandardCharsets.UTF_8));
        } catch (Exception error) {
            throw new IllegalStateException("Unable to write result", error);
        }
    }

    private String resultFileName(String requestId) {
        StringBuilder safe = new StringBuilder();
        for (int i = 0; i < requestId.length(); i++) {
            char c = requestId.charAt(i);
            safe.append(Character.isLetterOrDigit(c) || c == '_' || c == '-' ? c : '_');
        }
        return "result_" + safe + ".json";
    }
}
