import math
import pickle
import re
import logging
import string
import time
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


PUNCTUATIONS: List[str] = list(string.punctuation + "—…’")
STOP_WORDS: List[str] = stop_word_list()
ALPHA = 0.75


def extract_data_from_url(url: str, is_query: bool = False, in_dict: bool = False) -> (
        str, str, List[str], List[str], List[str], List[str]):
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
            logging.error("Error happended while parsing the url: {0}{1}".format(url, ex))
            url = url[:url.index("/book/")] + "/en" + url[url.index("/book/"):]
            print("Program will try to parse this url: {0}".format(url))
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
        if "<div>" in description:
            description = description.replace("<div>", " ").replace("</div>", " ")
        if "<br /><br />" in description:
            description = description.replace("<br /><br />", "\n")

        recommended_book_urls: List[str] = re.findall("'>\n<a href=\"(.*?)\"><img alt=\"",
                                                      re.findall("<div class='carouselRow' style='width: 3600px'>"
                                                                 "(.*?)</div>", info, re.DOTALL)[0], re.DOTALL)
        genres: List[str] = re.findall('<a class="actionLinkLite bookPageGenreLink" href="/genres/(.*?)">', info,
                                       re.DOTALL)

        if title.strip() == "" or title is None:
            logging.error("Title is not valid for url: {0}".format(url))
        if author_list == [] or author_list is None:
            logging.error("Author list is not valid for url: {0}".format(url))
        if str(description).strip() == "" or description is None or len(description) < 15:
            logging.error("Description is not valid for url: {0}".format(url))
            is_desc_valid = False
            print("Description is \"" + str(description) + "\" .")
        if recommended_book_urls == [] or recommended_book_urls is None:
            logging.error("Recommended books are not valid for url: {0}".format(url))
        if genres == [] or genres is None:
            logging.error("Genres are not valid for url: {0}".format(url))
            if not is_desc_valid:
                is_valid = False

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
            return unique_link, title, author_list, tokens, recommended_book_urls, genres


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


def create_dict() -> Dict[str, Dict[str, List[str] or str]]:
    """
    Creates a dictionary which keeps necessary info of the books.
    :return: book dictionary: {unique_part: {book_title:'', authors:[], tokens:[], recommended_urls[], genres:[]}}
    """
    book_dict: Dict[str, Dict[str, List[str] or str]] = {}
    with open("input/books.txt", "r") as file:
        urls = file.readlines()
        results = ThreadPool(15).imap_unordered(extract_data_from_url, urls)
        for fetched_data in results:
            book_dict[fetched_data[0]] = {"title": fetched_data[1]}
            book_dict[fetched_data[0]]["authors"] = fetched_data[2]
            book_dict[fetched_data[0]]["tokens"] = fetched_data[3]
            book_dict[fetched_data[0]]["recommendations"] = fetched_data[4]
            book_dict[fetched_data[0]]["genres"] = fetched_data[5]
    return book_dict


def calculate_tf_weight(tokens: List[str]) -> Dict[str, float]:
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


def calculate_df(book_dict) -> (Dict[str, int], Dict[str, int]):
    """
    Calculates the document frequency of each token and genre.
    :param book_dict: {unique_part: {book_title:'', authors:[], tokens:[], recommended_urls[], genres:[]}}
    :return: Tuple of dictionaries represented as ({token: df_score}{genre: df_score})
    """
    token_df_dict: Dict[str, int] = {}  # {token: doc. freq.}
    genre_df_dict: Dict[str, int] = {}
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
    return token_df_dict, genre_df_dict


def calculate_idf(df_dict: Dict[str, int], num_of_books: int) -> Dict[str, float]:
    """
    Calculates the document frequency of tokens and genres.
    :param df_dict: a dictionary which keeps the df score tokens or genres {token or genre: df_score}
    :param num_of_books: number of books in the system
    :return: a dictionary which keeps the idf score tokens or genres {token or genre: idf_score}
    """
    idf_dict: Dict[str, float] = {}
    for token in df_dict:
        idf_dict[token] = math.log(num_of_books / df_dict[token])
    return idf_dict


def genre_calculate_score(tf_dict: Dict[str, Dict[str, float]], idf_dict: Dict[str, float]) \
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


def calculate_score(tf_dict: Dict[str, Tuple[Dict[str, float], str]], idf_dict: Dict[str, float]) \
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


def genre_calculate_normalization(score_dict: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Calculates the normalization scores of tf * idf scores for the genres.
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


def calculate_normalization(score_dict: Dict[str, Tuple[Dict[str, float], str]]) \
        -> Dict[str, Tuple[Dict[str, float], str]]:
    """
    Calculates the normalization scores of tf * idf scores for the tokens.
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


def calculate_similarity(query_link: str, book_dict: Dict[str, Dict[str, List[str] or str]],
                         normalized_dict: Dict[str, Tuple[Dict[str, float], str]],
                         genre_normalized_dict: Dict[str, Dict[str, float]]) \
        -> (Dict[str, list], Dict[str, Tuple[str, List[str]]]):
    """
    Calculates the similarity score between the input query and system books.
    :param query_link: unique part of the input query url
    :param book_dict: a dictionary represented as {unique_part: {book_title:'', authors:[], tokens:[], recommended_urls[], genres:[]}}
    :param normalized_dict: a dictionary represented as {unique_part: ({token: normalized_score}, book_title)}
    :param genre_normalized_dict: a dictionary represented as {unique_part: {token: normalized_score}}
    """
    value_results: Dict[str, float] = {}
    title_authors: Dict[str, Tuple[str, List[str]]] = {}
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
    print("Recommended book title vs. author pairs are:")
    for unique_link in recommendations:
        pair: Tuple[str, List[str]] = title_authors[unique_link]
        print("{0} --- {1}".format(pair[0], str(pair[1])[1:-1]))


def calculate_precision(query_recom_urls: List[str], recommendations: List[str]):
    """
    Calculates the average precision and precision scores and prints these to the console.
    :param query_recom_urls: list of recommended urls of the input query
    :param recommendations: list of unique_parts of the urls recommended by the system
    """
    precision: float = 0
    matches: int = 0
    len_recommendations: int = len(recommendations)
    len_query_recom_urls: int = len(query_recom_urls)
    if len_recommendations < len_query_recom_urls:
        logging.error(
            "Total number of recommend urls of the query are bigger than 18. --> ({0})".format(len_query_recom_urls))
    num_of_urls = min(len_recommendations, len_query_recom_urls)

    for i in range(num_of_urls):
        url = query_recom_urls[i]
        unique_link = url[url.rfind("/") + 1:] + "\n"
        if unique_link == recommendations[i]:
            matches += 1
            precision += matches / (i + 1)
    avg_precision: float = precision / matches
    precision: float = matches / num_of_urls
    print("AVG PRECISION: {0}".format(avg_precision))
    print("PRECISION: {0}".format(precision))


if __name__ == '__main__':
    before_create_dict = time.time()
    if os.path.exists("output/book_dict.pickle"):
        with open("output/book_dict.pickle", "rb") as book_dict_file:
            book_dict: Dict[str, Dict[str, List[str] or str]] = pickle.load(book_dict_file)
            after_create_dict = time.time()
    else:
        book_dict: Dict[str, Dict[str, List[str] or str]] = create_dict()
        after_create_dict = time.time()
        with open("output/book_dict.pickle", "wb") as book_dict_file:
            pickle.dump(book_dict, book_dict_file)
    print("Book dictionary created. Time passed: {0}".format(after_create_dict - before_create_dict))

    query_url: str = sys.argv[1]  # Takes the input
    unique_part = query_url[query_url.rfind("/") + 1:] + "\n"
    if unique_part not in book_dict:
        fetched_data = extract_data_from_url(query_url, True)
        print("Query url: {0} is not in the dictionary".format(query_url))
        book_dict[fetched_data[0]] = {"title": fetched_data[1]}
        book_dict[fetched_data[0]]["authors"] = fetched_data[2]
        book_dict[fetched_data[0]]["tokens"] = fetched_data[3]
        book_dict[fetched_data[0]]["recommendations"] = fetched_data[4]
        book_dict[fetched_data[0]]["genres"] = fetched_data[5]
        print("Query url: {0} is added to the dictionary.".format(query_url))
    else:
        extract_data_from_url(query_url, True, True)
        print("Query url: {0} is found in the dictionary!".format(query_url))
    recommended_urls: List[str] = book_dict[unique_part]["recommendations"]

    genre_tf_dict: Dict[str, Dict[str, float]] = {}
    tf_dict: Dict[str, Tuple[Dict[str, float], str]] = {}
    for unique_link in book_dict:
        genre_tf_dict[unique_link] = calculate_tf_weight(book_dict[unique_link]["genres"])
        tf_dict[unique_link] = (calculate_tf_weight(book_dict[unique_link]["tokens"]), book_dict[unique_link]["title"])

    df_dict, genre_df_dict = calculate_df(book_dict)

    idf_dict: Dict[str, float] = calculate_idf(df_dict, len(book_dict))
    genre_idf_dict: Dict[str, float] = calculate_idf(genre_df_dict, len(book_dict))

    score_dict: Dict[str, Tuple[Dict[str, float], str]] = calculate_score(tf_dict, idf_dict)
    genre_score_dict: Dict[str, Dict[str, float]] = genre_calculate_score(genre_tf_dict, genre_idf_dict)

    normalized_dict: Dict[str, Tuple[Dict[str, float], str]] = calculate_normalization(score_dict)
    genre_normalized_dict: Dict[str, Dict[str, float]] = genre_calculate_normalization(genre_score_dict)

    try:
        value_results, title_authors = calculate_similarity(unique_part, book_dict, normalized_dict,
                                                            genre_normalized_dict)
        recommendations: List[str] = sorted(value_results, key=value_results.get, reverse=True)[:18]
        recommend_books(recommendations, title_authors)
        try:
            calculate_precision(recommended_urls, recommendations)
        except ZeroDivisionError as ex:
            logging.error("No matches founded for the value of alpha {0}".format(ALPHA))
    except Exception as ex:
        logging.error("Error happened while calculating the similarity results of query url: {0}{1}".format(query_url,
                                                                                                            ex))
