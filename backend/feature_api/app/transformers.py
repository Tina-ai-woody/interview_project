from .schemas import TransactionInput, FeatureOutput


FEATURE_VERSION = 'baseline_v1'


def transform_single(txn: TransactionInput) -> FeatureOutput:
    delta_orig = txn.oldbalanceOrg - txn.newbalanceOrig
    delta_dest = txn.newbalanceDest - txn.oldbalanceDest
    is_orig_zero = int(txn.oldbalanceOrg == 0)
    is_dest_zero = int(txn.oldbalanceDest == 0)

    return FeatureOutput(
        step=txn.step,
        type=txn.type,
        amount=txn.amount,
        oldbalanceOrg=txn.oldbalanceOrg,
        newbalanceOrig=txn.newbalanceOrig,
        oldbalanceDest=txn.oldbalanceDest,
        newbalanceDest=txn.newbalanceDest,
        isFlaggedFraud=txn.isFlaggedFraud,
        deltaOrig=delta_orig,
        deltaDest=delta_dest,
        isOrigBalanceZero=is_orig_zero,
        isDestBalanceZero=is_dest_zero,
        feature_version=FEATURE_VERSION,
    )
