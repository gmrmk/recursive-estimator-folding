try:
    from .base_estimator import Estimator as _BaseEstimator
except ImportError:
    from base_estimator import Estimator as _BaseEstimator


class Estimator(_BaseEstimator):
    n_base = 4_200
