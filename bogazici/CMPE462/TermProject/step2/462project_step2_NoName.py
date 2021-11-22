import os
import pickle
import string
import sys
import nltk
import warnings
import pandas as pd
import numpy as np
from gensim.parsing.preprocessing import remove_stopwords
from contractions import contractions_dict
from scipy.sparse import hstack
from scipy.sparse import spmatrix, coo_matrix
from sklearn.base import BaseEstimator
from sklearn.linear_model.base import LinearClassifierMixin, SparseCoefMixin
from sklearn.svm import LinearSVC

nltk.download('wordnet', quiet=True)

# To Ignore Warning Messages

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)


# Implementation of NBSVM
# This implementation is taken from https://github.com/prakhar-agarwal/Naive-Bayes-SVM
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


# Dataset Folder
data_folder = sys.argv[2]

# Read the Dataset
test_data = {"index": [], "title": [], "body": [], "class": []}

for file_name in os.listdir(data_folder):

    f_index, f_class = file_name.split("_")
    f_class = f_class.split(".")[0]

    file_text = open(f"{data_folder}/" + file_name, encoding="latin").readlines()

    if len(file_text) == 0:
        file_text = ["", ""]

    test_data["index"].append(int(f_index))
    test_data["title"].append(file_text[0].strip())
    test_data["body"].append(" ".join(file_text[1:]).strip())
    test_data["class"].append(f_class)

# Convert Dictionary to DataFrame
test_df = pd.DataFrame.from_dict(test_data)
test_df = test_df.set_index("index")
test_df = test_df.sort_index()


# Preprocess Steps

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
    r"\w+@\w+(\.[a-z]{2,})+",  # Remove e-mails
    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s("
    r")<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
    # Remove URLS
    r"[{}]".format(string.punctuation),  # Remove Punctuation
    r"[^a-zA-Z]",  # Remove nonalphabetic characters
    r"(^|\s)(\w\s+){3,}",  # Remove single characters repeated at least 3 times
]

# Remove Specified Patters
for pattern in removable_patterns:
    test_df["title"] = test_df["title"].str.replace(pattern, ' ')
    test_df["body"] = test_df["body"].str.replace(pattern, ' ')

# Remove Stopwords
test_df["title"] = test_df["title"].apply(remove_stopwords)
test_df["body"] = test_df["body"].apply(remove_stopwords)


# Lemmatize the text
def lemmatize_text(text):
    lem = nltk.stem.WordNetLemmatizer()
    text = ' '.join([lem.lemmatize(word) for word in text.split()])
    return text


# Apply function on review column
test_df['title'] = test_df['title'].apply(lemmatize_text)
test_df['body'] = test_df['body'].apply(lemmatize_text)


# Stemming the text
def stem_text(text):
    ps = nltk.porter.PorterStemmer()
    text = ' '.join([ps.stem(word) for word in text.split()])
    return text


# Apply function on review column
test_df['title'] = test_df['title'].apply(stem_text)
test_df['body'] = test_df['body'].apply(stem_text)

# Remove unnecessary blanks
test_df["title"] = test_df["title"].apply(lambda x: x.strip())
test_df["body"] = test_df["body"].apply(lambda x: x.strip())

# Read the pretrained model, feature extractor, and feature selector
[nbsvm, rfecv, x_train_mean, bow_title, bow_body] = pickle.load(open(sys.argv[1], "rb"))

# Calculate BOW Features
title_bow = bow_title.transform(test_df["title"])
body_bow = bow_body.transform(test_df['body'])
# Concatenate Feature Vectors
test_bow = hstack((title_bow, body_bow))

# Add other Features
x_test = np.hstack((
    np.array([test_df["title"].str.split().str.len()]).T,
    np.array([test_df["body"].str.split().str.len()]).T,
    np.array([test_df["title"].str.len()]).T,
    np.array([test_df["body"].str.len()]).T,
))
x_test = x_test - x_train_mean
x_test[x_test > 0] = 1
x_test[x_test <= 0] = 0
X_test = test_bow.toarray()
X_test[X_test > 0] = 1
X_test = np.hstack((X_test, x_test))

# Predict with Pre-Trained Models
predictions = nbsvm.predict(rfecv.transform(X_test))

output_dict = {2: "P", 1: "Z", 0: "N"}

# Print the Prediction Classes
for pred in predictions:
    print(output_dict[pred], end="")
