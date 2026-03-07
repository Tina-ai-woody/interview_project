# Time Drift EDA Plan (Aligned with `baseline_model.ipynb`)

## Objective

用**和 `baseline_model.ipynb` 完全一致**的時間分段方式，先做 drift 檢查，確認資料分布與詐欺行為是否隨時間改變，避免模型在未來區段失效。

---

## Segmentation Rule (Same as Baseline)

依照 baseline notebook 的邏輯：

1. 取 `step` 的唯一值並排序：`steps_sorted = np.sort(df['step'].unique())`
2. 計算切點：
   - `train_cut_idx = int(len(steps_sorted) * 0.70)`
   - `valid_cut_idx = int(len(steps_sorted) * (0.70 + 0.15))`
3. 取得邊界 step：
   - `train_max_step = steps_sorted[train_cut_idx - 1]`
   - `valid_max_step = steps_sorted[valid_cut_idx - 1]`
4. 分段：
   - **Train segment**: `step <= train_max_step`
   - **Valid segment**: `train_max_step < step <= valid_max_step`
   - **Test segment**: `step > valid_max_step`

> 重點：是按「唯一 step 的比例」切，不是按 row 數量硬切。

---

## Drift EDA Scope

### A) Label Drift（目標漂移）

比較 Train / Valid / Test：
- `isFraud` rate
- `isFlaggedFraud` rate
- fraud 在各 `type` 的占比

輸出：
- 分段對照表
- fraud rate 變化折線圖（按 step / step bucket）

---

### B) Feature Distribution Drift（特徵分布漂移）

重點數值欄位：
- `amount`
- `oldbalanceOrg`, `newbalanceOrig`
- `oldbalanceDest`, `newbalanceDest`
- `deltaOrig`, `deltaDest`（衍生）

重點類別欄位：
- `type`

每段輸出：
- 均值 / 中位數 / P90 / P99
- 分布圖（建議 log1p(amount)）
- 類別比例條圖

---

### C) Relationship Drift（關係漂移）

看「同一特徵與 fraud 的關係」是否改變：
- Fraud rate by `type`（三段比較）
- Fraud rate by amount bucket（分段對比）
- step 區間中，`isFlaggedFraud -> isFraud` 的關聯是否穩定

---

## Practical Execution Strategy (Large Data Safe)

因資料量大，執行方式採兩層：

1. **全量輕統計**（必做）
   - 分段筆數、fraud rate、type 比例、分位數
   - 可用 chunk 聚合，避免 kernel 爆記憶體

2. **抽樣視覺化**（建議）
   - 每段做 stratified sample（依 `isFraud`）
   - 圖表只在 sample 上繪製

---

## Drift Decision Criteria (Simple Rules)

先用實務可讀規則，不急著上複雜檢定：

1. **Label drift warning**
   - `|fraud_rate_test - fraud_rate_train| / fraud_rate_train > 20%`

2. **Category drift warning**
   - 任一 `type` 佔比變化 > 5 個百分點

3. **Amount drift warning**
   - `log1p(amount)` 的中位數或 P90 在 Test 相對 Train 偏移明顯（例如 > 15%）

若觸發 warning，後續模型策略需調整：
- 重新校準 threshold
- 加強 time-aware 特徵
- 考慮 rolling retrain

---

## Deliverables

建議最終輸出：

1. `drift_summary_table.csv`
   - Train/Valid/Test 的核心統計

2. `drift_plots/`
   - fraud rate over step
   - amount distribution by segment
   - type composition by segment

3. `drift_findings.md`
   - 主要 drift 發現
   - 對 baseline 模型的風險與調整建議

---

## One-line Summary

**使用與 baseline 完全一致的 step 切分（70/15/15 by unique steps），先做 label/feature/relationship 三層 drift EDA，再回饋模型閾值與特徵策略。**
