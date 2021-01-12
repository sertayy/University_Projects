import math
import pickle
from urllib.request import urlopen
import re
from typing import List, Dict, Tuple
import logging
import string
import time
import collections
import os
import sys
from multiprocessing.pool import ThreadPool


def stop_word_list() -> List[str]:
    with open("input/stop_words.txt", "r") as stop_word_file:
        return stop_word_file.read().splitlines()


PUNCTUATIONS: List[str] = list(string.punctuation + "—…’")
STOP_WORDS: List[str] = stop_word_list()


def extract_data_from_url(url: str, is_query: bool = False) -> (str, str, List[str], List[str], List[str], List[str]):
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

        # TODO Illustrator?
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
    """Creates the book dictionary."""
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
    score_dict: Dict[str, float] = {}
    doc_freq: Dict[str, int] = dict(collections.Counter(tokens))
    for token in tokens:
        score_dict[token] = 1.0 + math.log(doc_freq[token])
    return score_dict


def calculate_df(book_dict) -> (Dict[str, int], Dict[str, int]):
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
    idf_dict: Dict[str, float] = {}
    for token in df_dict:
        idf_dict[token] = math.log(num_of_books / df_dict[token])
    return idf_dict


def genre_calculate_score(tf_dict: Dict[str, Dict[str, float]], idf_dict: Dict[str, float]) \
        -> Dict[str, Dict[str, float]]:
    for book_title in tf_dict:
        for token in tf_dict[book_title]:
            idf_value: float = idf_dict[token]
            tf_value: float = tf_dict[book_title][token]
            tf_dict[book_title][token] = idf_value * tf_value
            # tf_dict now keeps the score of the token instead of tf value
    return tf_dict


def calculate_score(tf_dict: Dict[str, Tuple[Dict[str, float], str]], idf_dict: Dict[str, float]) \
        -> Dict[str, Tuple[Dict[str, float], str]]:
    for unique_link in tf_dict:
        for token in tf_dict[unique_link][0]:
            idf_value: float = idf_dict[token]
            tf_value: float = tf_dict[unique_link][0][token]
            tf_dict[unique_link][0][token] = idf_value * tf_value
            # tf_dict now keeps the score of the token instead of tf value
    return tf_dict


def genre_calculate_normalization(score_dict: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
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


def cosine_simularity(query_scores: Dict[str, float], book_score: Dict[str, float]) -> float:
    val: float = 0
    for token in query_scores:
        if token in book_score:
            val += query_scores[token] * book_score[token]
    return val


def calculate_simularity(query_link: str, book_dict: Dict[str, Dict[str, List[str] or str]],
                         normalized_dict: Dict[str, Tuple[Dict[str, float], str]],
                         genre_normalized_dict: Dict[str, Dict[str, float]]) \
        -> (Dict[str, list], Dict[str, Tuple[str, List[str]]]):
    value_results: Dict[str, float] = {}
    title_authors: Dict[str, Tuple[str, List[str]]] = {}
    alfa: float = 0.75
    for unique_link in book_dict:
        if unique_link != query_link:
            desc_sim: float = cosine_simularity(normalized_dict[query_link][0], normalized_dict[unique_link][0])
            genre_sim: float = cosine_simularity(genre_normalized_dict[query_link],
                                                 genre_normalized_dict[unique_link])
            sim_value: float = alfa * desc_sim + (1 - alfa) * genre_sim
            value_results[unique_link] = sim_value
            title_authors[unique_link] = (book_dict[unique_link]["title"], book_dict[unique_link]["authors"])
    return value_results, title_authors


def recommend_books(results: Dict[str, float], title_authors: Dict[str, Tuple[str, List[str]]]):
    recommendations: List[str] = sorted(results, key=results.get, reverse=True)[:18]
    print("Readers also enjoyed:")
    for unique_link in recommendations:
        pair: Tuple[str, List[str]] = title_authors[unique_link]
        print("{0} --- {1}".format(pair[0], str(pair[1])[1:-1]))


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

    query_url: str = sys.argv[1]
    unique_part = query_url[query_url.rfind("/") + 1:] + "\n"
    fetched_data = extract_data_from_url(query_url, True)
    if unique_part not in book_dict:
        print("Query url: {0} is not in the dictionary".format(query_url))
        book_dict[fetched_data[0]] = {"title": fetched_data[1]}
        book_dict[fetched_data[0]]["authors"] = fetched_data[2]
        book_dict[fetched_data[0]]["tokens"] = fetched_data[3]
        book_dict[fetched_data[0]]["recommendations"] = fetched_data[4]
        book_dict[fetched_data[0]]["genres"] = fetched_data[5]
        print("Query url: {0} is added to the dictionary.".format(query_url))
    else:
        print("Query url: {0} is found in the dictionary!".format(query_url))



    genre_tf_dict: Dict[str, Dict[str, float]] = {}
    tf_dict: Dict[str, Tuple[Dict[str, float], str]] = {}
    for unique_link in book_dict:
        genre_tf_dict[unique_link] = calculate_tf_weight(book_dict[unique_link]["genres"])
        tf_dict[unique_link] = (calculate_tf_weight(book_dict[unique_link]["tokens"]), book_dict[unique_link]["title"])
        # {unique_linnk: ({token: tf}, title)} Dict[str, Tuple[Dict[str, float], str]

    # book_vs_tokens = {dict.fromkeys(book_dict): book_dict["tokens"]} df için böyle bir şey oluşturabilirsin
    df_dict, genre_df_dict = calculate_df(book_dict)

    idf_dict: Dict[str, float] = calculate_idf(df_dict, len(book_dict))
    genre_idf_dict: Dict[str, float] = calculate_idf(genre_df_dict, len(book_dict))

    score_dict: Dict[str, Tuple[Dict[str, float], str]] = calculate_score(tf_dict, idf_dict)
    genre_score_dict: Dict[str, Dict[str, float]] = genre_calculate_score(genre_tf_dict, genre_idf_dict)

    normalized_dict: Dict[str, Tuple[Dict[str, float], str]] = calculate_normalization(score_dict)
    genre_normalized_dict: Dict[str, Dict[str, float]] = genre_calculate_normalization(genre_score_dict)

    try:
        value_results, title_authors = calculate_simularity(unique_part, book_dict, normalized_dict,
                                                            genre_normalized_dict)
        recommend_books(value_results, title_authors)
    except Exception as ex:
        logging.error(
"Error happened while calculating the simularity results of query url: {0}{1}".format(query_url, ex))
