# Frontend（Nuxt）實作計畫

## 目標
建立一個簡單 Nuxt 前端頁面：
1. 使用者輸入交易欄位
2. 呼叫 Feature API 產生特徵
3. 再呼叫 Model API 取得預測
4. 顯示 `fraud_prob` 與 `risk_level`

## MVP 功能
- 單頁表單（Transaction Input）
- 按下「預測」後依序呼叫：
  - `POST feature-api /v1/features/transform`
  - `POST model-api /v1/model/predict`
- 結果卡片顯示：
  - Fraud Probability
  - Risk Level（Low/Medium/High）
  - 使用 thresholds（t_mid, t_high）

## 欄位（先對齊 baseline）
- `step` (number)
- `type` (select: CASH_IN / CASH_OUT / DEBIT / PAYMENT / TRANSFER)
- `amount` (number)
- `oldbalanceOrg` (number)
- `newbalanceOrig` (number)
- `oldbalanceDest` (number)
- `newbalanceDest` (number)
- `isFlaggedFraud` (0/1)

## Nuxt 專案結構建議
- `deploy/frontend/`
  - `pages/index.vue`（主頁）
  - `components/TransactionForm.vue`
  - `components/PredictionCard.vue`
  - `server/api/`（可選：代理後端）
  - `.env`（API base URL）

## 介面流程
1. 使用者填寫交易資料
2. 前端呼叫 Feature API，得到 feature payload
3. 前端呼叫 Model API，得到 `fraud_prob` / `risk_level`
4. 顯示結果與錯誤訊息（若 API 失敗）

## 環境變數
- `NUXT_PUBLIC_FEATURE_API_BASE=http://localhost:8001`
- `NUXT_PUBLIC_MODEL_API_BASE=http://localhost:8002`

## 前後端串接範例（流程）
- `transformResp = await $fetch(featureApi + '/v1/features/transform', {method:'POST', body: form})`
- `predictResp = await $fetch(modelApi + '/v1/model/predict', {method:'POST', body: transformResp})`

## 顯示規則（建議）
- `HIGH`：紅色警示
- `MEDIUM`：橘色提醒
- `LOW`：綠色通過

## 後續擴充（非 MVP）
- 批次上傳 CSV 推論
- 查詢歷史預測紀錄
- 加入案例標記（Case Management）入口
