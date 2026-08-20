try:
    from .fold_estimator import Estimator as _FoldEstimator
except ImportError:
    from fold_estimator import Estimator as _FoldEstimator


class Estimator(_FoldEstimator):
    n_base = 10_000
