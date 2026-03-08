# Transaction-level Retrospective Mining Plan（交易級回顧式關聯）

> 目標：以交易 `isFraud` 為核心，建立交易級 SNA/行為特徵，先做 retrospective pattern mining，再篩選可遷移到 baseline 的特徵。

---

## 1) 任務定位（雙模式）

- 分析單位：**交易級**（每筆交易一列）
- 標籤：`isFraud`
- 目的：找出與交易詐欺高度相關的特徵組合（關聯分析）

本計畫採雙模式：

### Mode A：Retrospective Exploratory（純回顧洞察）
- 允許使用全歷史統計來挖掘關聯模式
- 目標是洞察與行為規則，不主張即時預測可用性

### Mode B：Leakage-safe Transfer（可遷移 baseline）
- 只保留交易當下可取得、且 past-only 的特徵
- 目標是把有效特徵導入 baseline model 做公平比較

---

## 2) 與 account-level 分析的關係

- account-level：擅長做行為輪廓與群像
- transaction-level：擅長直接優化 `isFraud` 預測

本計畫會把帳戶特徵映射到交易：
- `orig_*_at_txn`
- `dest_*_at_txn`
- `pair_*_at_txn`

---

## 3) 特徵框架（可疑交易級特徵）

## A. 交易本身（基礎）
1. `amount`, `log1p_amount`
2. `type`
3. `deltaOrig = oldbalanceOrg - newbalanceOrig`
4. `deltaDest = newbalanceDest - oldbalanceDest`
5. `balance_inconsistency_flags`（餘額變化異常旗標）

## B. 來源帳戶狀態（at txn time）
1. `orig_out_degree_hist`
2. `orig_unique_dest_hist`
3. `orig_out_amount_sum_hist`
4. `orig_out_amount_mean_hist`
5. `orig_out_amount_std_hist`
6. `orig_recent_gap`
7. `orig_activity_burst_proxy`
8. `orig_repeat_counterparty_ratio`
9. `orig_counterparty_entropy`

## C. 目的帳戶狀態（at txn time）
1. `dest_in_degree_hist`
2. `dest_unique_orig_hist`
3. `dest_in_amount_sum_hist`
4. `dest_in_amount_mean_hist`
5. `dest_in_amount_std_hist`
6. `dest_recent_gap`
7. `dest_activity_burst_proxy`
8. `dest_repeat_counterparty_ratio`
9. `dest_counterparty_entropy`

## D. Pair 關係特徵（origin-destination）
1. `pair_txn_count_hist`
2. `pair_amount_sum_hist`
3. `pair_amount_mean_hist`
4. `pair_last_seen_gap`
5. `is_first_time_pair`
6. `pair_share_in_orig_out`（該 pair 在來源帳戶流出中的占比）

## E. 交互與比值特徵（交易級可疑模式）
1. `amount_vs_orig_mean_ratio = amount / max(orig_out_amount_mean_hist, eps)`
2. `amount_vs_pair_mean_ratio = amount / max(pair_amount_mean_hist, eps)`
3. `orig_dest_degree_ratio = orig_out_degree_hist / max(dest_in_degree_hist,1)`
4. `new_counterparty_and_large_amount`（首次 pair 且金額偏大）
5. `burst_and_large`（活躍突增且大額）

---

## 4) 雙模式實作規則（Exploratory vs Transfer）

## Mode A：Retrospective Exploratory（洞察優先）
- 可使用全歷史聚合特徵（例如全期間 entropy、全期間 concentration）
- 可快速辨識高關聯行為樣態
- 產出重點：關聯強度、行為 archetypes、SHAP 解釋

## Mode B：Leakage-safe Transfer（導入 baseline）
對第 `i` 筆交易（時間 `t_i`）：
\[
 f_i = g(\{e_j \mid t_j < t_i\})
\]

### 落地準則
1. 逐筆（或時間塊）先取特徵，再更新狀態
2. 禁止全資料聚合後回填
3. 若用窗口特徵，窗口上界必須小於 `t_i`
4. 只將 Mode B 通過的特徵導入 baseline 比較

---

## 5) 分階段實作（對齊 baseline）

## Stage A（20% train，快速驗證）
- 建立 A+B+C+D 類核心特徵
- 模型：Logistic + Decision Tree
- 觀察：PR-AUC、threshold scan

## Stage B（50% train，穩健比較）
- 新增 E 類交互特徵
- 模型：Logistic / Decision Tree / LightGBM
- 加入 SHAP 看重要特徵

## Stage C（近全量，最終版本）
- 特徵裁剪後跑：Logistic / Decision Tree / LightGBM / XGBoost（可選）
- 產出風險分級（Low/Medium/High）

---

## 6) 評估框架（主軸）

1. **PR-AUC**（主指標）
2. **Threshold scan**（Precision/Recall/F1 across thresholds）
3. **Risk tier**
   - 各 tier volume
   - 各 tier fraud rate
   - High+Medium fraud capture
4. 補充：Recall@Precision（例如 Precision>=0.2）

---

## 7) 特徵遷移策略（Mode A -> Mode B -> Baseline）

將 Mode A 挖掘出的特徵分 3 類：

### A. 可直接遷移（推薦）
- 嚴格 past-only 且交易當下可得特徵
- 例如 degree_hist / pair_count_hist / recent_gap

### B. 可遷移但需改寫
- retrospective 用全期統計者，需重寫成滾動/歷史版

### C. 暫不遷移
- 明顯依賴未來資訊或高風險洩漏特徵

---

## 8) 交付物（Deliverables）

1. `notebooks/transaction_level_retrospective_mining.ipynb`
2. `transaction_feature_table.csv`
3. `transaction_pattern_model_importance.csv`
4. `transaction_pattern_threshold_scan.csv`
5. `transaction_pattern_risk_tier_summary.csv`
6. `transaction_pattern_findings.md`

---

## 9) 成功標準

至少達成其一：
1. 新增交易級 SNA 特徵後 PR-AUC 提升
2. 在固定 Precision 下 Recall 提升
3. 在固定審核容量下 fraud capture 提升

---

## 10) 一句話總結

以交易為中心整合來源帳戶、目的帳戶與 pair 關係的歷史 SNA 訊號，先做回顧式關聯挖掘，再把可因果落地的特徵導入 baseline 模型，提升詐欺捕捉能力。