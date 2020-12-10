import json
import logging
from trie import Trie
import pickle


# the query processor that search for the IDs according to the input query,
def query_processor(created_inv_index, created_trie):
    while True:
        input_query = input("Enter your query:(Press \"quit\" for terminate.) ")
        if input_query == "quit":
            break  # program terminates
        elif " " in input_query:  # single word requirement
            print("Wrong format! Write a single word or prefix*.")
        else:
            input_query = input_query.casefold()
            is_found = created_trie.search(input_query)
            if is_found[0]:  # FOUND QUERY
                if is_found[1]:  # PREFIX SEARCH
                    output_ids = []
                    prefix = input_query[:-1]
                    length_prefix = len(prefix)
                    dict_tokens = list(created_inv_index.keys())
                    for token in dict_tokens:
                        if length_prefix <= len(token) and token[:length_prefix] == prefix:
                            output_ids += created_inv_index[token]
                    output_ids = list(dict.fromkeys(output_ids))
                    output_ids.sort()
                    print(output_ids)
                else:  # WORD SEARCH
                    print(created_inv_index[input_query])
            else:
                print("Input query " + input_query + " is not found! Please try again.")


def read_json():  # reads the json file to create the inverted_index that will be used by query processor
    with open('inverted_index.json') as json_f:
        inverted_index = json.load(json_f)
    return inverted_index


def read_pickle(new_trie):  # reads the pkl file to create the trie that will be used by query processor
    with open("trie.pkl", "rb") as pickle_f:
        new_trie.root = pickle.load(pickle_f)
    return new_trie


try:
    created_inv_index = read_json()
    new_trie = Trie()
    created_trie = read_pickle(new_trie)
    query_processor(created_inv_index, created_trie)
except FileNotFoundError as ex:
    # an information message to inform the user.
    print("Run prep.py first with \"python prep.py\". After that you should run query.py.")
    logging.error(ex)

