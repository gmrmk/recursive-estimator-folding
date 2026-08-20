try:
    from .base_estimator import Estimator as _BaseEstimator
    from .replicated_fold_estimator import Estimator as _ReplicatedEstimator
except ImportError:
    from base_estimator import Estimator as _BaseEstimator
    from replicated_fold_estimator import Estimator as _ReplicatedEstimator


class Estimator(_ReplicatedEstimator):
    """Four digital-shift replicates without the late folding experiment."""

    n_base = 14_000
    n_replicates = 4
    predict = _BaseEstimator.predict
