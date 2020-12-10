import re
from typing import List, Dict
import os
import logging
import string
import datetime
import json
from trie import Trie
import pickle


def extract_files():
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
            text_list = [pt.split('</REUTERS>')[0] for pt in file_data.strip().split('<REUTERS')][1:]
            id_list += re.findall(r'(?<=NEWID=")(.*)(?=">)', file_data)

            for text in text_list:
                article = ""
                if "<TITLE>" in text and "</TITLE>" in text:
                    article += text[text.index("<TITLE>") + 7: text.index("</TITLE>")] + " \n"
                if "<BODY>" in text and "</BODY>" in text:
                    article += text[text.index("<BODY>") + 6: text.rfind("</BODY>")]

                article_list.append(article)
        except Exception as ex:
            logging.error("An error occured while reading the sgm file. {0}".format(ex))
        finally:
            if in_file:
                in_file.close()
    return id_list, article_list, stop_words


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


def create_inverted_index(tokens_with_indexes: List[List[str]]):
    token_index_dict: Dict[str: List[str]] = {}
    for index, token_list in enumerate(tokens_with_indexes):
        for token in token_list:
            if token not in token_index_dict:
                token_index_dict[token] = [index+1]
            else:
                token_index_dict[token].append(index+1)
    return token_index_dict


def create_json_file(token_index_dict):
    with open("inverted_index.json", "w") as outfile:
        json.dump(token_index_dict, outfile)


def create_trie(all_tokens: List[str]) -> Trie:
    trie = Trie()
    for token in all_tokens:
        trie.insert_token(token)
    return trie


def create_pickle_file(trie):
    with open("trie.pkl", "wb") as trie_file:
        pickle.dump(trie.root, trie_file)


def query_processor(inverted_index, trie):
    while True:
        input_query = input("Enter your query:(Press \"quit\" for terminate.) ")
        if input_query == "quit":
            break
        elif " " in input_query:
            print("Wrong format! Write a single word or prefix*.")
        else:
            is_found = trie.search(input_query)
            if is_found[0]:  # FOUND
                if is_found[1]:  # PREFIX SEARCH
                    output_str = ""
                    prefix = input_query[:-1]
                    length_prefix = len(prefix)
                    dict_tokens = list(inverted_index.keys())
                    for token in dict_tokens:
                        if length_prefix <= len(token) and token[:length_prefix] == prefix:
                            output_str += "Did you mean " + "\"" + token + "\"? If so the IDs are (at max 10 IDs) " \
                                          + str(inverted_index[token][:10])[1:-1] + ".\n"
                    print(output_str[:-1])
                else:  # WORD SEARCH
                    print(input_query + " is found! The first 10 IDs are " + str(inverted_index[input_query][:10])[1:-1] + ".")
            else:
                print("Input query " + input_query + " is not found! Please try again.")


if __name__ == '__main__':
    begin = datetime.datetime.now()
    id_list, article_list, stop_words = extract_files()  # id list'e gerek olmayabiir
    tokens_with_indexes, all_tokens = get_tokens(article_list, stop_words)
    inverted_index = create_inverted_index(tokens_with_indexes)
    trie = create_trie(all_tokens)
    create_json_file(inverted_index)
    create_pickle_file(trie)
    print("Before query processor {0}".format(datetime.datetime.now() - begin))
    query_processor(inverted_index, trie)
    print("Terminated")
