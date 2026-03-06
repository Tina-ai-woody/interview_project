# Chunking Strategy for Fraud Detection Dynamics Financial Transaction

## Objective

此資料集（`Transactions Data.csv`）規模大（約 636 萬筆），且具有：
- **強烈類別不平衡**（`isFraud` 極少）
- **時間動態特性**（`step`）
- **帳戶ID高基數**（`nameOrig`, `nameDest`）

因此 chunking 目標是：
1. 在不爆記憶體的情況下穩定處理資料
2. 保留時間順序與時序訊號
3. 避免資料洩漏（data leakage）
4. 對極端不平衡維持可訓練與可評估性

---

## Core Principles

1. **Time-first chunking（優先按時間切塊）**
   - 以 `step` 為主切分，而非純隨機切分。
   - 避免未來資訊進入過去資料。

2. **Boundary-safe feature generation（邊界安全）**
   - 若使用 rolling/window 特徵，需在 chunk 之間保留狀態（state carry-over）。
   - 禁止在全量資料上先聚合再回填（會穿越時間）。

3. **Class-aware processing（類別感知）**
   - 每個訓練 chunk 要監控 fraud 筆數，避免全為負類導致學習失效。
   - 評估時保持原始分布，不做人為重採樣。

4. **ID leakage control（ID 洩漏控制）**
   - `nameOrig`, `nameDest` 若做 encoding，必須以訓練期間統計，不能看見驗證/測試區間。

---

## Recommended Chunking Design

### A. Temporal Split (Dataset-level)

先做全域資料切分（依 `step` 排序後）：
- **Train**: 前 70%
- **Validation**: 中間 15%
- **Test**: 最後 15%

> 若 step 分布不均，可改成按 step 的實際區間切分（例如 step <= T1, T1<T<=T2, >T2）。

### B. In-Train Chunking (Processing-level)

在 Train 區內再切成可處理的小塊：
- 每塊約 **200k ~ 500k rows**（視機器記憶體可調）
- 保持 `step` 單調遞增
- 每個 chunk 記錄：
  - row_count
  - fraud_count
  - fraud_rate
  - step_min / step_max

### C. Stateful Window Strategy (for time features)

若要計算帳戶近期行為特徵（例如過去 N steps 交易數、平均金額）：
- 建立 `state` 字典（key = account id）
- 每個 chunk 開始時讀入前一 chunk 的 state
- chunk 結束後寫回 state
- 僅使用「當前交易之前」的歷史更新特徵

### D. Evaluation Chunking

Validation/Test 不做重採樣，按原始時間順序批次推論：
- 每批 200k~500k
- 計算批次與整體 metrics：PR-AUC、ROC-AUC、Recall、Precision、F1
- 額外監控各 step 區間的 drift（fraud rate 與 score 分布）

---

## Practical Config (Initial)

- `chunk_size`: `300_000`
- `sort_key`: `step`
- `target`: `isFraud`
- `time_split`: `70/15/15`
- `metrics_priority`:
  1. PR-AUC
  2. Recall@Precision>=X
  3. Cost-based threshold metric

---

## Anti-Patterns to Avoid

1. 隨機切分後再做時間特徵（嚴重 leakage）
2. 在全資料上做 target encoding 再切 train/test
3. 只看 Accuracy（在極不平衡資料幾乎沒有意義）
4. 每個 chunk 獨立標準化但使用全域未分期統計

---

## Deliverables Plan (Next Steps)

1. 實作 `chunk_loader.py`：時間排序 + chunk iterator
2. 實作 `feature_state.py`：跨 chunk 狀態保存
3. 實作 `train_baseline.py`：chunk-by-chunk 訓練/評估
4. 實作 `eval_report.md`：按時間區間輸出指標與閾值建議

---

## One-line Summary

**此資料集應採用「時間優先 + 狀態延續 + 類別不平衡感知」的 chunking strategy，才能在大規模與高風險詐欺場景下得到可信且可落地的模型結果。**
