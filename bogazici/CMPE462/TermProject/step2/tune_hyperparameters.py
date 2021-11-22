from preprocessing import read_data, convert_to_df, calculate_bow, calculate_tf_idf, encode_target_classes, \
    preprocessing
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier


def tune_svm(train, val, y_train, y_val):
    # Parameters to try
    c_list = [0.05, 0.1, 1, 50, 100]
    k_list = ['rbf', 'poly', 'sigmoid', 'linear']
    g_list = [1, 0.1, 0.01, 0.001]
    max_accur = 0
    best = []
    for c in c_list:
        for k in k_list:
            for g in g_list:
                # SVM is trained
                svm_cls = SVC(C=c, degree=3, gamma=g, kernel=k)
                svm_cls.fit(train, y_train)
                accur = accuracy_score(y_val, svm_cls.predict(val))

                # Print best score until now
                if accur > max_accur:
                    max_accur = accur
                    print(max_accur)
                    best = [c, k, g]
                    print(best)


def tune_RF(train, val, y_train, y_val):
    # Parameters to try
    n_estimators = [100, 300, 500, 800, 1200]
    max_depth = [5, 8, 15, 25, 30]
    min_samples_split = [2, 5, 10, 15, 100]
    min_samples_leaf = [1, 2, 5, 10]
    max_accur = 0
    for n in n_estimators:
        for md in max_depth:
            for mss in min_samples_split:
                for msl in min_samples_leaf:
                    # RFis trained
                    random_forest_cls = RandomForestClassifier(n_estimators=n, max_depth=md, min_samples_leaf=msl,
                                                               min_samples_split=mss)
                    random_forest_cls.fit(train, y_train)
                    accur = accuracy_score(y_val, random_forest_cls.predict(val))

                    # Print best score until now
                    if accur > max_accur:
                        max_accur = accur
                        print("Train Accuracy:\n", accuracy_score(y_train, random_forest_cls.predict(train)))
                        print("Validation Accuracy:\n", accur)
                        print([n, md, mss, msl])


if __name__ == "__main__":
    train_path = "TRAIN"
    val_path = "VAL"

    # Read the Data
    train_data, val_data = read_data(train_path, val_path)
    # Convert it to DataFrame
    train_df, val_df = convert_to_df(train_data, val_data)
    y_train, y_val = encode_target_classes(train_df, val_df)
    preprocessing(train_df, val_df)
    # Calculate Features
    train_tf_idf, val_tf_idf = calculate_tf_idf(train_df, val_df)
    train_bow, val_bow = calculate_bow(train_df, val_df)

    tune_svm(train_tf_idf, val_tf_idf, y_train, y_val)
    tune_svm(train_bow, val_bow, y_train, y_val)

    tune_RF(train_tf_idf, val_tf_idf, y_train, y_val)
    tune_RF(train_bow, val_bow, y_train, y_val)
