# Account-level SNA Feature Revised Plan（進階版）

> 基於 `account_SNA_feature.md` 的 MVP（12 欄）進一步擴充，目標是提升在極度不平衡資料下的 Recall 與 PR-AUC，並維持嚴格防洩漏。

---

## 1) 設計目標

1. 在帳戶級 SNA 特徵中加入「時間窗口、關係強度、網路結構、風險傳播」訊號。  
2. 保持交易級預測任務（`isFraud`），但強化每筆交易的帳戶上下文。  
3. 將模型主力放在 LightGBM / XGBoost，Logistic 保留可解釋對照。  
4. 全程遵守時間因果：特徵只使用 `t_j < t_i` 的資料。

---

## 2) 防洩漏規範（進階版仍必守）

對第 `i` 筆交易（時間 `t_i`），特徵定義：
\[
 f_i = g(\{e_j \mid t_j < t_i\})
\]

### 禁止事項
- 先用全資料建圖再回填特徵
- 使用未來窗口（`t_j >= t_i`）
- 使用全期間計算的帳戶 fraud rate / centrality

### 建議做法
- 逐筆增量更新（online stats）
- 或按時間區塊批次更新（block-wise, strictly past-only）

---

## 3) 進階特徵分層架構

## Layer A：MVP 延伸（低成本，高收益）

在原 12 欄上新增：
1. `orig_out_amount_std_hist` / `dest_in_amount_std_hist`（金額波動）
2. `orig_recent_txn_gap` / `dest_recent_txn_gap`（最近一次活動間隔）
3. `orig_pair_concentration_top1`（最大對手占比）
4. `dest_pair_concentration_top1`

> 用途：辨識「突然活躍、金額不穩定、關係過度集中」行為。

---

## Layer B：窗口化時序特徵（中成本）

針對 1d / 7d / 30d（以 `step` 映射）建立：

### 活躍度
- `orig_out_degree_w1/w7/w30`
- `dest_in_degree_w1/w7/w30`

### 金額
- `orig_out_amt_sum_w1/w7/w30`
- `dest_in_amt_sum_w1/w7/w30`
- `orig_out_amt_mean_w1/w7`

### 變化率 / burst
- `orig_degree_burst = out_degree_w1 / max(out_degree_w7,1)`
- `orig_amt_burst = amt_sum_w1 / max(amt_sum_w7,eps)`
- `dest_degree_burst`, `dest_amt_burst`

> 用途：捕捉短期異常激增（詐欺常見模式）。

---

## Layer C：關係與對手方特徵（中高成本）

以帳戶-對手 pair 與鄰居分布建立：

1. `pair_txn_count_hist`（同 pair 歷史次數）
2. `pair_amt_sum_hist`, `pair_amt_mean_hist`
3. `pair_last_seen_gap`
4. `is_first_time_pair`
5. `counterparty_entropy_orig`（來源對手方分布熵）
6. `counterparty_entropy_dest`

> 用途：識別「陌生對手突發大額」與「洗錢式分散/集中路徑」。

---

## Layer D：圖結構特徵（高成本，分階段啟用）

### 節點重要性
- Rolling PageRank（窗口化重算）
- HITS hub / authority（選做）

### 局部結構
- 2-hop neighbors count
- 局部 clustering proxy
- reciprocal edge ratio（互轉比例）

### 社群訊號（選做）
- 社群 ID（Louvain/Leiden）
- 社群歷史活躍度與金額密度

> 注意：社群風險率若要引入，必須以過去窗口計算，避免標籤洩漏。

---

## 4) 推薦進階特徵實作清單（第一輪 24 欄）

在原 12 欄外，先新增以下 12 欄（合計 24）：

1. `orig_out_amount_std_hist`
2. `dest_in_amount_std_hist`
3. `orig_recent_txn_gap`
4. `dest_recent_txn_gap`
5. `orig_pair_concentration_top1`
6. `dest_pair_concentration_top1`
7. `orig_out_degree_w7`
8. `dest_in_degree_w7`
9. `orig_out_amt_sum_w7`
10. `dest_in_amt_sum_w7`
11. `orig_degree_burst_w1_w7`
12. `dest_degree_burst_w1_w7`

> 這組是成本與效益平衡最好的進階版起手式。

---

## 5) 模型策略（Revised）

## 5.1 Model Ladder
1. Logistic（解釋基準）
2. LightGBM（主力）
3. XGBoost（穩健對照）

## 5.2 特徵 A/B 設計
- Exp-A: Base only
- Exp-B: Base + Account-SNA (12)
- Exp-C: Base + Account-SNA Revised (24)
- Exp-D: Base + Account-SNA Revised + Pair features

## 5.3 指標
- PR-AUC（主）
- Recall@Precision>=X
- Top-K fraud capture
- Risk tier capture (High/Medium/Low)

---

## 6) 計算與工程規劃

## 6.1 計算策略
- 先 20% train 子集做特徵驗證
- 有增益再擴到 50%
- 全量僅保留最有增益特徵

## 6.2 實作建議
- 以 `dict + deque` 做窗口統計
- 以單 pass 或時間塊更新避免重算全圖
- 對高成本圖特徵採離線批次（分 step 區間）

---

## 7) 風險與對策

1. **特徵過多導致過擬合**
   - 用 feature importance / permutation 做裁剪
2. **算力不足**
   - 先跑 24 欄進階版，不急著上 PageRank/社群
3. **冷啟動帳戶**
   - 以 0 + 全域先驗值補齊
4. **時序漂移**
   - 做 walk-forward 或分時段評估

---

## 8) 交付物（Revised）

1. `notebooks/account_SNA_feature_revised.ipynb`（後續實作）
2. 特徵字典（欄位定義、公式、洩漏防護）
3. A/B/C 實驗比較表（PR-AUC、Recall@Precision）
4. 風險分級容量與捕獲分析

---

## 9) 驗收標準

至少達成其一：
1. Revised 版相對 MVP 版 PR-AUC 再提升
2. 在固定 Precision 閾值下 Recall 顯著提升
3. 在固定審核容量下捕獲更多 fraud

---

## 10) 面試敘事（進階版）

> 我先以 leakage-safe 的帳戶級 SNA MVP 建立行為基線，再加入窗口化與關係強度等進階特徵，逐步驗證每層特徵對 PR-AUC 與 Recall@Precision 的邊際貢獻。這種分層式特徵工程能在資源限制下兼顧可解釋性、可重現性與實際預測效益。
