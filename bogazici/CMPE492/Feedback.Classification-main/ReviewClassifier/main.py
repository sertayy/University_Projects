import sys
import pandas as pd
import numpy as np
from pandas import DataFrame
from simpletransformers.classification import ClassificationModel
import sklearn
from sklearn import metrics
import os
import seaborn as sn
import matplotlib.pyplot as plt
from read_helper import get_data_from_bigquery, read_json, read_config, read_csv
from preprocess_data import apply_preprocess
import logging
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
K_FOLD = 5
DB_TYPE = "bigQuery"


def create_confisuon_matrix(conf_matrix):
    df_cm = pd.DataFrame(conf_matrix, index=[i for i in "BFRU"],
                         columns=[i for i in "BFRU"])
    plt.figure(figsize=(10, 7))
    sn.heatmap(df_cm, annot=True, fmt='g')
    plt.xlabel("true class")
    plt.ylabel("predicted class")
    plt.savefig('confusion_matrix.png')


def create_model():
    model_args = {
        "use_early_stopping": True,
        "early_stopping_delta": 0.01,
        "early_stopping_metric": "mcc",
        "early_stopping_metric_minimize": False,
        "early_stopping_patience": 5,
        "evaluate_during_training_steps": 1000,
        "fp16": False,
        "num_train_epochs": 3
    }

    model = ClassificationModel(
        "bert",
        "dbmdz/bert-base-turkish-cased",
        use_cuda=True,
        args=model_args,
        num_labels=4
    )
    return model


def train_model(df, k_fold_step):
    model = create_model()
    model.train_model(df, acc=sklearn.metrics.accuracy_score, output_dir="model_{0}".format(k_fold_step))
    return model


def test_model(trained_model, test_df):
    pred_matrix = np.zeros((4,4))
    for index, row in test_df.iterrows():
        predictions = trained_model.predict(row["text"])[0]
        pred_matrix[row["labels"]][predictions[0]] += 1
    return pred_matrix


def k_fold(df: pd.DataFrame):
    categories = df['labels'].unique()
    test_df = pd.DataFrame(columns=df.columns)
    train_df = pd.DataFrame(columns=df.columns)
    pred_matrix = np.zeros((4, 4))
    for i in range(K_FOLD):
        for category in categories:
            categ_df = df[df['labels'] == category]
            categ_values = categ_df.values
            piece = int(len(categ_values) / K_FOLD)
            training = np.concatenate((categ_values[:len(categ_values) - piece * (i + 1), :], categ_values[len(categ_values) - piece * i:, :]))
            test = categ_values[len(categ_values) - piece * (i + 1):len(categ_values) - piece * i, :]
            train_df = train_df.append(DataFrame(training, columns=categ_df.columns), ignore_index=True)
            test_df = test_df.append(DataFrame(test, columns=categ_df.columns), ignore_index=True)
        trained_model = train_model(train_df, i)
        conf_matrix = test_model(trained_model, test_df)
        pred_matrix += conf_matrix
    pred_matrix /= K_FOLD
    return pred_matrix


def arrange_df(df):
    df = df.sample(frac=1, random_state=1).reset_index(drop=True)
    df = df.replace("bug report", 0) \
        .replace('feature request', 1) \
        .replace('ratings', 2) \
        .replace('user experience', 3) \
        .rename(columns={"review": "text", "category": "labels"})
    return df


def use_existing_model(file_path):
    file_extension = os.path.splitext(file_path)[1]
    if file_extension == ".json":
        test_df = read_json(file_path)
    elif file_extension == ".csv":
        test_df = read_csv(file_path)
    else:
        logger.error(f'File extension "{file_extension}" is not supported! Use .json or .csv files.')
        return
    test_df = arrange_df(apply_preprocess(test_df))
    if os.path.exists("input/classifier.pt"):
        trained_model = create_model()
        trained_model.model.load_state_dict(torch.load("input/classifier.pt"))
        trained_model.model.eval()
    else:
        model_df = arrange_df(apply_preprocess(get_data_from_bigquery(config)))
        trained_model = train_model(model_df, "existing")
        torch.save(trained_model.model.state_dict(), "input/classifier.pt")
    conf_matrix = test_model(trained_model, test_df)
    create_confisuon_matrix(conf_matrix)


if __name__ == "__main__":
    df = None
    if os.path.exists(sys.argv[1]):
        file_path = sys.argv[1]
        config = read_config(sys.argv[1])
        if config["use_existing_model"]:
            use_existing_model(config["file_path"])
        else:
            if not config["is_file"] ^ config["db_connection"]:
                logger.error("is_file and db_connection parameters are not allowed to be same!")
            elif config["is_file"]:
                file_path = config["file_path"]
                file_extension = os.path.splitext(file_path)[1]
                if file_extension == ".json":
                    df = read_json(file_path)
                elif file_extension == ".csv":
                    df = read_csv(file_path)
                else:
                    logger.error(f'File extension "{file_extension}" is not supported! Use .json or .csv files.')
            else:
                if config["db_type"] == DB_TYPE:
                    df = get_data_from_bigquery(config)
                else:
                    logger.error(f'"{config["db_type"]}" is not supported! Use "bigQuery" instead.')
            if df is not None:
                df = arrange_df(apply_preprocess(df))
                pred_matrix = k_fold(df)
                create_confisuon_matrix(pred_matrix)
    else:
        logger.error(f'Input path {sys.argv[1]} does not exists!')
