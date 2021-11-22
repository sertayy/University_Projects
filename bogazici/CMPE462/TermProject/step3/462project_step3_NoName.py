import sys
import pickle
import pandas as pd
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
from gensim.parsing.preprocessing import remove_stopwords
import string
import nltk
nltk.download('wordnet',quiet=True)
nltk.download("opinion_lexicon",quiet=True)
nltk.download("punkt",quiet=True)
# To Ignore Warning Messages
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

from contractions import contractions_dict
from scipy.sparse import hstack
import numpy as np
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity

## Read the pretrained model, feature extractor, and feature selector
model = pickle.load(open(sys.argv[1],"rb"))

# Dataset Folder
data_folder = sys.argv[2]

# Read the Dataset
test_data = {"index":[],"title":[],"body":[],"class":[]}

for file_name in os.listdir(data_folder):

    f_index,f_class = file_name.split("_")
    f_class = f_class.split(".")[0]

    file_text = open(f"{data_folder}/" + file_name,encoding="latin").readlines()
    
    if len(file_text) == 0:
        file_text = ["",""]

    test_data["index"].append(int(f_index))
    test_data["title"].append(file_text[0].strip())
    test_data["body"].append(" ".join(file_text[1:]).strip())
    test_data["class"].append(f_class)

# Convert Dictionary to DataFrame
test_df = pd.DataFrame.from_dict(test_data)
test_df = test_df.set_index("index")
test_df = test_df.sort_index()

## Preprocess Steps

# Split Body into Sentences
test_df["body_sentences"] = test_df["body"].apply(sent_tokenize)

# Calculate Embeddings of Title and Body
test_df["sentence_embeddings"] = test_df["body_sentences"].apply(model["sentence_embedding"].encode)
test_df["title_embeddings"] = test_df["title"].apply(model["sentence_embedding"].encode)

# Remove Contraction
def remove_contraction(text):
    tokens = text.split()
    new_tokens = []
    for token in tokens:
        if token in contractions_dict:
            new_tokens.append(contractions_dict[token])
        elif token.lower() in contractions_dict:
            new_tokens.append(contractions_dict[token.lower()])
        else:
            new_tokens.append(token)
    
    return " ".join(new_tokens)

test_df["title"] = test_df["title"].apply(remove_contraction)
test_df["body"] = test_df["body"].apply(remove_contraction)

# Convert Everything into Lowercase
test_df["title"] = test_df["title"].str.lower()
test_df["body"] = test_df["body"].str.lower()

removable_patterns = [
                    r"\w+@\w+(\.[a-z]{2,})+", # Remove e-mails
                    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", # Remove URLS
                    r"[{}]".format(string.punctuation), # Remove Punctuation
                    r"[^a-zA-Z]", # Remove nonalphabetic characters
                    r"(^|\s)(\w\s+){3,}", # Remove single characters repeated at least 3 times
                    r"\b[a-zA-Z]\b", # Remove single characters

]

# Remove Specified Patters
for pattern in removable_patterns:

    test_df["title"] = test_df["title"].str.replace(pattern,' ')
    test_df["body"] = test_df["body"].str.replace(pattern,' ')

# Remove Stopwords
test_df["title"] = test_df["title"].apply(remove_stopwords)
test_df["body"] = test_df["body"].apply(remove_stopwords)

# Lemmatize the text
def lemmatize_text(text):
    lem = nltk.stem.WordNetLemmatizer()
    text= ' '.join([lem.lemmatize(word) for word in text.split()])
    return text

#Apply function on review column
test_df['title'] = test_df['title'].apply(lemmatize_text)
test_df['body'] = test_df['body'].apply(lemmatize_text)

#Stemming the text
def stem_text(text):
    ps=nltk.porter.PorterStemmer()
    text= ' '.join([ps.stem(word) for word in text.split()])
    return text

#Apply function on review column
test_df['title'] = test_df['title'].apply(stem_text)
test_df['body'] = test_df['body'].apply(stem_text)

# Remove unnecessary blanks
test_df["title"] = test_df["title"].apply(lambda x: x.strip())
test_df["body"] = test_df["body"].apply(lambda x: x.strip())

# Calculate BOW Features
title_bow = model["bow_title"].transform(test_df["title"])
body_bow = model["bow_body"].transform(test_df['body'])
# Concatenate Feature Vectors
test_bow = hstack((title_bow,body_bow))

# Add other Features
x_test = np.hstack((
    np.array([test_df["title"].str.split().str.len()]).T,
    np.array([test_df["body"].str.split().str.len()]).T,
    np.array([test_df["title"].str.len()]).T,
    np.array([test_df["body"].str.len()]).T,
))
x_test = x_test - model["x_train_mean"]
x_test[x_test>0] = 1
x_test[x_test<=0] = 0
X_test = test_bow.toarray()
X_test[X_test > 0] = 1
X_test = np.hstack((X_test,x_test))

# Apply Feature Selection of NBSVM
X_test_fs = model["feature_sel_nbsvm"].transform(X_test)

# Calculate Means of Sentence Embeddings for Body Parts
test_df["sentence_embeddings_mean"] = test_df["sentence_embeddings"].apply(lambda x: np.mean(x,axis = 0))

# Generate Features from NBSVM
X_test_new_ = model["nbsvm"].decision_function(X_test_fs)
X_test_new_ = np.hstack((
    X_test_new_,
    np.vstack((X_test_new_[:,0] - X_test_new_[:,1], X_test_new_[:,0] - X_test_new_[:,2], X_test_new_[:,1] - X_test_new_[:,2])).T,
))

X_test_new_ = model["scaler"].transform(X_test_new_)

# Calculate Features Generated by KMeans - TITLE
test_pos_cos_sim_title = cosine_similarity(model["pos_center_title"], np.array(list(test_df["title_embeddings"])))
test_neg_cos_sim_title = cosine_similarity(model["neg_center_title"], np.array(list(test_df["title_embeddings"])))
test_net_cos_sim_title = cosine_similarity(model["net_center_title"], np.array(list(test_df["title_embeddings"])))

test_kmeans_title = []
    
for elem in test_pos_cos_sim_title:
    test_kmeans_title.append(np.transpose(test_neg_cos_sim_title - elem))
    test_kmeans_title.append(np.transpose(test_net_cos_sim_title - elem))
    
for elem in test_net_cos_sim_title:
    test_kmeans_title.append(np.transpose(test_neg_cos_sim_title - elem))

test_kmeans_title = np.hstack((np.hstack(test_kmeans_title),test_pos_cos_sim_title.T,test_neg_cos_sim_title.T,test_net_cos_sim_title.T))
test_kmeans_title = model["kmeans_title_scaler"].transform(test_kmeans_title)
test_kmeans_title = model["lf_kmeans_title"].transform(test_kmeans_title)

# Calculate Features Generated by KMeans - BODY
test_pos_cos_sim_sent = cosine_similarity(model["pos_center_sent"], np.array(list(test_df["sentence_embeddings_mean"])))
test_neg_cos_sim_sent = cosine_similarity(model["neg_center_sent"], np.array(list(test_df["sentence_embeddings_mean"])))
test_net_cos_sim_sent = cosine_similarity(model["net_center_sent"], np.array(list(test_df["sentence_embeddings_mean"])))

test_kmeans_sent = []
    
for elem in test_pos_cos_sim_sent:
    test_kmeans_sent.append(np.transpose(test_neg_cos_sim_sent - elem))
    test_kmeans_sent.append(np.transpose(test_net_cos_sim_sent - elem))
    
for elem in test_net_cos_sim_sent:
    test_kmeans_sent.append(np.transpose(test_neg_cos_sim_sent - elem))

test_kmeans_sent = np.hstack((np.hstack(test_kmeans_sent),test_pos_cos_sim_sent.T,test_neg_cos_sim_sent.T,test_net_cos_sim_sent.T))
test_kmeans_sent = model["kmeans_sent_scaler"].transform(test_kmeans_sent)
test_kmeans_sent = model["lf_kmeans_sent"].transform(test_kmeans_sent)

# Concatenate all Features
X_test_new = np.hstack((
    X_test_new_,
    model["lf_t"].transform(np.array(list(test_df["title_embeddings"]))),
    model["title_pca"].transform(model["title_scaler"].transform(model["feature_sel_embed_t"].transform(np.array(list(test_df["title_embeddings"]))))),
    ##################################################################################
    model["feature_sel_embed_sen_t"].transform(np.array(list(test_df["sentence_embeddings_mean"]))),
    model["lf_te"].transform(np.array(list(test_df["sentence_embeddings_mean"]))),
    ##################################################################################
    test_kmeans_title,
    test_kmeans_sent,
))
# Predict with the pre-trained model
predictions = model["xgbcls"].predict(X_test_new)

output_dict = model["class_map"]

# Print the Prediction Classes
for pred in predictions:
    print(output_dict[pred],end="")
