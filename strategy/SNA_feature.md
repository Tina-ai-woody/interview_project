# SNA Feature Engineering Plan（Fraud Detection）

> 目標：以 Social Network Analysis（SNA）建立交易關係特徵，評估是否提升 fraud 預測表現（Recall 優先）。

---

## 1) 為什麼在這份資料可行

資料天然是交易網路：
- 節點（Node）：`nameOrig`, `nameDest`
- 邊（Edge）：每筆交易（`nameOrig -> nameDest`）
- 邊屬性：`amount`, `type`, `step`, `isFraud`

SNA 可補足一般表格特徵不足，捕捉：
- 可疑資金路徑
- 異常互動模式
- 高風險節點/社群

---

## 2) 最高原則：防資料洩漏（必守）

1. **時間切分固定**：Train / Valid / Test 依 `step`。
2. **特徵只能用過去資訊**：每筆交易 `t` 的特徵只能來自 `< t` 的歷史。
3. **禁止全資料先建圖再回填特徵**（這會把未來資訊洩漏到過去）。
4. **Valid/Test 僅用 Train（或當前之前）統計更新**，不能看未來標籤。

---

## 3) 分階段特徵路線圖（由低成本到高價值）

## Stage 1：低成本、可增量（先做）

### A. Node degree 類
- `orig_out_degree_hist`：來源帳戶歷史轉出次數
- `dest_in_degree_hist`：目的帳戶歷史轉入次數
- `orig_unique_dest_hist`：來源歷史不同目的帳戶數
- `dest_unique_orig_hist`：目的歷史不同來源帳戶數

### B. Edge relation 類
- `pair_txn_count_hist`：`(nameOrig, nameDest)` 歷史交易次數
- `pair_last_seen_gap`：距上次同 pair 交易的時間差
- `is_first_time_pair`：是否首次互動

### C. Flow amount 類（歷史累積）
- `orig_out_amount_sum_hist`
- `dest_in_amount_sum_hist`
- `orig_avg_amount_hist`
- `pair_avg_amount_hist`

> 預期：這批通常可在筆電可接受成本內完成，且最容易有增益。

---

## Stage 2：時間窗口化 SNA 特徵（中成本）

在固定窗口（例如最近 24h、最近 7 天）計算：

### A. Window degree / activity
- `orig_out_degree_w1d`, `orig_out_degree_w7d`
- `dest_in_degree_w1d`, `dest_in_degree_w7d`
- `orig_txn_count_w1d`, `orig_txn_count_w7d`

### B. Window amount behavior
- `orig_out_amount_sum_w1d`, `w7d`
- `orig_out_amount_mean_w1d`, `w7d`
- `orig_out_amount_std_w1d`, `w7d`
- `pair_amount_sum_w1d`, `w7d`

### C. Burst / anomaly proxy
- `orig_activity_burst = txn_count_w1d / max(txn_count_w7d,1)`
- `orig_amount_burst = amount_sum_w1d / max(amount_sum_w7d,eps)`

> 預期：對短期異常行為偵測（詐欺高峰）更敏感。

---

## Stage 3：圖演算法特徵（高成本，選做）

### A. Node importance
- PageRank（分時間窗重算）
- HITS（hub/authority）

### B. Local structure
- 2-hop neighbor count
- 三角關係或閉環 proxy（可用簡化版本）

### C. Community features
- 社群 ID（Louvain/Leiden）
- 社群歷史 fraud rate（需嚴格時間約束）

> 注意：這部分算力消耗高，建議在 Stage 1/2 已證實有效後再做。

---

## 4) 建議先做的 8 個核心 SNA 特徵（MVP）

1. `orig_out_degree_hist`
2. `dest_in_degree_hist`
3. `orig_unique_dest_hist`
4. `dest_unique_orig_hist`
5. `pair_txn_count_hist`
6. `is_first_time_pair`
7. `orig_out_amount_sum_hist`
8. `pair_avg_amount_hist`

這 8 個特徵具備：
- 防洩漏可控
- 可增量更新
- 計算成本相對可接受
- 容易對接 baseline 模型

---

## 5) 與現有模型流程整合方式

1. 在既有時間切分前提下新增 SNA features。
2. 先與原 baseline features 做組合：
   - Base only
   - Base + SNA(MVP)
3. 模型比較順序：
   - Logistic Regression（可解釋）
   - LightGBM（主力）
   - XGBoost（對照）
4. 評估：PR-AUC、Recall@Precision、Risk tier 覆蓋率。

---

## 6) 成功判準（建議）

在 Test 上至少達成其一：
1. PR-AUC 明顯提升（相對提升 > 3% 可視為有意義）
2. 在固定 Precision 條件下（如 >= 0.2），Recall 提升
3. 在固定審核量（Top-K）下，抓到更多 fraud

---

## 7) 計算資源與執行策略（筆電）

- 先在 Train 子集（20%）做 SNA MVP 驗證
- 若有效，再擴到 50%
- 全量僅保留最有增益特徵，避免過重
- 盡量使用可增量更新統計（dict / groupby 累積），避免每步重建全圖

---

## 8) 風險與應對

1. **特徵過多導致過擬合**
   - 先做 MVP，小步擴張
2. **ID 記憶化偏差**
   - 以關係統計代替直接 one-hot ID
3. **算力不足**
   - 優先歷史累積/窗口統計，延後圖演算法
4. **評估失真**
   - 固定同一切分與同一評估協議

---

## 9) 執行清單（下一步）

- [ ] 定義 SNA MVP 欄位 schema（8 個）
- [ ] 在時間序列流程中落實「只看過去」特徵生成
- [ ] 完成 Base vs Base+SNA 的對照實驗
- [ ] 在 LightGBM / XGBoost 上驗證增益
- [ ] 產出面試版結論（指標 + 風險分級影響）

---

## 10) 面試敘事範本（可直接講）

> 我把交易資料視為動態有向網路，先建立低成本且可增量更新的 SNA 特徵（節點活躍度、關係強度、資金流統計），並嚴格限制特徵只能使用當下之前的資訊，避免資料洩漏。接著用 Base 與 Base+SNA 在相同時間切分下比較 PR-AUC 與 Recall@Precision，確認 SNA 是否在固定誤報成本下提升詐欺捕獲率。
