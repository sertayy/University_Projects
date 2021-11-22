"""
    In This File Preprocessing Steps are Implemented Which are as Follows:
        1. Cleaning the Data
        2. Feature Extraction (BOW, TF-IDF) + Noise Elimination is added
        3. Feature Selection (Chi Squared - Mutual Information - ANOVA-F)
        4. Feature Extraction for NBSVM (Our Best Model)
"""

# Import Necessary Modules
import pandas as pd
import os
from gensim.parsing.preprocessing import remove_stopwords
import string
import nltk
nltk.download('wordnet')
nltk.download("opinion_lexicon")
nltk.download("punkt")
from nltk.corpus import opinion_lexicon
from nltk.tokenize import sent_tokenize

import matplotlib.pyplot as plt
from contractions import contractions_dict
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
tqdm.pandas()
import copy

def read_data(train_dir,val_dir):
    """
        This function read the data given in txt files
    """
    # Read Training Data
    train_data = {"index":[],"title":[],"body":[],"class":[]}

    for file_name in os.listdir(train_dir):

        f_index,f_class = file_name.split("_")
        f_class = f_class.split(".")[0]

        file_text = open(f"{train_dir}/" + file_name,encoding="latin").readlines()
        
        if len(file_text) == 0:
            continue

        train_data["index"].append(int(f_index))
        train_data["title"].append(file_text[0].strip())
        train_data["body"].append(" ".join(file_text[1:]).strip())
        train_data["class"].append(f_class)

    # Read Validation Data
    val_data = {"index":[],"title":[],"body":[],"class":[]}

    for file_name in os.listdir(val_dir):

        f_index,f_class = file_name.split("_")
        f_class = f_class.split(".")[0]

        file_text = open(f"{val_dir}/" + file_name,encoding="latin").readlines()
        
        if len(file_text) == 0:
            continue

        val_data["index"].append(int(f_index))
        val_data["title"].append(file_text[0].strip())
        val_data["body"].append(" ".join(file_text[1:]).strip())
        val_data["class"].append(f_class)

    return train_data, val_data

def convert_to_df(train_data,val_data):
    """
        This function converts dictionaries to DataFrames
    """
    # Convert Dictionaries to Dataframes
    train_df = pd.DataFrame.from_dict(train_data)
    train_df = train_df.set_index("index")
    train_df = train_df.sort_index()

    val_df = pd.DataFrame.from_dict(val_data)
    val_df = val_df.set_index("index")
    val_df = val_df.sort_index()

    return train_df, val_df

"""
    1. Cleaning the Data
"""
def preprocessing(train_df,val_df,training = False):
    """
        This function implements the preprocessing steps specified in the project report
    """
    ###################################
    # Split Documents into Same Sized Splits
    # This is to use Sentence Embeddings
    # This part generates splits with 200 length with 50 intersected parts
    def get_split(text1):
        l_total = []
        l_parcial = []
        
        if len(text1.split())//150 >0:
            n = len(text1.split())//150
        else: 
            n = 1
        for w in range(n):
            if w == 0:
                l_parcial = text1.split()[:200]
                l_total.append(" ".join(l_parcial))
            else:
                l_parcial = text1.split()[w*150:w*150 + 200]
                l_total.append(" ".join(l_parcial))
        
        return l_total
    if not training:
        train_df["body_splits"] = train_df["body"].apply(get_split)
        val_df["body_splits"] = val_df["body"].apply(get_split)
    ###################################
    # Split Documents into Sentences
    train_df["body_sentences"] = train_df["body"].apply(sent_tokenize)
    val_df["body_sentences"] = val_df["body"].apply(sent_tokenize)
    ###################################
    # Calculate Sentence Embeddings for Different Configurations
    # 1 => Calculate Separately for Each Sentence
    # 2 => Calculate Total of Body
    # 3 => Calculate For Each Split
    # 4 => Calculate for Titles

    sentence_embedding = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    train_df["sentence_embeddings"] = train_df["body_sentences"].progress_apply(sentence_embedding.encode)
    val_df["sentence_embeddings"] = val_df["body_sentences"].progress_apply(sentence_embedding.encode)
    
    if not training:
        train_df["total_embedding"] = train_df["body"].progress_apply(sentence_embedding.encode)
        val_df["total_embedding"] = val_df["body"].progress_apply(sentence_embedding.encode)

    if not training:
        train_df["split_embeddings"] = train_df["body_splits"].progress_apply(sentence_embedding.encode)
        val_df["split_embeddings"] = val_df["body_splits"].progress_apply(sentence_embedding.encode)

    train_df["title_embeddings"] = train_df["title"].progress_apply(sentence_embedding.encode)
    val_df["title_embeddings"] = val_df["title"].progress_apply(sentence_embedding.encode)
    ###################################
    # Remove Contraction
    # Remove contractions from the data. For example, convert `I'm` to `I am`.
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

    train_df["title"] = train_df["title"].apply(remove_contraction)
    train_df["body"] = train_df["body"].apply(remove_contraction)

    val_df["title"] = val_df["title"].apply(remove_contraction)
    val_df["body"] = val_df["body"].apply(remove_contraction)
    ###################################
    # Convert Everything into Lowercase
    train_df["title"] = train_df["title"].str.lower()
    train_df["body"] = train_df["body"].str.lower()

    val_df["title"] = val_df["title"].str.lower()
    val_df["body"] = val_df["body"].str.lower()
    ##################################
    # Calculate Lexicon Score with Different Dictionaries

    pos_set = set(opinion_lexicon.positive())
    neg_set = set(opinion_lexicon.negative())

    def pos_score(text):
        score = 0
        for word in nltk.word_tokenize(text):
            if word in pos_set:
                score += 1
        return score

    def neg_score(text):
        score = 0
        for word in nltk.word_tokenize(text):
            if word in neg_set:
                score += 1
        return score

    if not training:
        train_df["pos_score"] = train_df["body"].apply(pos_score)
        train_df["neg_score"] = train_df["body"].apply(neg_score)

        val_df["pos_score"] = val_df["body"].apply(pos_score)
        val_df["neg_score"] = val_df["body"].apply(neg_score)

        train_df["diff_score"] = train_df["pos_score"] - train_df["neg_score"]
        val_df["diff_score"] = val_df["pos_score"] - val_df["neg_score"]

    lexicon_lines = open("lexicon.txt").readlines()

    sentiment_scores_ = {}

    for token in lexicon_lines:
        
        token = token.split("\t")
        sentiment_scores_[token[0]] = [float(token[1]),float(token[2])]

    sentiment_scores = copy.deepcopy(sentiment_scores_)

    for key in sentiment_scores_:
        if key.isalnum():
            del sentiment_scores[key]

    def sent_score_mean(text):
        
        score = 0
        for token in text.split():
            if token in sentiment_scores:
                score += sentiment_scores[token][0]
        
        return score

    def sent_score_val(text):
        
        score = 0
        for token in text.split():
            if token in sentiment_scores:
                score = np.sqrt(sentiment_scores[token][1]**2 + score**2)
        
        return score

    if not training:
        train_df["body_mean"] = train_df["body"].apply(sent_score_mean)
        train_df["body_std"] = train_df["body"].apply(sent_score_val)

        val_df["body_mean"] = val_df["body"].apply(sent_score_mean)
        val_df["body_std"] = val_df["body"].apply(sent_score_val)

    ###################################
    # Remove the Following patterns from the data.
    # 1. Remove e-mails
    # 2. Remove URLs
    # 3. Remove punctuation
    # 4. Remove nonalphabetical characters
    # 5. Remove single characters repeated at least 3 times
    # 6. Remove single characters repeated
    removable_patterns = [
                    r"\w+@\w+(\.[a-z]{2,})+", # Remove e-mails
                    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", # Remove URLS
                    r"[{}]".format(string.punctuation), # Remove Punctuation
                    r"[^a-zA-Z]", # Remove nonalphabetic characters
                    r"(^|\s)(\w\s+){3,}", # Remove single characters repeated at least 3 times
                    r"\b[a-zA-Z]\b", # Remove single characters

    ]
    # Remove Specified Patters
    for patern in removable_patterns:

        train_df["title"] = train_df["title"].str.replace(patern,' ')
        train_df["body"] = train_df["body"].str.replace(patern,' ')

        val_df["title"] = val_df["title"].str.replace(patern,' ')
        val_df["body"] = val_df["body"].str.replace(patern,' ')

    ###################################
    # Remove Stopwords
    train_df["title"] = train_df["title"].apply(remove_stopwords)
    train_df["body"] = train_df["body"].apply(remove_stopwords)

    val_df["title"] = val_df["title"].apply(remove_stopwords)
    val_df["body"] = val_df["body"].apply(remove_stopwords)

    ###################################
    # Lemmatize the text
    def lemmatize_text(text):
        lem = nltk.stem.WordNetLemmatizer()
        text= ' '.join([lem.lemmatize(word) for word in text.split()])
        return text

    #Apply function on review column
    train_df['title'] = train_df['title'].apply(lemmatize_text)
    train_df['body'] = train_df['body'].apply(lemmatize_text)

    val_df['title'] = val_df['title'].apply(lemmatize_text)
    val_df['body'] = val_df['body'].apply(lemmatize_text)

    ###################################
    #Stemming the text
    def stem_text(text):
        ps=nltk.porter.PorterStemmer()
        text= ' '.join([ps.stem(word) for word in text.split()])
        return text

    #Apply function on review column
    train_df['title'] = train_df['title'].apply(stem_text)
    train_df['body'] = train_df['body'].apply(stem_text)

    val_df['title'] = val_df['title'].apply(stem_text)
    val_df['body'] = val_df['body'].apply(stem_text)

    ###################################
    # Remove unnecessary blanks
    train_df["title"] = train_df["title"].apply(lambda x: x.strip())
    train_df["body"] = train_df["body"].apply(lambda x: x.strip())

    val_df["title"] = val_df["title"].apply(lambda x: x.strip())
    val_df["body"] = val_df["body"].apply(lambda x: x.strip())

    if training:
        return train_df, val_df, sentence_embedding

    return train_df, val_df

"""
    2. Feature Extraction (BOW, TF-IDF)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import hstack
import numpy as np

def calculate_tf_idf(train_df,val_df):
    """
        Calculated the TF_IDF Vectors of Train and Validation Set
    """

    # Vectorize Titles
    tf_idf_title = TfidfVectorizer(min_df = 5)
    title_train = tf_idf_title.fit_transform(train_df["title"])
    title_val = tf_idf_title.transform(val_df["title"])

    # Vectorize Body
    tf_idf_body = TfidfVectorizer(min_df = 10)
    body_train = tf_idf_body.fit_transform(train_df["body"])
    body_val = tf_idf_body.transform(val_df["body"])

    # Concatenate Vectors
    train_tf_idf = hstack((title_train,body_train))
    val_tf_idf = hstack((title_val,body_val))

    return train_tf_idf, val_tf_idf, tf_idf_title, tf_idf_body

def calculate_bow(train_df,val_df):

    # Vectorize Titles
    bow_title = CountVectorizer(min_df = 5)
    title_train = bow_title.fit_transform(train_df["title"])
    title_val = bow_title.transform(val_df["title"])

    # Vectorize Body
    bow_body = CountVectorizer(min_df = 10)
    body_train = bow_body.fit_transform(train_df["body"])
    body_val = bow_body.transform(val_df["body"])
    
    # Concatenate Vectors
    train_bow = hstack((title_train,body_train))
    val_bow = hstack((title_val,body_val))

    return train_bow, val_bow, bow_title, bow_body

def encode_target_classes(train_df,val_df):
    
    # Encode P with 2, Z with 1 and N with 0
    y_train = train_df["class"].map({"P":2,"Z":1,"N":0})
    y_val = val_df["class"].map({"P":2,"Z":1,"N":0})

    return y_train, y_val

"""
    3. Feature Selection (Chi Squared - Mutual Information - ANOVA-F)
"""
from sklearn.feature_selection import chi2, mutual_info_classif, f_classif
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import FeatureUnion
from kneed import KneeLocator

def feature_selection(train_features, y_train):

    # Apply Methods individually and Calculate the Knee Values
    ###################################
    # Chi Squared Feature Selection
    chi2_scores,_ = chi2(train_features,y_train)
    chi2_kneedle = KneeLocator([i for i in range(len(chi2_scores))],sorted(chi2_scores), S=1.0, curve="convex", direction="increasing")

    ###################################
    # Apply Mutual Information Test
    mutlual_info = mutual_info_classif(train_features,y_train)
    mi_kneedle = KneeLocator([i for i in range(len(mutlual_info))],sorted(mutlual_info), S=1.0, curve="convex", direction="increasing")

    ###################################
    # Apply ANOVA-F
    f_scores,_ = f_classif(train_features.toarray(),y_train)
    fs_kneedle = KneeLocator([i for i in range(len(f_scores))],sorted(f_scores), S=1.0, curve="convex", direction="increasing")

    ###################################
    #  Combine 3 Methods
    feature_selection = FeatureUnion([
        ("chi2", SelectKBest(chi2,k=len(chi2_scores)-chi2_kneedle.knee)),
        ("mutual_info", SelectKBest(mutual_info_classif,k=len(mutlual_info)-mi_kneedle.knee)),
        ("f_classif", SelectKBest(f_classif,k=len(f_scores)-fs_kneedle.knee))
    ])

    return feature_selection.fit(train_features,y_train)

"""
    4. Feature Extraction for NBSVM (Our Best Model)
"""
def nb_svm_features(train_feature_set, val_feature_set,train_df,val_df):
    """
        This Function Encodes All Features as 0-1 as it is stated in 
        https://www.aclweb.org/anthology/P12-2018.pdf
    """
    x_train = np.hstack((
        np.array([train_df["title"].str.split().str.len()]).T,
        np.array([train_df["body"].str.split().str.len()]).T,
        np.array([train_df["title"].str.len()]).T,
        np.array([train_df["body"].str.len()]).T
    ))
    x_train_mean = np.mean(x_train,axis=0)
    x_train = x_train - x_train_mean
    x_train[x_train>0] = 1
    x_train[x_train<=0] = 0
    X_train = train_feature_set.toarray()
    X_train[X_train > 0] = 1
    X_train = np.hstack((X_train,x_train))

    x_val = np.hstack((
        np.array([val_df["title"].str.split().str.len()]).T,
        np.array([val_df["body"].str.split().str.len()]).T,
        np.array([val_df["title"].str.len()]).T,
        np.array([val_df["body"].str.len()]).T,
    ))
    x_val = x_val - x_train_mean
    x_val[x_val>0] = 1
    x_val[x_val<=0] = 0
    X_val = val_feature_set.toarray()
    X_val[X_val > 0] = 1
    X_val = np.hstack((X_val,x_val))

    return X_train, X_val, x_train_mean