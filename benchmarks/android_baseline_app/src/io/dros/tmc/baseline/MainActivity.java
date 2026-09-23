package io.dros.tmc.baseline;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.util.Base64;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

public final class MainActivity extends Activity {
    private static final String REQUEST_EXTRA = "request_json";

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(new TextView(this));

        String revokePrincipal = getIntent().getStringExtra("revoke_principal");
        if (revokePrincipal != null) {
            writeFile("revoked_principal.txt", revokePrincipal);
            finish();
            return;
        }

        String encodedRequest = getIntent().getStringExtra("request_b64");
        String rawRequest = encodedRequest == null
                ? getIntent().getStringExtra(REQUEST_EXTRA)
                : new String(Base64.decode(encodedRequest, Base64.DEFAULT), StandardCharsets.UTF_8);
        JSONObject result = evaluate(rawRequest);
        String requestId = result.optString("request_id", "");
        writeFile(resultFileName(requestId), result.toString());
        finish();
    }

    private JSONObject evaluate(String rawRequest) {
        long started = System.nanoTime();
        JSONObject result = new JSONObject();
        try {
            JSONObject request = new JSONObject(rawRequest == null ? "{}" : rawRequest);
            String requestId = request.optString("request_id", "");
            String action = request.optString("action", "");
            String capability = request.optString("capability", "");
            String principal = request.optString("principal", "");
            String required = "READ_CONTACTS".equals(action) ? "CAP_CONTACTS" : "";
            boolean revoked = principal.equals(readFile("revoked_principal.txt"));
            boolean allowed = !revoked && !required.isEmpty() && required.equals(capability);

            result.put("request_id", requestId);
            result.put("policy_hash", request.optString("policy_version", ""));
            result.put("decision", allowed ? "ALLOW" : "DENY");
            result.put("execution_started", allowed);
            result.put("execution_completed", allowed);
            result.put("execution_effect", allowed ? "BOUNDED_FIXTURE" : "NONE");
            result.put("reason", allowed ? "CAPABILITY_AUTHORIZED" : (revoked ? "AUTHORITY_REVOKED" : "CAPABILITY_MISSING"));
            result.put("decision_latency_ns", System.nanoTime() - started);
            result.put("app_elapsed_ns", System.nanoTime() - started);

            if (allowed) {
                writeFile("effects.jsonl", new JSONObject()
                        .put("request_id", requestId)
                        .put("effect", "BOUNDED_FIXTURE")
                        .toString() + "\n");
            }
        } catch (Exception error) {
            try {
                result.put("request_id", "");
                result.put("policy_hash", "");
                result.put("decision", "DENY");
                result.put("execution_started", false);
                result.put("execution_completed", false);
                result.put("execution_effect", "NONE");
                result.put("reason", "MALFORMED_REQUEST");
                result.put("decision_latency_ns", System.nanoTime() - started);
                result.put("app_elapsed_ns", System.nanoTime() - started);
            } catch (Exception ignored) {
                // JSONObject.put above cannot fail for these primitive values.
            }
        }
        return result;
    }

    private String resultFileName(String requestId) {
        StringBuilder safe = new StringBuilder();
        for (int index = 0; index < requestId.length(); index++) {
            char character = requestId.charAt(index);
            if ((character >= 'A' && character <= 'Z')
                    || (character >= 'a' && character <= 'z')
                    || (character >= '0' && character <= '9')
                    || character == '_' || character == '-') {
                safe.append(character);
            } else {
                safe.append('_');
            }
        }
        return "result_" + safe + ".json";
    }

    private void writeFile(String name, String content) {
        File target = new File(getFilesDir(), name);
        try (FileOutputStream output = new FileOutputStream(target, "effects.jsonl".equals(name))) {
            output.write(content.getBytes(StandardCharsets.UTF_8));
        } catch (Exception error) {
            throw new IllegalStateException("Unable to write " + name, error);
        }
    }

    private String readFile(String name) {
        File source = new File(getFilesDir(), name);
        if (!source.exists()) {
            return "";
        }
        try (FileInputStream input = new FileInputStream(source);
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[256];
            int count;
            while ((count = input.read(buffer)) != -1) {
                output.write(buffer, 0, count);
            }
            return output.toString(StandardCharsets.UTF_8.name());
        } catch (Exception error) {
            return "";
        }
    }
}
