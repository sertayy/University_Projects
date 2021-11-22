import string
from nltk.tokenize import word_tokenize
from snowballstemmer import TurkishStemmer

TURK_STEM = TurkishStemmer()


def apply_preprocess(reviews_df):
    reviews_df["review"] = reviews_df["review"].apply(lowercase_text)
    reviews_df["review"] = reviews_df["review"].apply(remove_punctuations)
    reviews_df["review"] = reviews_df["review"].apply(remove_whitespace)
    return reviews_df


# Lowercase given text data
def lowercase_text(data):
    return data.lower()


# Remove whitespaces from given text data
def remove_whitespace(data):
    return " ".join(data.split())


# Remove punctuations from given text data
def remove_punctuations(data):
    return "".join([char for char in data if char not in string.punctuation])


# Stem the given text data
def stem_text(data):
    tokenized_data = word_tokenize(data)
    stemmed_data_list = TURK_STEM.stemWords(tokenized_data)
    return " ".join(stemmed_data_list)
