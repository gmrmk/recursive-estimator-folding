try:
    from .replicated_fold_estimator import Estimator as _ReplicatedEstimator
except ImportError:
    from replicated_fold_estimator import Estimator as _ReplicatedEstimator


class Estimator(_ReplicatedEstimator):
    n_base = 10_000
    n_replicates = 4
