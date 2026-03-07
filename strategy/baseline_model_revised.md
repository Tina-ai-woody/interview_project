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

## 3) Baseline 模型範圍（保留 + 調整）

### 3.1 Logistic Regression（主 baseline）
- 用途：
  - 可解釋、穩定
  - 在大資料下通常比樹模型更可控
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
- 重跑 Logistic（必要時加 Tree）
- 比較 Stage A/B 指標穩定性

### Stage C（時間允許）
- Logistic 上近全量 Train
- Tree 模型保留為對照或小樣本補充
- 固定最終分級規則到 Test

---

## 8) 面試敘事建議

可用以下邏輯回答「為何不直接全量訓練」：

1. 資源限制下，先用開發子集快速驗證特徵與評估框架。
2. 全程維持時間切分，避免方法上失真。
3. 確認策略有效後再逐步擴大資料量，提高實驗效率與可重現性。
4. 最終指標以 PR-AUC 與風險分級表現做決策，而非 Accuracy。

---

## 9) 與原 baseline_model.md 的關係

- `baseline_model.md`：完整 baseline 架構與模型計畫
- `baseline_model_revised.md`：在筆電環境下加入「開發子集 + 分階段放大」實作策略

兩者互補，revised 版是執行層面的資源優化與落地版本。
