# DROS-Mobile SDK Policy Harness

本 VEP 模組是供 mobile-agent 威脅劇本使用的 host-side policy fixture。Python adapters 透過 `ctypes` 載入 host Windows DLL，僅模擬 mobile-style request shape；不會執行 Android JNI、iOS Swift 或實體裝置 runtime。

## 測試情境

Harness 對相簿／通訊錄、剪貼簿／OTP、背景位置與麥克風、以及生物辨識付款等請求執行本地 assertions。結果只描述宣告的 fixture，不是 Android OS permission test 或 mobile-platform security result。

## 執行

```bash
python benchmarks/mobile_sdk/run_mobile_bench.py
```

## 證據範圍

- 舊 adapter 輸出的 P50/P99 是 host-side wrapper timing，不是手機端 latency；runner 未保存 raw timing samples。
- 本 harness **未量測** battery、power、energy 或 network-egress impact。歷史 `<0.001 mAh`／`<0.05 μJ` 數字是未驗證 estimate，不得視為實測。
- 宣告 Pixel_7 Android 34 x86_64 application-runtime 的證據，請使用 `reports/evidence/tmc_android_phase1_2_index/` 與 `reports/evidence/tmc_android_framework_baselines/` 下的 TMC indexes。
