from google.cloud import bigquery
from google.cloud import bigquery_storage
from google.oauth2 import service_account
import pandas as pd
import json
from typing import Dict, TypeVar

T = TypeVar('T')


def get_data_from_bigquery(config: Dict[str, T]):
    credentials = service_account.Credentials.from_service_account_file(config["key_path"])  # change path with yours
    project_id = config["project_id"]
    client = bigquery.Client(credentials=credentials, project=project_id)
    bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)
    table = bigquery.TableReference.from_string(
        f'{config["project_id"]}.{config["schema_name"]}.{config["table_name"]}')
    rows = client.list_rows(table)
    df = rows.to_dataframe(bqstorage_client=bqstorageclient)
    if "rating" in list(df["category"]):
        df = df.drop(df[(df.category == 'rating')].index).reset_index(drop=True)
    return df


def read_csv(input_path: str):
    return pd.read_csv(input_path)


def read_json(input_path: str):
    return pd.read_json(input_path)


def read_config(input_path: str):
    with open(input_path) as json_file:
        return json.load(json_file)


"""# create_confisuon_matrix()
df = pd.read_feather("reviews")
df = df.sample(frac=1, random_state=1).reset_index(drop=True)
categories = df['labels'].unique()
test_df = pd.DataFrame(columns=df.columns)
train_df = pd.DataFrame(columns=df.columns)
for category in categories:
    categ_df = df[df['labels'] == category]
    categ_values = categ_df.values
    piece = int(len(categ_values) / 5)
    training = np.concatenate(
        (categ_values[:len(categ_values) - piece * 4, :], categ_values[len(categ_values) - piece * 3:, :]))
    test = categ_values[len(categ_values) - piece * 4:len(categ_values) - piece * 3, :]
    train_df = train_df.append(DataFrame(training, columns=categ_df.columns), ignore_index=True)
    test_df = test_df.append(DataFrame(test, columns=categ_df.columns), ignore_index=True)

trained_model = train_model(train_df)
# model_save_name = 'classifier.pt'
# path = F"/content/drive/MyDrive/Colab Notebooks/{model_save_name}"
# torch.save(trained_model.model.state_dict(), path)
test_model(trained_model, test_df)
# 2 -> training = np.concatenate((categ_values[:len(categ_values) - piece*2, :], categ_values[len(categ_values) - piece:, :]))
# test = categ_values[len(categ_values) - piece*2:len(categ_values) - piece, :]
# training = np.concatenate((categ_values[:len(categ_values) - piece*3, :], categ_values[len(categ_values) - piece*2:, :]))
# test = categ_values[len(categ_values) - piece*3:len(categ_values) - piece*2, :]
# 4 -> training = np.concatenate((categ_values[:len(categ_values) - piece*4, :], categ_values[len(categ_values) - piece*3:, :]))
# test = categ_values[len(categ_values) - piece*4:len(categ_values) - piece*3, :]
# 5 -> training = np.concatenate((categ_values[:len(categ_values) - piece*5, :], categ_values[len(categ_values) - piece*4:, :]))
# test = categ_values[len(categ_values) - piece*5:len(categ_values) - piece*4, :]"""
