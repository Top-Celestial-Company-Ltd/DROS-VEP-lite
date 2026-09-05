# 🛸 DROS-Physical-Drone-Bench: Physical AI / 无人机實體執行期防禦基準

本專案為 **DROS (Deterministic Runtime Operation System)** 針對 **無人機 (Drone)、邊緣 Homelab 私有雲與 Physical AI (具身智能)** 所打造的專屬安全評測基準與展示套件。

---

## 🎯 產業痛點 (Industrial Pain Points for Systems & Test Engineers)

1. **物理炸機不可逆性**：傳統軟體報錯可重啟，但無人載具在空中收到惡意指令（如 Disarm 或滿油門覆寫）會直接導致墜毀或人身安全事故。
2. **Homelab 語意上下文盲區 (Context-Blindness)**：邊緣私有雲中多個 Agent 共享同一區域網路與 Process，Seccomp 與路由器無法分辨 MAVLink 封包是由哪個 Agent 角色發出。
3. **微秒級實時控制要求**：Python 語意護欄需要 500ms 以上，而 DROS L4 C-ABI 門閘提供 **< 500ns 帶內硬熔斷**。

---

## 🚀 快速開始 (Quick Start)

只需具備 Python 3.8+ 環境即可直接一鍵執行：

```bash
python run_drone_bench.py
```

### 驗證對照：
* **B0 (Bare Mode - 無 DROS)**：攻擊成功穿透，馬達於 20 米空中停轉，自由落體墜毀（$\Delta S > 0$）。
* **B1 (DROS Enabled - 啟用治理)**：C-ABI 於 500 納秒內直接 DENY，無人機姿態鎖定並安全懸停（$\Delta S \equiv 0$）。
