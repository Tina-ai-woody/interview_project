from fastapi import FastAPI

from .schemas import (
    TransactionInput,
    FeatureOutput,
    BatchTransactionInput,
    BatchFeatureOutput,
)
from .transformers import transform_single


app = FastAPI(title='feature-api', version='0.1.0')


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'feature-api'}


@app.post('/v1/features/transform', response_model=FeatureOutput)
def transform(payload: TransactionInput):
    return transform_single(payload)


@app.post('/v1/features/transform-batch', response_model=BatchFeatureOutput)
def transform_batch(payload: BatchTransactionInput):
    return BatchFeatureOutput(items=[transform_single(x) for x in payload.items])
