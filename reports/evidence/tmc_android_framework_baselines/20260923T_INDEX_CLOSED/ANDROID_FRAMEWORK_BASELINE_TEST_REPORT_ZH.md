# Android Framework Baseline 測試報告

## 1. 範圍與目標

本報告整理 DROS-Mobile 所宣告的 Android framework comparative baseline
set。所有實驗使用相同目標：

- Pixel_7 Android Virtual Device；
- Android API 34；
- x86_64 ABI；
- ADB transport；
- 具有可獨立檢查 effect marker 的 application-runtime fixture。

這些 baseline 是比較性觀測，不是 DROS 的替代品，也不是 Android-wide
security proof。本次宣告集合包含 native permission、AppOps、protected
Binder service，以及 SELinux environment observation 四條 slice。

## 2. 證據方法

每個 baseline 都使用獨立 fixture 與 runner。Runner 保存 request、authority
state、decision、execution-started、execution-completed，以及由 fixture
或 service 擁有的 effect marker。單獨的 result string 不足以形成 closure。
只有在 runner 能根據保存的 artifact 重現預期 deny/allow 或 observation
結果後，才選為 clean candidate。

失敗或受污染的嘗試保留在 provenance history，但不納入 canonical result。
Aggregate machine-readable index 記錄 canonical 路徑與選定的 SHA-256 hash。

## 3. 結果總表

| Baseline | Authority state | 觀測結果 | Evidence status |
|---|---|---|---|
| `ANDROID-PERM-01` | `READ_CONTACTS` 撤銷／授予 | `DENY` 無 execution/effect；`ALLOW` 有 bounded ContactsProvider effect | Verified |
| `ANDROID-APPOPS-01` | permission 已授予；AppOps deny/allow | 結果依 AppOps mode 產生 `DENY` 或 `ALLOW`，並有對應 marker | Verified |
| `ANDROID-BINDER-01` | protected service permission 撤銷／授予 | 撤銷時 Binder bind 被拒且無 effect；授予時 transaction 完成並有 service effect | Verified |
| `ANDROID-SELINUX-01` | AVD policy/context observation | `getenforce=Enforcing`；app 位於 `untrusted_app`；無 app-specific AVC attribution | Observed, not canonical |

### 3.1 Native permission baseline

Artifact：`reports/evidence/tmc_android_permission_baseline/20260923T1R4/`。

App 宣告 `READ_CONTACTS`，並執行 Android permission-mediated ContactsProvider
path。權限撤銷時，app 回傳 `DENY`，沒有開始或完成 bounded action，也沒有
fixture marker。權限授予時，provider query 完成並產生 bounded permission
fixture marker。APK SHA-256：
`87139e56bb922cde4a22736404b3d45022cb915d3ccacab2e2a472dacd935fcb`。

### 3.2 AppOps baseline

Artifact：`reports/evidence/tmc_android_appops_baseline/20260923T1R3/`。

兩個 phase 都維持 `READ_CONTACTS` permission granted，唯一改變的是 native
AppOps mode。`READ_CONTACTS=deny` 產生 `DENY`、無 execution、無 marker；
`READ_CONTACTS=allow` 產生 `ALLOW`、完成 bounded query，並產生 marker。
APK SHA-256：
`8104c7c0e8346d845e31187fa80b2a14ae700948001b29748ba799c6f4e6b1ef`。

### 3.3 Protected Binder service baseline

Artifact：`reports/evidence/tmc_android_binder_baseline/20260923T1R4/`。

Client 在兩個乾淨 uninstall/reinstall phase 呼叫同一個 exported Binder
service。Service permission 撤銷時，client 記錄 `DENY`、
`execution_started=false`、`execution_completed=false`，且 service-side
`effects.jsonl` 沒有記錄。Permission 授予時，Binder transaction 完成，
service 獨立記錄 `BOUNDED_BINDER_FIXTURE`。

Service APK SHA-256：
`56a3ac869a3294749201ccc41b3c02fbbaf14ed07e6ac4ee30f4415e03b2fdea`。
Client APK SHA-256：
`1c96bae4f2850cf3d26b9666e27ca526945a79ca56c240bdcd3a5a848535b8ff`。

### 3.4 SELinux observation

Artifact：`reports/evidence/tmc_android_selinux_baseline/20260923T1/`。

AVD 回報 enforcing mode，DROS baseline process 位於
`u:r:untrusted_app:s0` context。擷取到的 generic AVC records 沒有歸因於
DROS fixture，因此本 slice 僅屬 observation，不能說明 SELinux 導致了
application denial。

## 4. Failure provenance

- Permission 與 AppOps 的早期 runner 嘗試保留在各自 baseline directory；
  若缺乏 clean attribution 或 closure，不列為 canonical。
- Binder `T1` 未將 Java inner classes 納入 DEX input。
- Binder `T1R2` 使用同一 debug signer 的 signature permission，Android 將
  它視為不可 runtime 變更。
- Binder `T1R3` 沿用已安裝 package，因此保留上一輪 permission grant；
  `T1R4` 以乾淨 uninstall/reinstall state reset 修正。

## 5. Claim ceiling

本報告支持的 bounded statement 是：

> 在宣告的 Pixel_7 Android 34 x86_64 application-runtime target 上，native
> permission、AppOps 與 protected Binder-service path 產生了可重現且依
> authority state 改變的 execution outcome；SELinux enforcing mode 與 app
> context 則被觀測到，但沒有 causal denial attribution。

本報告不建立 Android-wide security、Binder-framework-wide security、kernel
enforcement、實體裝置能耗、scalability，或 Android framework mechanism 與
DROS execution governance 等價的主張。
