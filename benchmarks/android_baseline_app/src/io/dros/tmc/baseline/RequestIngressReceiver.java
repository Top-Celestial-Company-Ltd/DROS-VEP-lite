package io.dros.tmc.baseline;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Base64;

import org.json.JSONObject;

import java.nio.charset.StandardCharsets;

public final class RequestIngressReceiver extends BroadcastReceiver {
    public static final String ACTION = "io.dros.tmc.baseline.REQUEST_INGRESS";

    @Override
    public void onReceive(Context context, Intent intent) {
        String encoded = intent.getStringExtra("request_b64");
        String raw = encoded == null
                ? "{}"
                : new String(Base64.decode(encoded, Base64.DEFAULT), StandardCharsets.UTF_8);
        try {
            JSONObject request = new JSONObject(raw);
            JSONObject record = new JSONObject();
            record.put("request_id", request.optString("request_id", ""));
            record.put("event", "RECEIVED");
            context.getSharedPreferences("ingress", Context.MODE_PRIVATE)
                    .edit()
                    .putString("last_request_id", request.optString("request_id", ""))
                    .apply();
            IngressFile.append(context, record.toString() + "\n");
            RequestDispatcher.dispatch(context, request);
        } catch (Exception error) {
            JSONObject record = new JSONObject();
            try {
                record.put("request_id", "");
                record.put("event", "MALFORMED");
            } catch (Exception ignored) {
                // JSONObject.put above cannot fail for these primitive values.
            }
            IngressFile.append(context, record.toString() + "\n");
        }
    }
}
