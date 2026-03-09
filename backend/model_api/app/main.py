from fastapi import FastAPI

from .schemas import (
    FeatureInput,
    PredictResponse,
    BatchFeatureInput,
    BatchPredictResponse,
)
from .predictor import (
    MODEL_VERSION,
    T_MID,
    T_HIGH,
    load_metadata,
    fallback_score,
    risk_level,
)


app = FastAPI(title='model-api', version='0.1.0')
metadata = load_metadata()


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'service': 'model-api',
        'model_version': MODEL_VERSION,
        'metadata': metadata,
    }


@app.post('/v1/model/predict', response_model=PredictResponse)
def predict(payload: FeatureInput):
    prob = fallback_score(payload.model_dump())
    return PredictResponse(
        fraud_prob=prob,
        risk_level=risk_level(prob),
        thresholds={'t_mid': T_MID, 't_high': T_HIGH},
        model_version=MODEL_VERSION,
    )


@app.post('/v1/model/predict-batch', response_model=BatchPredictResponse)
def predict_batch(payload: BatchFeatureInput):
    items = []
    for row in payload.items:
        prob = fallback_score(row.model_dump())
        items.append(
            PredictResponse(
                fraud_prob=prob,
                risk_level=risk_level(prob),
                thresholds={'t_mid': T_MID, 't_high': T_HIGH},
                model_version=MODEL_VERSION,
            )
        )
    return BatchPredictResponse(items=items)
