# Stratified Sampling Strategy for EDA

## Goal

針對 `Transactions Data.csv`（約 636 萬筆、`isFraud` 極度不平衡）設計一套**可穩定執行、不易炸 kernel**的 EDA 策略。核心方法是：

- 先做**分層抽樣（stratified sampling）**進行探索式分析
- 再用全量資料做必要的輕量驗證（counts / ratios）

---

## Why Stratified Sampling

如果直接隨機抽樣，在本資料集中可能遇到：
- fraud 樣本太少，視覺化幾乎看不到差異
- 每次抽樣波動大，結論不穩

以 `isFraud` 分層可確保：
1. 抽樣資料中同時有足夠的 fraud 與 non-fraud
2. 模式探索（distribution / boxplot / feature contrast）更清楚
3. 可用較小樣本完成大部分圖表探索

---

## Two-Sample Design (Recommended)

為了同時兼顧「真實分布」與「可觀察性」，建立兩份樣本：

### A) Representative Sample（代表性樣本）
- 用途：估計接近母體分布的統計（例如整體分布、type 比例）
- 方法：依 `isFraud` 分層後按原比例抽樣
- 建議大小：
  - 300k（筆電）
  - 500k（工作站）

### B) Analytical Sample（分析樣本）
- 用途：看 fraud/non-fraud 差異（箱型圖、分布對比、特徵關聯）
- 方法：對 fraud 全保留（或高比例保留），non-fraud 下採樣
- 建議比例：
  - fraud:non-fraud = 1:5 或 1:10
- 注意：
  - 此樣本**不代表真實機率**，只用於模式探索

---

## Sampling Steps

1. 定義隨機種子（確保可重現）
   - `random_state = 42`
2. 以 `isFraud` 做 strata
3. 先產生 Representative Sample
4. 再產生 Analytical Sample
5. 紀錄抽樣 metadata（重要）
   - 原始總筆數
   - 每類別抽樣數
   - 抽樣比例
   - random_state
   - 抽樣時間

---

## EDA Workflow on Stratified Samples

### Phase 1 — Representative Sample
- 結構檢查：shape / dtypes / missing / duplicates
- 單變數分布：`amount`, `step`, `type`
- 基礎 target 檢查：`isFraud` 比例
- 輕量關聯：fraud rate by `type`、by step bucket

### Phase 2 — Analytical Sample
- Fraud vs non-fraud 對比圖
  - `amount`（log1p）分布
  - `old/new balance` 變化
  - `deltaOrig`, `deltaDest`
- 風險訊號探索
  - `isFlaggedFraud` 與 `isFraud` 交叉表
  - 不同交易型態下的 fraud rate

### Phase 3 — Full-data Sanity Check
只做低成本驗證：
- 全量 fraud rate
- 全量 `type` 分布
- 全量 step 區間 fraud trend（可用 chunk 聚合）

> 目的：確認抽樣 EDA 結論沒有明顯偏移

---

## Guardrails (避免誤用)

1. 不可用 Analytical Sample 的 fraud rate 當真實發生率
2. 圖表若基於 Analytical Sample，標題需註明「rebalanced sample」
3. 模型最終評估必須在原始分布（validation/test）上
4. 若觀察到時間漂移，抽樣需加入 time-aware 條件（按 step 分層）

---

## Optional Upgrade: Time-aware Stratified Sampling

若要更貼近 production：
- 先把 `step` 分成多個時間桶（例如 10 桶）
- 在每個時間桶內再對 `isFraud` 分層抽樣

這樣可以同時保留：
- 類別比例資訊
- 時間動態資訊

---

## Deliverables

在實作階段應輸出：
- `samples/representative_sample.parquet`
- `samples/analytical_sample.parquet`
- `samples/sampling_metadata.json`

---

## One-line Summary

**先用分層抽樣做「快而穩」的 EDA，再用全量輕量統計回頭驗證，是這份大型且極不平衡詐欺資料最實務的探索流程。**
