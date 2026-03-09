# Backend Services (FastAPI MVP)

## Services
- `feature_api`: 對齊 `baseline_model_revised.ipynb` 的 baseline 特徵轉換
- `model_api`: 接收特徵後輸出 `fraud_prob` 與 `risk_level`

## Run (feature api)
```bash
cd backend/feature_api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## Run (model api)
```bash
cd backend/model_api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

## Endpoints
### feature-api
- `GET /health`
- `POST /v1/features/transform`
- `POST /v1/features/transform-batch`

### model-api
- `GET /health`
- `POST /v1/model/predict`
- `POST /v1/model/predict-batch`

## Notes
目前 model-api 使用 heuristic fallback scorer（MVP）以便先串接整體流程。
下一步可把 notebook 訓練產出的模型 artifacts（model.pkl + feature schema）接入。
