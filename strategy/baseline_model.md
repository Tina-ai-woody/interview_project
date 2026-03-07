# Baseline Model 實作計畫（Fraud Detection）

## 1) 目標與原則

### 目標
- **主要目標：降低漏報**（Recall 優先）
- **輸出方式：風險分級**（Low / Medium / High）
- 先建立可解釋、可重現的 baseline，作為後續進階模型（XGBoost/LightGBM）比較基準

### 原則
- 以 `step` 做**時間切分**，避免資料洩漏
- 不以 Accuracy 為主，改看 PR-AUC / Recall / Precision
- 先做「簡單但正確」版本，再逐步增加複雜度

---

## 2) 資料切分與驗證設計

### 時間切分（建議）
- Train: 前 70% `step`
- Valid: 中間 15% `step`
- Test: 後 15% `step`

> 不使用 random split（會把未來資訊洩漏到訓練集）

### 驗證策略
- 先固定一組 Hold-out（Train/Valid/Test）
- 若時間允許，再補 walk-forward 驗證（rolling window）檢查穩定性

---

## 3) 資料前處理與特徵規劃

### 3.1 目標欄位
- `y = isFraud`

### 3.2 基礎特徵（第一版）
- 數值：`step`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`
- 類別：`type`
- 衍生特徵：
  - `deltaOrig = oldbalanceOrg - newbalanceOrig`
  - `deltaDest = newbalanceDest - oldbalanceDest`
  - `isOrigBalanceZero = (oldbalanceOrg == 0)`
  - `isDestBalanceZero = (oldbalanceDest == 0)`

### 3.3 暫不納入（第一版）
- `nameOrig`, `nameDest`（高基數 ID，先避免過擬合與記憶化）

### 3.4 缺失與縮放
- 先確認缺失值（預期少）
- Logistic Regression 對數值做 `StandardScaler`
- Tree model 不強制縮放

---

## 4) Baseline 模型實作範圍

## 4.1 Logistic Regression Baseline

### Pipeline
- `ColumnTransformer`
  - `type` → OneHotEncoder
  - 數值欄位 → StandardScaler
- 模型：`LogisticRegression`
  - `class_weight='balanced'`
  - `max_iter=1000`

### 目的
- 做為可解釋 linear baseline
- 觀察哪些特徵方向與強度與詐欺相關

### 觀察點
- PR-AUC
- Recall@指定 Precision（例如 Precision >= 0.10 / 0.20）
- 係數方向是否符合業務直覺

---

## 4.2 Tree Model Baseline（建議先 Decision Tree，再 Random Forest）

### A. Decision Tree（快速可解釋）
- `DecisionTreeClassifier`
- 重要參數：`max_depth`, `min_samples_leaf`, `class_weight='balanced'`

### B. Random Forest（穩定版 tree baseline）
- `RandomForestClassifier`
- 重要參數：`n_estimators`, `max_depth`, `min_samples_leaf`, `class_weight='balanced_subsample'`

### 目的
- 擷取非線性關係與特徵交互作用
- 與 Logistic 比較 Recall / Precision trade-off

### 觀察點
- PR-AUC 是否明顯提升
- 是否在同等 Precision 下提供更高 Recall
- Feature importance（僅做輔助解讀）

---

## 5) 評估與報告格式（統一）

每個模型在 **Valid + Test** 都輸出：

1. PR-AUC
2. ROC-AUC（僅輔助）
3. 不同 threshold 的 Precision / Recall / F1
4. 混淆矩陣（預設 threshold + 最佳策略 threshold）
5. 風險分級結果（建議）
   - High: `p >= t_high`
   - Medium: `t_mid <= p < t_high`
   - Low: `p < t_mid`

---

## 6) 風險分級閾值規劃

先在 Valid 集上找閾值，再固定到 Test：

- `t_high`：偏高 precision（高風險池）
- `t_mid`：提升 recall（中風險池）

可用兩種方式定義：
1. 以 Precision 約束定義（如 High risk 需 Precision >= 0.3）
2. 以容量限制定義（如每日可人工審核前 K 筆）

---

## 7) 交付物（Deliverables）

1. Notebook / script：
   - 資料切分
   - 特徵工程
   - Logistic baseline
   - Tree baseline
2. 一頁比較表（Valid/Test）
   - PR-AUC, Recall@Precision, F1
3. 風險分級示意表
   - 各分級占比、詐欺率、捕獲率
4. 面試可講版本（3~5 分鐘）

---

## 8) 執行順序（建議）

1. 建立時間切分
2. 完成共同前處理與特徵工程
3. 跑 Logistic Regression baseline
4. 跑 Decision Tree / Random Forest baseline
5. 在 Valid 做 threshold 與分級策略
6. 固定策略到 Test 做最終報告

---

## 9) 風險與注意事項

- 極度不平衡資料下，Accuracy 幾乎無參考價值
- `isFlaggedFraud` 可能有規則引擎痕跡，需小心是否造成不公平比較
- 若未來納入 `nameOrig/nameDest`，需避免 ID 記憶化（例如 target encoding 必須嚴格在訓練折內）

---

## 10) 下一步（可直接執行）

- [ ] 先實作 Logistic baseline（含 PR curve + 閾值掃描）
- [ ] 再加 Decision Tree baseline 做第一輪比較
- [ ] 根據 Valid 結果決定是否加 Random Forest
- [ ] 產出第一版風險分級規則
