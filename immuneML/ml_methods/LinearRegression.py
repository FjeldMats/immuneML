from pathlib import Path
from sklearn.metrics import SCORERS
from sklearn.linear_model import LinearRegression as SklearnLinearRegression

from sklearn.model_selection import GridSearchCV
from immuneML.data_model.encoded_data.EncodedData import EncodedData
from immuneML.ml_methods.SklearnMethod import SklearnMethod


class LinearRegression(SklearnMethod):
    """
    This is a wrapper of scikit-learn’s LinearRegression class. Please see the
    `scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html>`_
    of LinearRegression for the parameters.

    Note: if you are interested in plotting the coefficients of the logistic regression model,
    consider running the :ref:`Coefficients` report.

    For usage instructions, check :py:obj:`~immuneML.ml_methods.SklearnMethod.SklearnMethod`.


    YAML specification:

    .. indent with spaces
    .. code-block:: yaml

        my_logistic_regression: # user-defined method name
            LinearRegression: # name of the ML method
                # sklearn parameters (same names as in original sklearn class)
                penalty: l1 # always use penalty l1
                C: [0.01, 0.1, 1, 10, 100] # find the optimal value for C
                # Additional parameter that determines whether to print convergence warnings
                show_warnings: True
            # if any of the parameters under LinearRegression is a list and model_selection_cv is True,
            # a grid search will be done over the given parameters, using the number of folds specified in model_selection_n_folds,
            # and the optimal model will be selected
            model_selection_cv: True
            model_selection_n_folds: 5
        # alternative way to define ML method with default values:
        my_default_logistic_regression: LinearRegression

    """
    default_parameters = {'fit_intercept': True, 'normalize': True}

    def __init__(self, parameter_grid: dict = None, parameters: dict = None):
        parameters = {**self.default_parameters, **(parameters if parameters is not None else {})}

        if parameter_grid is not None:
            parameter_grid = parameter_grid
        else:
            parameter_grid = {'fit_intercept': [True], 'normalize': [True]}

        super(LinearRegression, self).__init__(parameter_grid=parameter_grid, parameters=parameters)

    def _get_ml_model(self, cores_for_training: int = 2, X=None):
        params = self._parameters.copy()
        params["n_jobs"] = cores_for_training
        return SklearnLinearRegression(**params)

    def can_predict_proba(self) -> bool:
        return False

    def get_params(self):
        params = self.model.get_params()
        params["coefficients"] = self.model.coef_.tolist()
        params["intercept"] = self.model.intercept_.tolist()
        return params

    def predict(self, encoded_data: EncodedData, label_name: str):
        return {label_name: self.model.predict(encoded_data.examples)}

    def store(self, path: Path, feature_names=None, details_path: Path = None):
        return

    def fit_by_cross_validation(self, encoded_data: EncodedData, number_of_splits: int = 5, label_name: str = None, cores_for_training: int = -1,
                                optimization_metric='r2'):

        self.class_mapping = {}
        self.feature_names = encoded_data.feature_names
        self.label_name = label_name

        self.model = self._fit_by_cross_validation(encoded_data.examples, encoded_data.labels[label_name], number_of_splits, label_name, cores_for_training,
                                                   optimization_metric)

    def _fit_by_cross_validation(self, X, y, number_of_splits: int = 5, label_name: str = None, cores_for_training: int = 1,
                                 optimization_metric: str = "balanced_accuracy"):

        model = self._get_ml_model()
        scoring = optimization_metric

        if optimization_metric not in SCORERS.keys():
            scoring = "balanced_accuracy"
            warnings.warn(
                f"{self.__class__.__name__}: specified optimization metric ({optimization_metric}) is not defined as a sklearn scoring function, using {scoring} instead... ")

        if not self.show_warnings:
            warnings.simplefilter("ignore")
            os.environ["PYTHONWARNINGS"] = "ignore"

        self.model = GridSearchCV(model, param_grid=self._parameter_grid, cv=number_of_splits, n_jobs=cores_for_training,
                                  scoring=scoring, refit=True)
        self.model.fit(X, y)

        if not self.show_warnings:
            del os.environ["PYTHONWARNINGS"]
            warnings.simplefilter("always")

        self.model = self.model.best_estimator_  # do not leave RandomSearchCV object to be in models, use the best estimator instead

        return self.model

