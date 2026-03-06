# Fraud Detection Dynamics Financial Transaction — Data Summary

來源：
- Kaggle: https://www.kaggle.com/datasets/rohit265/fraud-detection-dynamics-financial-transaction/data

## 下載與檔案狀態

已下載到目前專案資料夾：
- `fraud-detection-dynamics-financial-transaction.zip`
- `Transactions Data.csv`

## 我對資料集的理解

這是一個**金融交易詐欺偵測**資料集，資料以交易事件為單位，每筆資料包含：
- 交易時間步（`step`）
- 交易類型（`type`）
- 交易金額（`amount`）
- 交易前後餘額（`oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`）
- 來源與目的帳戶識別（`nameOrig`, `nameDest`）
- 詐欺標籤（`isFraud`）
- 高風險標記（`isFlaggedFraud`）

### 結構與規模（實際掃描結果）
- 總筆數：`6,362,620`
- 欄位數：`11`
- 欄位列表：
  - `step`
  - `type`
  - `amount`
  - `nameOrig`
  - `oldbalanceOrg`
  - `newbalanceOrig`
  - `nameDest`
  - `oldbalanceDest`
  - `newbalanceDest`
  - `isFraud`
  - `isFlaggedFraud`

### 目標欄位與分布
- 目標欄位：`isFraud`
- 正類比例（fraud rate）：約 `0.129%`（~0.00129）

> 這代表資料是**高度不平衡**（extreme class imbalance），在建模時不能只看 Accuracy，應重點看 PR-AUC、Recall、Precision、F1 與成本敏感閾值。

### 型別與缺失值（抽樣掃描）
- 推斷型別：
  - 數值：`step`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `isFraud`, `isFlaggedFraud`
  - 類別字串：`type`, `nameOrig`, `nameDest`
- 前 200k 筆抽樣中未觀察到空值（建議完整 EDA 時再做全量確認）

## 建模/EDA上的重點建議

1. **先做時間切分（time-based split）**
   - 例如用 `step` 做 train/valid/test，避免隨機切分造成資料洩漏。

2. **處理類別不平衡**
   - 可使用 class weight、欠採樣/過採樣、或 focal loss（若用深度學習）。
   - 指標以 PR-AUC、Recall@Precision、成本函數為主。

3. **特徵工程方向**
   - 餘額變化：
     - `deltaOrig = oldbalanceOrg - newbalanceOrig`
     - `deltaDest = newbalanceDest - oldbalanceDest`
   - 交易模式：`type` one-hot / target encoding
   - 時序統計：帳戶在近期窗口內交易頻率、累積金額、異常峰值。

4. **風險與限制**
   - `nameOrig`, `nameDest` 是高基數ID，直接餵模型可能過擬合，需謹慎編碼。
   - 若資料為模擬/特定場景，模型外推到真實環境時需再驗證。

## 一句話總結

這個資料集很適合做「**極度不平衡 + 交易時序**」的詐欺偵測面試題，重點在於：
- 正確的切分策略
- 合理的評估指標
- 可解釋的風險特徵工程
