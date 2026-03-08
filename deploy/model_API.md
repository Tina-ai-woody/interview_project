# Model API 實作計畫（FastAPI）

## 目標
將 `baseline_model_revised.ipynb` 的推論流程拆為獨立模型微服務，接收特徵並輸出風險機率與層級。

## 範圍（MVP）
- 使用 baseline 模型（建議先 Logistic Regression）
- 輸入：由 Feature API 產出的欄位
- 輸出：`fraud_prob`, `risk_level`（Low/Medium/High）

## API 設計（MVP）
### 1) Health
- `GET /health`
- 回傳：`{"status":"ok","service":"model-api"}`

### 2) 單筆推論
- `POST /v1/model/predict`
- Request：feature JSON（欄位需與訓練一致）
- Response：
  - `fraud_prob: float`
  - `risk_level: "LOW" | "MEDIUM" | "HIGH"`
  - `thresholds: {"t_mid":0.10,"t_high":0.30}`
  - `model_version`

### 3) 批次推論（可選）
- `POST /v1/model/predict-batch`
- 回傳每筆機率與風險層級

## 風險分層規則（先固定）
- `HIGH`：`p >= t_high`
- `MEDIUM`：`t_mid <= p < t_high`
- `LOW`：`p < t_mid`

建議初始：
- `t_mid = 0.10`
- `t_high = 0.30`

## 專案結構建議
- `deploy/model_api/app/main.py`：FastAPI 入口
- `deploy/model_api/app/schemas.py`：請求/回應 schema
- `deploy/model_api/app/predictor.py`：模型載入 + predict
- `deploy/model_api/models/`：`model.pkl`、`metadata.json`
- `deploy/model_api/requirements.txt`
- `deploy/model_api/Dockerfile`

## 實作重點
1. 啟動時載入模型與欄位清單（feature names）。
2. 驗證輸入欄位完整性與順序。
3. 將 thresholds 放入 config（env 或 yaml），不要寫死。
4. 回傳 `model_version` 方便追蹤。

## 訓練與部署流程（簡化）
1. 從 notebook 抽出訓練腳本（train_baseline.py）。
2. 輸出 `model.pkl` + `feature_columns.json`。
3. Model API 啟動時讀取 artifacts。

## 後續擴充（非 MVP）
- 加入 LightGBM/XGBoost 多模型路由
- 支援模型 A/B test
- 增加解釋欄位（SHAP top features）
