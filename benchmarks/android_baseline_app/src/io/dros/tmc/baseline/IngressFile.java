package io.dros.tmc.baseline;

import android.content.Context;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;

final class IngressFile {
    private IngressFile() {}

    static synchronized void append(Context context, String content) {
        append(context, "ingress_records.jsonl", content);
    }

    static synchronized void append(Context context, String name, String content) {
        File target = new File(context.getFilesDir(), name);
        try (FileOutputStream output = new FileOutputStream(target, true)) {
            output.write(content.getBytes(StandardCharsets.UTF_8));
        } catch (Exception error) {
            throw new IllegalStateException("Unable to write ingress record", error);
        }
    }
}
