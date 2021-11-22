# Implementation of NBSVM 
# This implementation is taken from https://github.com/prakhar-agarwal/Naive-Bayes-SVM
from scipy.sparse import spmatrix, coo_matrix
from sklearn.base import BaseEstimator
from sklearn.linear_model.base import LinearClassifierMixin, SparseCoefMixin
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import RFECV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from preprocessing import read_data, convert_to_df, calculate_bow, encode_target_classes, preprocessing, nb_svm_features
import matplotlib.pyplot as plt
import seaborn as sn
import pickle
import pandas as pd
import numpy as np


class NBSVM(BaseEstimator, LinearClassifierMixin, SparseCoefMixin):

    def __init__(self, alpha=1, C=1, beta=0.25, fit_intercept=False, max_iter=1000, tol=1e-4, intercept_scaling=1.0,
                 class_weights=None, dual=False):
        self.alpha = alpha
        self.C = C
        self.beta = beta
        self.fit_intercept = fit_intercept
        self.max_iter = max_iter
        self.tol = tol
        self.intercept_scaling = intercept_scaling
        self.class_weights = class_weights
        self.dual = dual

    def fit(self, X, y):
        self.classes_ = np.unique(y)

        if len(self.classes_) == 2:
            coef_, intercept_ = self._fit_binary(X, y, self.classes_[0])
            self.coef_ = coef_
            self.intercept_ = intercept_
        else:
            coef_, intercept_ = zip(*[
                self._fit_binary(X, y == class_, class_)
                for class_ in self.classes_
            ])
            self.coef_ = np.concatenate(coef_)
            self.intercept_ = np.array(intercept_).flatten()
        return self

    def _fit_binary(self, X, y, class_):
        p = np.asarray(self.alpha + X[y == 1].sum(axis=0)).flatten()
        q = np.asarray(self.alpha + X[y == 0].sum(axis=0)).flatten()
        r = np.log(p / np.abs(p).sum()) - np.log(q / np.abs(q).sum())
        b = np.log((y == 1).sum()) - np.log((y == 0).sum())

        if isinstance(X, spmatrix):
            indices = np.arange(len(r))
            r_sparse = coo_matrix(
                (r, (indices, indices)),
                shape=(len(r), len(r))
            )
            X_scaled = X * r_sparse
        else:
            X_scaled = X * r

        lsvc = LinearSVC(
            C=self.C,
            fit_intercept=self.fit_intercept,
            max_iter=self.max_iter,
            tol=self.tol,
            intercept_scaling=self.intercept_scaling,
            class_weight=self.class_weights[class_],
            dual=self.dual

        ).fit(X_scaled, y)
        mean_mag = np.abs(lsvc.coef_).mean()
        coef_ = (1 - self.beta) * mean_mag * r + self.beta * (r * lsvc.coef_)

        intercept_ = (1 - self.beta) * mean_mag * b + self.beta * lsvc.intercept_

        return coef_, intercept_


def plot_confusion_matrix(confusion_matrix_train, confusion_matrix_val):
    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)

    df_cm = pd.DataFrame(confusion_matrix_train.T, index=[i for i in "NZP"],
                         columns=[i for i in "NZP"])
    sn.heatmap(df_cm, annot=True, fmt='g')
    plt.xlabel("true class")
    plt.ylabel("predicted class")

    plt.subplot(1, 2, 2)

    df_cm = pd.DataFrame(confusion_matrix_val.T, index=[i for i in "NZP"],
                         columns=[i for i in "NZP"])
    sn.heatmap(df_cm, annot=True, fmt='g')
    plt.xlabel("true class")
    plt.ylabel("predicted class")
    plt.show()


if __name__ == "__main__":
    train_path = "TRAIN"
    val_path = "VAL"

    # Read the Data
    train_data, val_data = read_data(train_path, val_path)
    # Convert it to DataFrame
    train_df, val_df = convert_to_df(train_data, val_data)
    # Preprocess the Data
    train_df, val_df = preprocessing(train_df, val_df)
    y_train, y_val = encode_target_classes(train_df, val_df)

    # Calculate Features
    train_bow, val_bow, bow_title, bow_body = calculate_bow(train_df, val_df)

    X_train, X_val, x_train_mean = nb_svm_features(train_bow, val_bow, train_df, val_df)

    # Make Feature Selection via Recursive Feature Elimination with Cross Validation
    nbsvm = NBSVM(alpha=1, C=0.001, beta=0.10, fit_intercept=True, max_iter=100000, tol=1e-4, intercept_scaling=15.0,
                  class_weights={0: "balanced", 1: "balanced", 2: "balanced"}, dual=True)
    rfecv = RFECV(estimator=nbsvm, step=200, cv=StratifiedKFold(5),
                  scoring='accuracy',
                  min_features_to_select=2000)

    rfecv.fit(X_train, y_train)

    # Train the main model
    nbsvm = NBSVM(alpha=1, C=0.005, beta=0.35, fit_intercept=True, max_iter=100000, tol=1e-4, intercept_scaling=5.0,
                  class_weights={0: "balanced", 1: "balanced", 2: "balanced"}, dual=True)
    nbsvm.fit(rfecv.transform(X_train), y_train)

    # Print Performance Metrics
    print("Train Accuracy:\n", accuracy_score(y_train, nbsvm.predict(rfecv.transform(X_train))))
    print("Validation Accuracy:\n", accuracy_score(y_val, nbsvm.predict(rfecv.transform(X_val))))

    print("Train Report:\n", classification_report(y_train, nbsvm.predict(rfecv.transform(X_train))))
    print("Validation Report:\n", classification_report(y_val, nbsvm.predict(rfecv.transform(X_val))))

    plot_confusion_matrix(confusion_matrix(y_train, nbsvm.predict(rfecv.transform(X_train))),
                          confusion_matrix(y_val, nbsvm.predict(rfecv.transform(X_val))))

    object_list = [nbsvm, rfecv, x_train_mean, bow_title, bow_body]
    pickle.dump(object_list, open("step2_model_NoName.pkl", "wb"))
