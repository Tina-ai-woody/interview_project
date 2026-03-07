# Baseline Model Revised Plan（含開發子集策略）

> 專案：Fraud Detection Dynamics Financial Transaction  
> 目標：在筆電資源限制下，仍能維持方法正確（時間切分 + 不平衡評估）並高效率迭代

---

## 1) 任務目標（不變）

- **主要目標：降低漏報（Recall 優先）**
- **輸出方式：風險分級（Low / Medium / High）**
- 不以 Accuracy 為主，改看：
  - PR-AUC（主指標）
  - Recall / Precision / F1
  - Recall@Precision（或 Precision@Recall）

---

## 2) 核心更新：分階段資料策略（Development Subset Strategy）

資料總量約 636 萬筆，70% train 約 445 萬筆，對筆電常過重。  
因此改採「**同一套時間切分 + 不同訓練資料規模**」策略：

### 2.1 時間切分框架固定（避免資料洩漏）
- Train: 前 70% `step`
- Valid: 中間 15% `step`
- Test: 後 15% `step`

### 2.2 訓練資料採分階段放大
- **Stage A（快速迭代）**：Train 區間內抽 10%~20%
- **Stage B（穩健驗證）**：Train 區間內抽 30%~50%
- **Stage C（最終版）**：可行再上 70%~100%（依機器資源）

> 建議：Valid / Test 保持完整或至少固定抽樣方式，確保比較公平。

---

## 3) Baseline + Boosting 模型範圍（保留 + 擴充）

### 3.1 Logistic Regression（主 baseline）
- 用途：
  - 可解釋、穩定
  - 在大資料下通常比傳統樹集成更可控
- 設定：
  - `class_weight='balanced'`
  - `max_iter=1000`
  - 數值特徵標準化 + 類別 one-hot

### 3.2 Decision Tree（對照 baseline）
- 用途：
  - 快速驗證非線性是否有明顯收益
- 設定：
  - 限制 `max_depth`, `min_samples_leaf`
  - `class_weight='balanced'`

### 3.3 Random Forest（可選）
- 筆電上可能非常耗時，建議僅在 Stage A/B 試跑
- 若耗時過高，可改列「補充實驗」而非主結果

### 3.4 LightGBM（建議重點模型）
- 用途：
  - 在大規模表格資料通常比 Random Forest 更快、效果更好
  - 對非線性與特徵交互有較強表現
- 建議設定方向：
  - `objective='binary'`
  - `metric='average_precision'`（或同時計算 AUC）
  - `is_unbalance=true` 或 `scale_pos_weight`
  - `num_leaves`, `min_data_in_leaf`, `feature_fraction`, `bagging_fraction`
  - 搭配 early stopping（以 Valid PR-AUC 監控）

### 3.5 XGBoost（次重點模型，用於交叉驗證）
- 用途：
  - 與 LightGBM 做 boosting 家族的穩健對照
  - 常在極度不平衡資料提供不錯的 precision-recall trade-off
- 建議設定方向：
  - `objective='binary:logistic'`
  - `eval_metric='aucpr'`
  - `scale_pos_weight`（依正負樣本比）
  - `max_depth`, `min_child_weight`, `subsample`, `colsample_bytree`
  - 搭配 early stopping（Valid 上監控 `aucpr`）

---

## 4) 特徵策略（與 baseline_model.md 對齊）

### 4.1 基礎特徵
- 數值：`step`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`
- 類別：`type`
- 衍生：
  - `deltaOrig = oldbalanceOrg - newbalanceOrig`
  - `deltaDest = newbalanceDest - oldbalanceDest`
  - `isOrigBalanceZero`, `isDestBalanceZero`

### 4.2 暫不納入
- `nameOrig`, `nameDest`（高基數 ID，baseline 先避免記憶化過擬合）

### 4.3 欄位注意
- `isFlaggedFraud` 可能接近規則引擎訊號，建議：
  - baseline 保留一版
  - 再做一版移除做敏感度比較

---

## 5) 評估設計（各 Stage 一致）

每個模型皆輸出：
1. PR-AUC（主）
2. ROC-AUC（輔助）
3. Threshold 掃描下的 Precision / Recall / F1
4. Confusion Matrix
5. Risk Tier 統計：Low / Medium / High 的 volume、fraud rate、fraud capture

---

## 6) 風險分級與閾值策略

先在 Valid 定義，再固定到 Test：
- `t_high`：高風險池（追求較高 precision）
- `t_mid`：中風險池（提升 recall 覆蓋）

可採雙約束：
- 約束 A：High risk precision 至少達某值（如 0.25）
- 約束 B：中高風險總量不超過可審核容量

---

## 7) 建議執行節奏（筆電友善）

### Stage A（1~2 小時內完成）
- Train 20% 子集
- 跑 Logistic + Decision Tree
- 產生初版 threshold 與風險分級

### Stage B（半天內）
- Train 擴大到 50%
- 重跑 Logistic
- 新增 LightGBM（優先）
- 比較 Stage A/B 指標穩定性（特別看 PR-AUC 與 Recall@Precision）

### Stage C（時間允許）
- Logistic 上近全量 Train
- LightGBM 上較大資料量（必要時調降複雜度）
- XGBoost 作為補充對照（可用較小資料或較少迭代）
- Tree / Random Forest 保留為 baseline 參照
- 固定最終分級規則到 Test

---

## 8) 面試敘事建議

可用以下邏輯回答「為何不直接全量訓練」：

1. 資源限制下，先用開發子集快速驗證特徵與評估框架。
2. 全程維持時間切分，避免方法上失真。
3. 確認策略有效後再逐步擴大資料量，提高實驗效率與可重現性。
4. 最終指標以 PR-AUC 與風險分級表現做決策，而非 Accuracy。

---

## 9) LightGBM / XGBoost 實作注意事項（補充）

1. **不平衡處理**
   - 先用正負樣本比估算 `scale_pos_weight`
   - 與未加權版本都保留紀錄，避免只看單一設定

2. **早停與驗證**
   - 一律用時間切分後的 Valid 做 early stopping
   - LightGBM 監控 `average_precision`；XGBoost 監控 `aucpr`

3. **資源控制**
   - 先限制樹深、葉節點與迭代數（例如 200~500 rounds 起步）
   - 先求穩定結果，再慢慢加大模型容量

4. **結果呈現**
   - 至少比較：Logistic vs LightGBM vs XGBoost
   - 用同一套 threshold 與 risk tier 規則，確保可比性

---

## 10) 與原 baseline_model.md 的關係

- `baseline_model.md`：完整 baseline 架構與模型計畫
- `baseline_model_revised.md`：在筆電環境下加入「開發子集 + 分階段放大 + Boosting（LightGBM/XGBoost）」實作策略

兩者互補，revised 版是執行層面的資源優化與落地版本。
