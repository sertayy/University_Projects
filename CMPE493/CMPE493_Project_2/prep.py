import re
from typing import List, Dict
import os
import logging
import string
import json
import pickle
from trie import Trie


def extract_files():  # extracts the words in stopwords.txt and the necessary information from the Reuters articles
    files_dir_path: str = os.path.join(os.path.dirname(__file__), "reuters21578")
    id_list: List[str] = []
    article_list: List[str] = []
    in_file = None
    with open("stop_words.txt", "r") as stop_word_file:
        stop_words = stop_word_file.read().splitlines()

    for i in range(22):
        try:
            if i < 10:
                file_name = "reut2-00{0}.sgm".format(i)
            else:
                file_name = "reut2-0{0}.sgm".format(i)

            in_file = open(os.path.join(files_dir_path, file_name), "rb")
            file_data: str = in_file.read().decode("latin-1")

            # splits the file to the texts
            text_list = [pt.split('</REUTERS>')[0] for pt in file_data.strip().split('<REUTERS')][1:]
            for text in text_list:
                article = ""
                if "<TITLE>" in text and "</TITLE>" in text:
                    article += text[text.index("<TITLE>") + 7: text.index("</TITLE>")] + " \n"
                if "<BODY>" in text and "</BODY>" in text:
                    article += text[text.index("<BODY>") + 6: text.rfind("</BODY>")]

                article_list.append(article)  # ID list is not necessary since we will use article_list's index + 1
        except Exception as ex:
            logging.error("An error occured while reading the sgm file. {0}".format(ex))
        finally:
            if in_file:
                in_file.close()
    return article_list, stop_words


# returns all of the total distinct tokens and the list of token-list of each article
def get_tokens(article_list: List[str], stop_words: List[str]) -> (List[List[str]], List[str]):
    special_chars = string.punctuation
    tokens_with_indexes: List[List[str]] = []
    all_tokens: List[str] = []
    for text in article_list:
        if text != "":
            # punction-removal
            for char in special_chars:
                if char in text:
                    text = text.replace(char, ' ')

            # case-folding
            text = text.casefold()

            words = text.split()
            # removes duplicates for efficiency
            words = list(dict.fromkeys(words))
            # stopword removal
            for stop_word in stop_words:
                if stop_word in words:
                    words.remove(stop_word)
            tokens_with_indexes.append(words)
            all_tokens += words
        else:
            tokens_with_indexes.append([])
    all_tokens = list(dict.fromkeys(all_tokens))
    return tokens_with_indexes, all_tokens


def create_inverted_index(tokens_with_indexes: List[List[str]]):  # creates inverted index
    token_index_dict: Dict[str: List[int]] = {}
    for index, token_list in enumerate(tokens_with_indexes):
        for token in token_list:
            if token not in token_index_dict:
                token_index_dict[token] = [index + 1]  # The reason of + 1 ->NEWID starts with 1 but index starts with 0
            else:
                token_index_dict[token].append(index + 1)
    return token_index_dict


def create_json_file(token_index_dict):  # creates json file of inverted index
    with open("inverted_index.json", "w") as outfile:
        json.dump(token_index_dict, outfile)


def create_trie(all_tokens: List[str]) -> Trie:  # creates trie structure
    trie = Trie()
    for token in all_tokens:
        trie.insert_token(token)
    return trie


def create_pickle_file(trie): # creates pkl file
    with open("trie.pkl", "wb") as trie_file:
        pickle.dump(trie.root, trie_file)


try:
    article_list, stop_words = extract_files()
    tokens_with_indexes, all_tokens = get_tokens(article_list, stop_words)
    inverted_index = create_inverted_index(tokens_with_indexes)
    trie = create_trie(all_tokens)
    create_json_file(inverted_index)
    create_pickle_file(trie)
    print("trie.pkl and inverted_index.json files are created. Query processor can read the structures from these "
          "files.")  # an information message to inform the user.
except Exception as ex:
    print("SOMETHING WRONG HAPPENNED IN PREPARATION!")  # to prevent crashes
    logging.error(ex)
