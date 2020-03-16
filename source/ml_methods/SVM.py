from sklearn.model_selection import RandomizedSearchCV
from sklearn.svm import LinearSVC

from source.ml_methods.SklearnMethod import SklearnMethod


class SVM(SklearnMethod):
    """
    SVM wrapper of the corresponding scikit-learn's LinearSVC method.

    For usage and specification, check :py:obj:`~source.ml_methods.SklearnMethod.SklearnMethod`.
    For valid parameters, see: https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html

    """

    def __init__(self, parameter_grid: dict = None, parameters: dict = None):
        super(SVM, self).__init__()

        self._parameters = parameters if parameters is not None else {"max_iter": 10000, "multi_class": "crammer_singer"}

        if parameter_grid is not None:
            self._parameter_grid = parameter_grid
        else:
            self._parameter_grid = {}

    def _get_ml_model(self, cores_for_training: int = 2):
        params = {**self._parameters, **{}}
        return LinearSVC(**params)

    def _can_predict_proba(self) -> bool:
        return False

    def get_params(self, label):
        params = self.models[label].estimator.get_params() if isinstance(self.models[label], RandomizedSearchCV) \
            else self.models[label].get_params()
        params["coefficients"] = self.models[label].coef_[0].tolist()
        params["intercept"] = self.models[label].intercept_.tolist()
        return params
