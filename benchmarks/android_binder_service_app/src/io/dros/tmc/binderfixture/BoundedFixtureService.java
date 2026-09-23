package io.dros.tmc.binderfixture;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.os.Parcel;
import android.os.RemoteException;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;

public final class BoundedFixtureService extends Service {
    private final Binder binder = new Binder() {
        @Override
        protected boolean onTransact(int code, Parcel data, Parcel reply, int flags)
                throws RemoteException {
            if (code != 1) {
                return super.onTransact(code, data, reply, flags);
            }
            String requestId = data.readString();
            appendEffect(requestId == null ? "" : requestId);
            reply.writeNoException();
            reply.writeString("BOUNDED_BINDER_FIXTURE");
            return true;
        }
    };

    @Override
    public IBinder onBind(Intent intent) {
        return binder;
    }

    private void appendEffect(String requestId) {
        try (FileOutputStream output = new FileOutputStream(
                new File(getFilesDir(), "effects.jsonl"), true)) {
            output.write(new JSONObject()
                    .put("request_id", requestId)
                    .put("effect", "BOUNDED_BINDER_FIXTURE")
                    .toString().concat("\n").getBytes(StandardCharsets.UTF_8));
        } catch (Exception error) {
            throw new IllegalStateException("Unable to record Binder fixture effect", error);
        }
    }
}
