package io.dros.tmc.binderclient;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.os.Parcel;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;

public final class MainActivity extends Activity {
    private String requestId;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(new TextView(this));
        requestId = getIntent().getStringExtra("request_id");
        try {
            Intent intent = new Intent();
            intent.setComponent(new ComponentName(
                    "io.dros.tmc.binderfixture",
                    "io.dros.tmc.binderfixture.BoundedFixtureService"));
            if (!bindService(intent, connection, BIND_AUTO_CREATE)) {
                writeResult("DENY", false, false, "NONE", "BINDER_BIND_RETURNED_FALSE");
                finish();
            }
        } catch (SecurityException denied) {
            writeResult("DENY", false, false, "NONE", "BINDER_SERVICE_PERMISSION_DENIED");
            finish();
        }
    }

    private final ServiceConnection connection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            Parcel data = Parcel.obtain();
            Parcel reply = Parcel.obtain();
            try {
                data.writeString(requestId == null ? "" : requestId);
                service.transact(1, data, reply, 0);
                reply.readException();
                reply.readString();
                writeResult("ALLOW", true, true, "BOUNDED_BINDER_FIXTURE",
                        "BINDER_SERVICE_PERMISSION_GRANTED");
            } catch (Exception error) {
                writeResult("DENY", false, false, "NONE", "BINDER_TRANSACTION_FAILED");
            } finally {
                reply.recycle();
                data.recycle();
                unbindService(this);
                finish();
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            writeResult("DENY", false, false, "NONE", "BINDER_SERVICE_DISCONNECTED");
            finish();
        }
    };

    private void writeResult(String decision, boolean started, boolean completed,
                             String effect, String reason) {
        try (FileOutputStream output = new FileOutputStream(new File(
                getFilesDir(), "result.json"))) {
            output.write(new JSONObject()
                    .put("request_id", requestId == null ? "" : requestId)
                    .put("authority", "ANDROID_BINDER_SERVICE_PERMISSION")
                    .put("decision", decision)
                    .put("execution_started", started)
                    .put("execution_completed", completed)
                    .put("execution_effect", effect)
                    .put("reason", reason)
                    .toString().getBytes(StandardCharsets.UTF_8));
        } catch (Exception error) {
            throw new IllegalStateException("Unable to write Binder result", error);
        }
    }
}
