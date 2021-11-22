"""
    In this Script all models other than our best model is trained
    For each model accuracy, classification report and confusion matrix
"""
from preprocessing import read_data, convert_to_df, calculate_tf_idf, calculate_bow, encode_target_classes, \
    feature_selection, nb_svm_features, preprocessing

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd
import numpy as np


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
    plt.plot()


if __name__ == "__main__":
    train_path = "TRAIN"
    val_path = "VAL"

    # Read the Data
    train_data, val_data = read_data(train_path, val_path)
    # Convert it to DataFrame
    train_df, val_df = convert_to_df(train_data, val_data)
    # Preprocess the Data
    train_df, val_df = preprocessing(train_df, val_df)

    # Calculate Train and Validation Features
    train_tf_idf, val_tf_idf, _, _ = calculate_tf_idf(train_df, val_df)
    train_bow, val_bow, _, _ = calculate_bow(train_df, val_df)
    y_train, y_val = encode_target_classes(train_df, val_df)
    # Apply Feature Selection on BOW Model
    feature_trans = feature_selection(train_bow, y_train)
    train_fs_bow = feature_trans.transform(train_bow)
    val_fs_bow = feature_trans.transform(val_bow)

    # Train the Best Version of Each Classifier and Report its Performance Metrics
    ###################################
    # Naive Bayes
    from sklearn.naive_bayes import MultinomialNB

    print("Naive Bayes Model", end="\n")
    # Train the model
    nb_clf = MultinomialNB()
    nb_clf.fit(train_bow, y_train)

    # Print Performance Metrics
    print("Train Accuracy:\n", accuracy_score(y_train, nb_clf.predict(train_bow)))
    print("Validation Accuracy:\n", accuracy_score(y_val, nb_clf.predict(val_bow)))

    print("Train Report:\n", classification_report(y_train, nb_clf.predict(train_bow)))
    print("Validation Report:\n", classification_report(y_val, nb_clf.predict(val_bow)))

    plot_confusion_matrix(confusion_matrix(y_train, nb_clf.predict(train_bow)),
                          confusion_matrix(y_val, nb_clf.predict(val_bow)))
    plt.show()

    ###################################
    # Support Vector Machine
    from sklearn.svm import SVC

    print("Support Vector Machine", end="\n")
    # Train the model
    svm_cls = SVC(C=1, degree=3, gamma=1, kernel="linear")
    svm_cls.fit(train_tf_idf, y_train)

    # Print Performance Metrics
    print("Train Accuracy:\n", accuracy_score(y_train, svm_cls.predict(train_tf_idf)))
    print("Validation Accuracy:\n", accuracy_score(y_val, svm_cls.predict(val_tf_idf)))

    print("Train Report:\n", classification_report(y_train, svm_cls.predict(train_tf_idf)))
    print("Validation Report:\n", classification_report(y_val, svm_cls.predict(val_tf_idf)))

    plot_confusion_matrix(confusion_matrix(y_train, svm_cls.predict(train_tf_idf)),
                          confusion_matrix(y_val, svm_cls.predict(val_tf_idf)))
    plt.show()

    ###################################
    # Random Forest
    from sklearn.ensemble import RandomForestClassifier

    print("Random Forest", end="\n")
    # Train the model
    random_forest_cls = RandomForestClassifier(n_estimators=1200, max_depth=25, min_samples_leaf=15,
                                               min_samples_split=2)
    random_forest_cls.fit(train_bow, y_train)

    # Print Performance Metrics
    print("Train Accuracy:\n", accuracy_score(y_train, random_forest_cls.predict(train_bow)))
    print("Validation Accuracy:\n", accuracy_score(y_val, random_forest_cls.predict(val_bow)))

    print("Train Report:\n", classification_report(y_train, random_forest_cls.predict(train_bow)))
    print("Validation Report:\n", classification_report(y_val, random_forest_cls.predict(val_bow)))

    plot_confusion_matrix(confusion_matrix(y_train, random_forest_cls.predict(train_bow)),
                          confusion_matrix(y_val, random_forest_cls.predict(val_bow)))
    plt.show()

    ###################################
    # XGBoost
    import xgboost as xgb

    print("XGBoost", end="\n")
    # Train the model
    xgbcls = xgb.XGBClassifier(gamma=1, min_child_weight=3, max_depth=10, n_estimators=2500, learning_rate=0.01,
                               subsample=0.8, colsample_bytree=0.4, nthread=8, verbosity=0, reg_alpha=1,
                               objective="merror")
    xgbcls.fit(train_bow, y_train, eval_set=[(train_bow, y_train), (val_bow, y_val)], early_stopping_rounds=100,
               eval_metric="merror", verbose=True)

    # Print Performance Metrics
    print("Train Accuracy:\n", accuracy_score(y_train, xgbcls.predict(train_bow)))
    print("Validation Accuracy:\n", accuracy_score(y_val, xgbcls.predict(val_bow)))

    print("Train Report:\n", classification_report(y_train, xgbcls.predict(train_bow)))
    print("Validation Report:\n", classification_report(y_val, xgbcls.predict(val_bow)))

    plot_confusion_matrix(confusion_matrix(y_train, xgbcls.predict(train_bow)),
                          confusion_matrix(y_val, xgbcls.predict(val_bow)))
    plt.show()

    ###################################
    # LightGBM
    import lightgbm as lgb

    print("LightGBM", end="\n")
    # Train the model
    params = {"objective": 'multiclass', "metric": 'multi_logloss', "num_class": 3, "learning_rate": 0.05,
              "max_bin": 300}
    num_rounds = 1000
    lgb_model = lgb.train(params, lgb.Dataset(train_bow.toarray(), label=y_train.ravel()), num_rounds,
                          valid_sets=[lgb.Dataset(train_bow.toarray(), label=y_train.ravel()),
                                      lgb.Dataset(val_bow.toarray(), label=y_val.ravel())], early_stopping_rounds=200,
                          verbose_eval=100)

    # Print Performance Metrics
    print("Train Accuracy:\n", accuracy_score(y_train, np.argmax(lgb_model.predict(train_bow.toarray()), 1)))
    print("Validation Accuracy:\n", accuracy_score(y_val, np.argmax(lgb_model.predict(val_bow.toarray()), 1)))

    print("Train Report:\n", classification_report(y_train, np.argmax(lgb_model.predict(train_bow.toarray()), 1)))
    print("Validation Report:\n", classification_report(y_val, np.argmax(lgb_model.predict(val_bow.toarray()), 1)))

    plot_confusion_matrix(confusion_matrix(y_train, np.argmax(lgb_model.predict(train_bow.toarray()), 1)),
                          confusion_matrix(y_val, np.argmax(lgb_model.predict(val_bow.toarray()), 1)))
    plt.show()

    # Try Ensamble with NBSVM (Our Best Model)
    from sklearn.ensemble import BaggingClassifier
    from main_model import NBSVM

    print("Ensemble Model with NBSVM", end="\n")
    X_train, X_val, _ = nb_svm_features(train_bow, val_bow, train_df, val_df)
    # Train the model
    ensemble = BaggingClassifier(
        base_estimator=NBSVM(
            alpha=1,
            C=0.005,
            beta=0.35,
            fit_intercept=True,
            max_iter=100000,
            tol=1e-4,
            intercept_scaling=5.0,
            class_weights={0: "balanced", 1: "balanced", 2: "balanced"},
            dual=True),
        n_estimators=20,
        max_features=0.8,
        bootstrap_features=False,
        oob_score=False,
        warm_start=True,
    )
    ensemble.fit(X_train, y_train)

    # Print Performance Metrics
    print("Train Accuracy:\n", accuracy_score(y_train, ensemble.predict(X_train)))
    print("Validation Accuracy:\n", accuracy_score(y_val, ensemble.predict(X_val)))

    print("Train Report:\n", classification_report(y_train, ensemble.predict(X_train)))
    print("Validation Report:\n", classification_report(y_val, ensemble.predict(X_val)))

    plot_confusion_matrix(confusion_matrix(y_train, ensemble.predict(X_train)),
                          confusion_matrix(y_val, ensemble.predict(X_val)))
    plt.show()
