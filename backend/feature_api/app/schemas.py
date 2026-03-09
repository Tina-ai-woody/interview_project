from pydantic import BaseModel, Field
from typing import Literal, List

TxnType = Literal['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER']


class TransactionInput(BaseModel):
    step: int = Field(..., ge=1)
    type: TxnType
    amount: float = Field(..., ge=0)
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    isFlaggedFraud: int = Field(0, ge=0, le=1)


class FeatureOutput(BaseModel):
    step: int
    type: TxnType
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    isFlaggedFraud: int
    deltaOrig: float
    deltaDest: float
    isOrigBalanceZero: int
    isDestBalanceZero: int
    feature_version: str


class BatchTransactionInput(BaseModel):
    items: List[TransactionInput]


class BatchFeatureOutput(BaseModel):
    items: List[FeatureOutput]
