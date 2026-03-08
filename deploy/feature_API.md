# Feature API 實作計畫（FastAPI）

## 目標
把 `baseline_model_revised.ipynb` 的特徵工程邏輯拆成獨立微服務，供前端或模型服務呼叫。

## 範圍（對齊 baseline notebook）
- baseline 特徵：
  - `step`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `type`, `isFlaggedFraud`
- 衍生特徵：
  - `deltaOrig = oldbalanceOrg - newbalanceOrig`
  - `deltaDest = newbalanceDest - oldbalanceDest`
  - `isOrigBalanceZero = int(oldbalanceOrg == 0)`
  - `isDestBalanceZero = int(oldbalanceDest == 0)`
- 預留 SNA/account-SNA 欄位（先不做 stateful online 計算，MVP 先保留擴充接口）

## API 設計（MVP）
### 1) Health
- `GET /health`
- 回傳：`{"status":"ok","service":"feature-api"}`

### 2) 單筆特徵轉換
- `POST /v1/features/transform`
- Request（原始交易）：
  - `step`, `type`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `isFlaggedFraud`
- Response（模型輸入欄位）：
  - 上述 baseline 欄位 + `deltaOrig`, `deltaDest`, `isOrigBalanceZero`, `isDestBalanceZero`

### 3) 批次特徵轉換（可選）
- `POST /v1/features/transform-batch`
- Request: `[{...}, {...}]`
- Response: `[{...}, {...}]`

## 專案結構建議
- `deploy/feature_api/app/main.py`：FastAPI 入口
- `deploy/feature_api/app/schemas.py`：Pydantic 請求/回應 schema
- `deploy/feature_api/app/transformers.py`：特徵轉換函式
- `deploy/feature_api/requirements.txt`
- `deploy/feature_api/Dockerfile`

## 實作重點
1. 使用 Pydantic 驗證輸入型別與必要欄位。
2. 特徵欄位順序固定，避免 model service 對不上。
3. 回應包含 `feature_version`（例如 `baseline_v1`）便於追蹤。
4. 若未提供 `isFlaggedFraud`，MVP 預設 0（或由 config 決定）。

## 與 Model API 串接
- Frontend 呼叫 feature API
- feature API 回傳特徵 JSON
- 前端再把特徵 JSON 傳給 model API（簡化串接）

## 後續擴充（非 MVP）
- 加入 state store（Redis）後實作 SNA/account-SNA 線上特徵
- 增加 `/v1/features/with-sna` 端點（只看過去資料）
- 支援 Kafka consumer 模式
