import math
import pickle
import re
import logging
import string
import collections
import os
import sys
from urllib.request import urlopen
from typing import List, Dict, Tuple
from multiprocessing.pool import ThreadPool


def stop_word_list() -> List[str]:
    """
    Creates the stop-word list.
    :return: stop word list
    """
    with open("input/stop_words.txt", "r") as stop_word_file:
        return stop_word_file.read().splitlines()


# static variables
PUNCTUATIONS: List[str] = list(string.punctuation + "—…’“”")
STOP_WORDS: List[str] = stop_word_list()
ALPHA = 0.75


def extract_data_from_url(url: str, is_query: bool = False, in_dict: bool = False) -> (
        str, str, List[str], List[str], List[str], List[str], str):
    """
    Extracts the necessary parts of the book.
    :param url: good reads url of the book
    :param is_query: True if the parameter url is the input. Default value is False.
    :param in_dict: True if the parameter url is the input and is in system book dictionary. Default value is False.
    :return: unique part of the link, book title, authors, tokens, recommended book urls, genres
    """
    is_valid: bool = True
    is_desc_valid: bool = True
    with urlopen(url) as data:
        info = data.read().decode("utf-8")
        try:
            title: str = re.findall("<h1 id=\"bookTitle\" class=\"gr-h1 gr-h1--serif\" itemprop=\"name\">\n[\s]+(.*?)"
                                    "\n</h1>", info, re.DOTALL)[0]
        except IndexError as ex:
            print("(BROKEN LINK) Error happened while parsing the url: {0}".format(url))
            url = url[:url.index("/book/")] + "/en" + url[url.index("/book/"):]
            print("(INFO) Program will try to parse this url: {0}".format(url))
            fixed_data = urlopen(url)
            info = fixed_data.read().decode("utf-8")
            fixed_data.close()
            title: str = re.findall("<h1 id=\"bookTitle\" class=\"gr-h1 gr-h1--serif\" itemprop=\"name\">\n[\s]+(.*?)"
                                    "\n</h1>", info, re.DOTALL)[0]

        unique_link = url[url.rfind("/") + 1:]
        if not unique_link.endswith("\n"):
            unique_link += "\n"

        author_list: List[str] = re.findall("<span itemprop=\"name\">(.*?)</span>", info, re.DOTALL)
        description = re.findall("<span id=\"freeText(.*?)</span>",
                                 re.findall("<div id=\"descriptionContainer\">(.*?)</div>\n</div>", info, re.DOTALL)[0],
                                 re.DOTALL)
        if len(description) > 1:
            index = 1  # show more
            description = description[index][description[index].find(">") + 1:]
        elif len(description) == 1:
            index = 0
            description = description[index][description[index].find(">") + 1:]

        recommended_book_urls: List[str] = re.findall("'>\n<a href=\"(.*?)\"><img alt=\"",
                                                      re.findall("<div class='carouselRow' style='width: 3600px'>"
                                                                 "(.*?)</div>", info, re.DOTALL)[0], re.DOTALL)
        genres: List[str] = re.findall('<a class="actionLinkLite bookPageGenreLink" href="/genres/(.*?)">', info,
                                       re.DOTALL)

        if str(description).strip() == "" or description is None:
            is_desc_valid = False
        else:
            description = re.sub(r'<.*?>', '', str(description))

        if genres == [] or genres is None:
            if not is_desc_valid:
                is_valid = False
                print("(WARNING) Both genres and description are empty! URL: \"{0}\"".format(url))

        if is_query:
            with open("output/book_content.txt", "wb") as book_content:
                book_content.write("--Book Name--\n{0}\n--Authors--\n{1}\n--Description--\n{2}\n--Recommended Book Urls"
                                   "--\n".format(title, str(author_list)[1:-1].replace("'", ""), description).
                                   encode("utf-8"))
                for rec_url in recommended_book_urls:
                    book_content.write((rec_url + "\n").encode("utf-8"))
                book_content.write("--Genres--\n".encode("utf-8"))
                for genre in genres:
                    book_content.write((genre + "\n").encode("utf-8"))
            if in_dict:
                return

        if is_valid:
            try:
                tokens: List[str] = []
                if is_desc_valid:
                    tokens = tokenize(str(description))
            except Exception as ex:
                logging.error("Error happened while tokenizing.")
                raise ex
            if description is None:
                description = ""
            if is_query:
                return title, author_list, tokens, recommended_book_urls, genres
            return unique_link, title, author_list, tokens, recommended_book_urls, genres, description


def tokenize(description: str) -> List[str]:
    """
    Splits description to tokens.
    :param description: description text of the book
    :return: list of tokens
    """
    tokens: List[str] = []
    description = description.lower()

    for punctuation in PUNCTUATIONS:
        description = description.replace(punctuation, " ")
    description_words: List[str] = description.split()

    for word in description_words:
        if word not in STOP_WORDS and (word.isnumeric() or len(word) > 1):
            if len(word) > 6:
                if word.endswith("ies"):
                    word.replace("ies", "y")
                elif word.endswith("sses"):
                    word = word[:-2]
                elif word.endswith("s") and not word.endswith("ss"):
                    word = word[:-1]
            tokens.append(word)

    return tokens


def create_dict(file_path: str) -> Dict[str, Dict[str, List[str] or str]]:
    """
    Creates a dictionary which keeps necessary info of the books.
    :return: book dictionary: {unique_part: {book_title:'', authors:[], tokens:[], recommended_urls[], genres:[]}}
    """
    book_dict: Dict[str, Dict[str, List[str] or str]] = {}
    descriptions: List[str] = []
    with open(file_path, "r") as file:
        urls = file.readlines()
        results = ThreadPool(15).imap_unordered(extract_data_from_url, urls)
        for fetched_data in results:
            book_dict[fetched_data[0]] = {"title": fetched_data[1]}
            book_dict[fetched_data[0]]["authors"] = fetched_data[2]
            book_dict[fetched_data[0]]["tokens"] = fetched_data[3]
            book_dict[fetched_data[0]]["recommendations"] = fetched_data[4]
            book_dict[fetched_data[0]]["genres"] = fetched_data[5]
            descriptions.append(fetched_data[6])

    i = 0
    with open("output/book_content.txt", "wb") as book_content:
        for unique_part in book_dict:
            title = book_dict[unique_part]["title"]
            author_list = book_dict[unique_part]["authors"]
            recommended_book_urls = book_dict[unique_part]["recommendations"]
            genres = book_dict[unique_part]["genres"]
            description = descriptions[i]
            book_content.write("--Book Name--\n{0}\n--Authors--\n{1}\n--Description--\n{2}\n--Recommended Book Urls"
                               "--\n".format(title, str(author_list)[1:-1].replace("'", ""), description).
                               encode("utf-8"))
            for rec_url in recommended_book_urls:
                book_content.write((rec_url + "\n").encode("utf-8"))
            book_content.write("--Genres--\n".encode("utf-8"))
            for genre in genres:
                book_content.write((genre + "\n").encode("utf-8"))
            book_content.write("\n".encode("utf-8"))
            i += 1
    return book_dict


def tf_weight_calculator(tokens: List[str]) -> Dict[str, float]:
    """
    Calculates the TF Weight score of each token and genre.
    :param tokens: list of tokens or genres
    :return: a dictionary represented as {token or genre: tf_weight_score}
    """
    score_dict: Dict[str, float] = {}
    doc_freq: Dict[str, int] = dict(collections.Counter(tokens))
    for token in tokens:
        score_dict[token] = 1.0 + math.log(doc_freq[token])
    return score_dict


def df_calculator(book_dict: Dict[str, Dict[str, List[str] or str]], query_tokens: List[str] = None,
                  query_genres: List[str] = None) -> (Dict[str, int], Dict[str, int]):
    """
    Calculates the document frequency of each token and genre.
    :param query_tokens: Tokens of the input query
    :param query_genres: Genres of the input query
    :param book_dict: {unique_part: {book_title:'', authors:[], tokens:[], recommended_urls[], genres:[]}}
    :return: Tuple of dictionaries represented as ({token: df_score}{genre: df_score})
    """
    token_df_dict: Dict[str, int] = {}  # {token: doc. freq.}
    genre_df_dict: Dict[str, int] = {}

    if query_tokens is None:
        for unique_link in book_dict:
            token_set = list(set(book_dict[unique_link]["tokens"]))
            genre_set = list(set(book_dict[unique_link]["genres"]))
            for token in token_set:
                if token not in token_df_dict:
                    token_df_dict[token] = 1
                else:
                    token_df_dict[token] += 1
            for genre in genre_set:
                if genre not in genre_df_dict:
                    genre_df_dict[genre] = 1
                else:
                    genre_df_dict[genre] += 1

    else:  # calculate df values for the input query
        for token in query_tokens:
            for unique_link in book_dict:
                token_set = list(set(book_dict[unique_link]["tokens"]))
                if token in token_set:
                    if token not in token_df_dict:
                        token_df_dict[token] = 1
                    else:
                        token_df_dict[token] += 1
        for genre in query_genres:
            for unique_link in book_dict:
                genre_set = list(set(book_dict[unique_link]["genres"]))
                if genre in genre_set:
                    if genre not in genre_df_dict:
                        genre_df_dict[genre] = 1
                    else:
                        genre_df_dict[genre] += 1

    return token_df_dict, genre_df_dict


def idf_calculator(df_dict: Dict[str, int], num_of_books: int) -> Dict[str, float]:
    """
    Calculates the inverse document frequency of tokens and genres.
    :param df_dict: a dictionary which keeps the df score tokens or genres {token or genre: df_score}
    :param num_of_books: number of books in the system
    :return: a dictionary which keeps the idf score tokens or genres {token or genre: idf_score}
    """
    idf_dict: Dict[str, float] = {}
    for token in df_dict:
        idf_dict[token] = math.log(num_of_books / df_dict[token])
    return idf_dict


def genre_score_calculator(tf_dict: Dict[str, Dict[str, float]], idf_dict: Dict[str, float]) \
        -> Dict[str, Dict[str, float]]:
    """
    Calculates the score of the genres by doing idf * tf operation.
    :param tf_dict: a dictionary represented as {unique_part: {genre: tf_weight_score}}
    :param idf_dict: a dictionary represented as {genre: idf_score}
    :return: a dictionary represented as {unique_part: {genre: score}}, score = tf * idf
    """
    for unique_part in tf_dict:
        for genre in tf_dict[unique_part]:
            idf_value: float = idf_dict[genre]
            tf_value: float = tf_dict[unique_part][genre]
            tf_dict[unique_part][genre] = idf_value * tf_value
    return tf_dict


def token_score_calculator(tf_dict: Dict[str, Tuple[Dict[str, float], str]], idf_dict: Dict[str, float]) \
        -> Dict[str, Tuple[Dict[str, float], str]]:
    """
    Calculates the score of the tokens by doing idf * tf operation.
    :param tf_dict: a dictionary represented as {unique_part: ({token: tf_weight_score}, book_title)}
    :param idf_dict: a dictionary represented as {token: idf_score}
    :return: a dictionary represented as {unique_part: ({token: score}, book_title)}, score = tf * idf
    """
    for unique_link in tf_dict:
        for token in tf_dict[unique_link][0]:
            idf_value: float = idf_dict[token]
            tf_value: float = tf_dict[unique_link][0][token]
            tf_dict[unique_link][0][token] = idf_value * tf_value
    return tf_dict


def genre_length_normalization(score_dict: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Calculates the length normalization scores of tf * idf scores for the genres.
    :param score_dict: a dictionary represented as {unique_part: {genre: score}}, score = tf * idf
    :return: a dictionary represented as {unique_part: {genre: normalized_score}}
    """
    total: float = 0
    for book_title in score_dict:
        for token in score_dict[book_title]:
            val: float = score_dict[book_title][token]
            total += val ** 2

        total_sqrt = math.sqrt(total)

        for token in score_dict[book_title]:
            score_dict[book_title][token] /= total_sqrt
        total = 0
    return score_dict


def token_length_normalization(score_dict: Dict[str, Tuple[Dict[str, float], str]]) \
        -> Dict[str, Tuple[Dict[str, float], str]]:
    """
    Calculates the length normalization scores of tf * idf scores for the tokens.
    :param score_dict: a dictionary represented as {unique_part: ({token: score}, book_title)}, score = tf * idf
    :return: a dictionary represented as {unique_part: ({token: normalized_ score}, book_title)}
    """
    total: float = 0
    for unique_link in score_dict:
        for token in score_dict[unique_link][0]:
            val: float = score_dict[unique_link][0][token]
            total += val ** 2

        total_sqrt = math.sqrt(total)

        for token in score_dict[unique_link][0]:
            score_dict[unique_link][0][token] /= total_sqrt
        total = 0
    return score_dict


def cosine_similarity(query_scores: Dict[str, float], book_score: Dict[str, float]) -> float:
    """
    Calculates the cosine similarity between the input book and a book already in the system.
    (both for genres and tokens)
    :param query_scores: a dictionary for the input book represented as {token or genre: normalized_score}
    :param book_score: a dictionary represented as {token or genre: normalized_score}
    """
    val: float = 0
    for token in query_scores:
        if token in book_score:
            val += query_scores[token] * book_score[token]
    return val


def similarity_calculator(query_link: str, book_dict: Dict[str, Dict[str, List[str] or str]],
                          normalized_dict: Dict[str, Tuple[Dict[str, float], str]],
                          genre_normalized_dict: Dict[str, Dict[str, float]], query_tokens: Dict[str, float] = None,
                          query_genres: Dict[str, float] = None) \
        -> (Dict[str, list], Dict[str, Tuple[str, List[str]]]):
    """
    Calculates the similarity score between the input query and system books.
    :param query_genres: keeps the length normalization scores of the input query's genres
    :param query_tokens: keeps the length normalization scores of the input query's tokens
    :param query_link: unique part of the input query url
    :param book_dict: a dictionary represented as {unique_part: {book_title:'', authors:[], tokens:[],
    recommended_urls[], genres:[]}}
    :param normalized_dict: a dictionary represented as {unique_part: ({token: normalized_score}, book_title)}
    :param genre_normalized_dict: a dictionary represented as {unique_part: {token: normalized_score}}
    """
    value_results: Dict[str, float] = {}
    title_authors: Dict[str, Tuple[str, List[str]]] = {}
    if query_tokens is not None:
        for unique_link in book_dict:
            desc_sim: float = cosine_similarity(query_tokens, normalized_dict[unique_link][0])
            genre_sim: float = cosine_similarity(query_genres, genre_normalized_dict[unique_link])
            sim_value: float = ALPHA * desc_sim + (1 - ALPHA) * genre_sim
            value_results[unique_link] = sim_value
            title_authors[unique_link] = (book_dict[unique_link]["title"], book_dict[unique_link]["authors"])
    else:
        for unique_link in book_dict:
            if unique_link != query_link:
                desc_sim: float = cosine_similarity(normalized_dict[query_link][0], normalized_dict[unique_link][0])
                genre_sim: float = cosine_similarity(genre_normalized_dict[query_link],
                                                     genre_normalized_dict[unique_link])
                sim_value: float = ALPHA * desc_sim + (1 - ALPHA) * genre_sim
                value_results[unique_link] = sim_value
                title_authors[unique_link] = (book_dict[unique_link]["title"], book_dict[unique_link]["authors"])
    return value_results, title_authors


def recommend_books(recommendations: List[str], title_authors: Dict[str, Tuple[str, List[str]]]):
    """
    Prints the recommended books in a title-author pair format.
    :param recommendations: list of unique_parts of the urls recommended by the system
    :param title_authors: a dictionary represented as {unique_part: (book_title, author_list)}
    """
    print("Recommended title-author pairs are:")
    for unique_link in recommendations:
        pair: Tuple[str, List[str]] = title_authors[unique_link]
        print("Title: {0} | Authors: {1}".format(pair[0], str(pair[1])[1:-1]))


def precision_calculator(query_recom_urls: List[str], recommendations: List[str]):
    """
    Calculates the average precision and precision scores and prints these to the console.
    :param query_recom_urls: list of recommended urls of the input query
    :param recommendations: list of unique_parts of the urls recommended by the system
    """
    precision: float = 0
    matches: int = 0
    len_recommendations: int = len(recommendations)  # 18
    for i in range(len_recommendations):
        unique_link = "https://www.goodreads.com/book/show/" + recommendations[i][:-1]
        if unique_link in query_recom_urls:
            matches += 1
            precision += matches / (i + 1)
    avg_precision: float = precision / matches
    precision: float = matches / len_recommendations
    print("{0} matches are found!".format(matches))
    print("AVG PRECISION: {0}".format(round(avg_precision, 2)))
    print("PRECISION: {0}".format(round(precision, 2)))


def do_calculations(book_dict: Dict[str, Dict[str, List[str] or str]], num_of_books: int,
                    query_tokens: List[str] = None, query_genres: List[str] = None) \
        -> (Dict[str, Tuple[Dict[str, float], str]], Dict[str, Dict[str, float]]):
    """
    Does the necessary calculations of the tf-idf approach
    :param book_dict: keeps the necessary info of the corpus or input query
    :param num_of_books: total number of the books in the corpus
    :param query_tokens: tokens of the input book
    :param query_genres: genres of the input book
    :return: return length normalized dictionaries of genres and tokens
    """
    genre_tf_dict: Dict[str, Dict[str, float]] = {}
    tf_dict: Dict[str, Tuple[Dict[str, float], str]] = {}
    for unique_link in book_dict:
        genre_tf_dict[unique_link] = tf_weight_calculator(book_dict[unique_link]["genres"])
        tf_dict[unique_link] = (tf_weight_calculator(book_dict[unique_link]["tokens"]),
                                book_dict[unique_link]["title"])

    if query_tokens is not None:
        df_dict, genre_df_dict = df_calculator(book_dict, query_tokens, query_genres)
    else:
        df_dict, genre_df_dict = df_calculator(book_dict)

    idf_dict: Dict[str, float] = idf_calculator(df_dict, num_of_books)
    genre_idf_dict: Dict[str, float] = idf_calculator(genre_df_dict, num_of_books)

    score_dict: Dict[str, Tuple[Dict[str, float], str]] = token_score_calculator(tf_dict, idf_dict)
    genre_score_dict: Dict[str, Dict[str, float]] = genre_score_calculator(genre_tf_dict, genre_idf_dict)

    normalized_dict: Dict[str, Tuple[Dict[str, float], str]] = token_length_normalization(score_dict)
    genre_normalized_dict: Dict[str, Dict[str, float]] = genre_length_normalization(genre_score_dict)

    return normalized_dict, genre_normalized_dict


if __name__ == '__main__':
    arg: str = sys.argv[1]
    if os.path.exists(arg):  # input is a file
        print("(INFO) Model will be created...")
        book_dict: Dict[str, Dict[str, List[str] or str]] = create_dict(arg)
        normalized_dict, genre_normalized_dict = do_calculations(book_dict, len(book_dict))
        with open("output/token_model.pickle", "wb") as token_model_file:
            pickle.dump(normalized_dict, token_model_file)
        with open("output/genre_model.pickle", "wb") as genre_model_file:
            pickle.dump(genre_normalized_dict, genre_model_file)
        with open("output/book_dict.pickle", "wb") as book_file:
            pickle.dump(book_dict, book_file)
        print("(INFO) Model saved in the output folder.")

    else:  # input is a string url
        if os.path.exists("output/token_model.pickle") and os.path.exists("output/genre_model.pickle"):
            with open("output/token_model.pickle", "rb") as token_model_file:
                normalized_dict: Dict[str, Tuple[Dict[str, float], str]] = pickle.load(token_model_file)

            in_dict: bool = True
            query_url: str = arg
            unique_part = query_url[query_url.rfind("/") + 1:] + "\n"
            with open("output/genre_model.pickle", "rb") as genre_model_file:
                genre_normalized_dict: Dict[str, Dict[str, float]] = pickle.load(genre_model_file)
            with open("output/book_dict.pickle", "rb") as book_file:
                book_dict: Dict[str, Dict[str, List[str] or str]] = pickle.load(book_file)

            q_token_normalized: Dict[str, Tuple[Dict[str, float], str]] = {}
            q_genre_normalized: Dict[str, Dict[str, float]] = {}
            if unique_part in normalized_dict:
                print("(INFO) Query url: \"{0}\" is found in the dictionary!".format(query_url))
                extract_data_from_url(query_url, True, True)
                recommended_urls: List[str] = book_dict[unique_part]["recommendations"]

            else:  # query url is not in the corpus
                in_dict = False
                print("(INFO) Query url: \"{0}\" is not in the dictionary previously created!")
                title, author_list, tokens, recommended_book_urls, genres = extract_data_from_url(query_url, True)
                query_dict: Dict[str, Dict[str, List[str] or str]] = {unique_part: {"title": title}}
                query_dict[unique_part]["authors"] = author_list
                query_dict[unique_part]["tokens"] = tokens
                query_dict[unique_part]["recommendations"] = recommended_book_urls
                query_dict[unique_part]["genres"] = genres
                q_token_normalized, q_genre_normalized = do_calculations(query_dict, len(book_dict), tokens, genres)
                recommended_urls: List[str] = recommended_book_urls

            try:
                if in_dict:
                    value_results, title_authors = similarity_calculator(unique_part, book_dict, normalized_dict,
                                                                         genre_normalized_dict)
                else:
                    value_results, title_authors = similarity_calculator(
                        unique_part, book_dict, normalized_dict, genre_normalized_dict,
                        q_token_normalized[unique_part][0], q_genre_normalized[unique_part])
                recommendations: List[str] = sorted(value_results, key=value_results.get, reverse=True)[:18]
                recommend_books(recommendations, title_authors)
                try:
                    precision_calculator(recommended_urls, recommendations)
                except ZeroDivisionError as ex:
                    print("No matches founded...")
                    print("AVG PRECISION: 0")
                    print("PRECISION: 0")
            except Exception as ex:
                logging.error("Something wrong happened while calculating the similarity results of query url: {0}\n{1}"
                              .format(query_url, ex))
        else:
            print("(ERROR) Create the model FIRST, by giving the file path as an argument!")
