from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict


MODEL_VERSION = os.getenv('MODEL_VERSION', 'baseline_logit_v1')
T_MID = float(os.getenv('T_MID', '0.10'))
T_HIGH = float(os.getenv('T_HIGH', '0.30'))

MODEL_DIR = Path(__file__).resolve().parents[1] / 'models'
METADATA_PATH = MODEL_DIR / 'metadata.json'


def load_metadata() -> Dict:
    if METADATA_PATH.exists():
        return json.loads(METADATA_PATH.read_text(encoding='utf-8'))
    return {
        'note': 'No trained artifact found. Using heuristic fallback scorer.',
        'features': [
            'step', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest',
            'deltaOrig', 'deltaDest', 'isOrigBalanceZero', 'isDestBalanceZero', 'isFlaggedFraud', 'type'
        ]
    }


def _sigmoid(x: float) -> float:
    import math
    return 1.0 / (1.0 + math.exp(-x))


def fallback_score(features: Dict) -> float:
    """
    MVP fallback: heuristic score aligned with baseline intuition.
    後續可替換為 joblib 載入訓練好的 pipeline.
    """
    amount = float(features.get('amount', 0.0))
    delta_orig = float(features.get('deltaOrig', 0.0))
    delta_dest = float(features.get('deltaDest', 0.0))
    flagged = int(features.get('isFlaggedFraud', 0))
    tx_type = str(features.get('type', ''))

    z = -6.5
    z += 0.000003 * amount
    z += 0.000002 * max(delta_orig, 0.0)
    z += 0.000002 * max(delta_dest, 0.0)
    z += 2.0 * flagged
    if tx_type in {'TRANSFER', 'CASH_OUT'}:
        z += 0.6

    return max(0.0, min(1.0, _sigmoid(z)))


def risk_level(prob: float) -> str:
    if prob >= T_HIGH:
        return 'HIGH'
    if prob >= T_MID:
        return 'MEDIUM'
    return 'LOW'
