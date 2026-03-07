# Time Drift EDA Plan (Updated: Fine-grained Segments + Holdout)

## Objective

針對 `Transactions Data.csv` 進行更細緻的 time drift 檢查，提升趨勢觀察能力，同時保留可用於模型最終評估的穩定測試尾段。

---

## Why Update the Strategy

原先只用 baseline 的 70/15/15 三段切分，適合建模評估，但對 drift 訊號解析度不足。  
更新後採用「**雙軌分段策略**」：

1. **Drift Track（細分段）**：用較小時間段看漂移
2. **Model Track（保留尾段）**：保留最終 test holdout 做模型檢驗

> 重點：drift 分析可細分；模型最終比較仍需要穩定 holdout。

---

## Segmentation Design

## A) Drift Track — Fine-grained Segmentation

以 `step` 為主切更小區段，推薦兩種方式擇一：

### Option 1: Quantile Bins by Unique Steps（推薦）
- 將 `step` 的唯一值切成 `N=12` 或 `N=20` 段（decile/ventile 類似概念）
- 每段時間跨度不一定相同，但可維持較均衡的步數密度

### Option 2: Fixed-width Step Buckets
- 例如每 `24` step 一段（可視為日級）
- 時間跨度固定，較直觀

**建議預設：** `N=12`（先兼顧穩定與解析度）

---

## B) Model Track — Stable Holdout

保留 baseline 的尾段觀念：
- 例如最後 15% unique steps 當最終 test 區
- 不用於調參，只做最終驗證

這樣可以避免 drift 細分後每段 fraud 太少，導致模型評估指標不穩。

---

## Drift EDA Scope

### 1) Label Drift
每個細分段計算：
- `isFraud` rate
- `isFlaggedFraud` rate
- fraud volume

輸出：
- fraud rate over time（折線圖）
- rolling mean（例如 window=3）平滑曲線

### 2) Feature Distribution Drift
每段比較：
- `amount`（建議 log1p）
- `oldbalanceOrg`, `newbalanceOrig`
- `oldbalanceDest`, `newbalanceDest`
- `deltaOrig`, `deltaDest`
- `type` 組成比例

統計指標：
- mean / median / P90 / P99
- 類別比例變化

### 3) Relationship Drift
每段觀察：
- Fraud rate by `type`
- Fraud rate by amount bucket
- `isFlaggedFraud -> isFraud` 關聯是否改變

---

## Large-data Execution Plan

資料量大（~636萬），採以下執行方式：

1. **全量輕統計（必要）**
   - 只做 groupby 聚合（count/rate/quantile）
   - 以 chunk 方式累積，避免 kernel 爆記憶體

2. **分層抽樣視覺化（建議）**
   - 每個時間段做 stratified sample（依 `isFraud`）
   - 只在 sample 上畫 histogram/box/scatter

---

## Drift Warning Rules (Practical)

1. **Label drift warning**
- 任兩相鄰時間段 fraud rate 相對變化 > 20%

2. **Category drift warning**
- 任一 `type` 占比在相鄰段差異 > 5 個百分點

3. **Amount drift warning**
- `log1p(amount)` 的 median 或 P90 在相鄰段變化 > 15%

若多段連續觸發 warning：
- 在模型端做 threshold re-calibration
- 評估 rolling retrain 頻率
- 強化 time-aware features

---

## Deliverables

1. `drift_summary_fine_segments.csv`
   - 每個細分段核心統計

2. `drift_plots/`
   - fraud_rate_by_segment.png
   - fraud_rate_rolling.png
   - amount_quantiles_by_segment.png
   - type_share_by_segment.png

3. `drift_findings.md`
   - 漂移時點
   - 對模型與閾值的影響
   - retrain/monitoring 建議

4. `holdout_definition.md`
   - 最終 test holdout 的 step 邊界（供 baseline 模型一致使用）

---

## One-line Summary

**Drift 分析改用細分時間段提升解析度；同時保留最終 test holdout，確保模型評估仍可比較且可信。**
