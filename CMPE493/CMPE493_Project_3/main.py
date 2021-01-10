import math
from urllib.request import urlopen
import re
from typing import List, Dict
import logging
import string
import time
import collections


def stop_word_list() -> List[str]:
    with open("input/stop_words.txt", "r") as stop_word_file:
        return stop_word_file.read().splitlines()


PUNCTUATIONS: List[str] = list(string.punctuation)
STOP_WORDS: List[str] = stop_word_list()


def extract_data_from_url(url: str, is_query: bool) -> (str, List[str], List[str], List[str], List[str]) or str:
    is_valid: bool = True
    with urlopen(url) as data:
        info = data.read().decode("utf-8")
        title: str = re.findall("<title>(.*?)</title>", info)[0]
        if is_query:
            return title
        author_list: List[str] = re.findall("<span itemprop=\"name\">(.*?)</span>", info)
        description: str = re.findall("display:none\">(.*?)</span>",
                                      info)[0]
        if "<br /><br />" in description:
            description = description.replace("<br /><br />", "\n")
        recommanded_part = info.strip().split('<div class=\'carouselRow\' style=\'width: 3600px\'>')[1].split('</div>')[
            0]
        recommended_book_urls: List[str] = re.findall("'>\n<a href=\"(.*?)\"><img alt=\"", recommanded_part)
        genres: List[str] = re.findall('<a class="actionLinkLite bookPageGenreLink" href="/genres/(.*?)">', info)

        if title.strip() == "" or title is None:
            logging.error("Title is not valid for url: {0}".format(url))
            is_valid = False
        if author_list == [] or author_list is None:
            logging.error("Author list is not valid for url: {0}".format(url))
            is_valid = False
        if description.strip() == "" or description is None or len(description) < 15:
            logging.error("Description is not valid for url: {0}".format(url))
            print("Description is " + str(description) + " .")
            is_valid = False
        if recommended_book_urls == [] or recommended_book_urls is None:
            logging.error("Recommended books are not valid for url: {0}".format(url))
            is_valid = False
        if genres == [] or genres is None:
            logging.error("Genres are not valid for url: {0}".format(url))
            is_valid = False
        if is_valid:
            try:
                tokens: List[str] = tokenize(description)
            except Exception as ex:
                logging.error("Error happened while tokenizing.")
                raise ex
            return title, author_list, tokens, recommended_book_urls, genres


def tokenize(description: str) -> List[str]:
    tokens: List[str] = []
    description = description.lower()
    for punctuation in PUNCTUATIONS:
        if punctuation == ".":
            description = description.replace(punctuation, "")
            continue
        description = description.replace(punctuation, " ")
    description_words: List[str] = description.split()

    for word in description_words:
        if word not in STOP_WORDS and (word.isnumeric() or len(word) > 1):
            if len(word) > 3:
                if len(word) > 4 and word.endswith("ing"):  # TODO ing not efficient
                    word = word[:-3]
                elif word.endswith("ies"):
                    word.replace("ies", "y")
                elif len(word) > 4 and word.endswith("sses"):
                    word = word[:-2]
                elif word.endswith("s") and not word.endswith("ss"):
                    word = word[:-1]
            tokens.append(word)

    return tokens


def create_dict() -> Dict[str, Dict[str, List[str]]]:
    """Creates the book dictionary."""

    book_dict: Dict[str, Dict[str, List[str]]] = {}

    with open("input/books.txt", "r") as file:
        count = 0
        for url in file:
            try:
                title, author_list, tokens, recommended_book_urls, genres = extract_data_from_url(url.rstrip(), False)
            except Exception as ex:
                logging.error("Error happened in url: {0}{1}".format(url, ex))
                continue
            book_dict[title] = {"authors": author_list}
            book_dict[title]["tokens"] = tokens
            book_dict[title]["recommendations"] = recommended_book_urls
            book_dict[title]["genres"] = genres
            count += 1
            if count == 250:
                break
            if count in [250, 500, 750, 1000, 1250, 1500, 1750]:
                print("Count is --> {0}".format(count))

    if count == 1800:
        print("Done!")

    return book_dict


def calculate_tf_weight(tokens: List[str]) -> Dict[str, float]:
    score_dict: Dict[str, float] = {}
    doc_freq: Dict[str, int] = dict(collections.Counter(tokens))
    for token in tokens:
        score_dict[token] = 1.0 + math.log(doc_freq[token])
    return score_dict


def calculate_df(book_dict: Dict[str, Dict[str, List[str]]]) -> (Dict[str, int], Dict[str, int]):
    token_df_dict: Dict[str, int] = {}  # {token: doc. freq.}
    genre_df_dict: Dict[str, int] = {}
    for book in book_dict:
        token_set = list(set(book_dict[book]["tokens"]))
        genre_set = list(set(book_dict[book]["genres"]))
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


def calculate_score(tf_dict: Dict[str, Dict[str, float]], idf_dict: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    for book_title in tf_dict:
        for token in tf_dict[book_title]:
            idf_value: float = idf_dict[token]
            tf_value: float = tf_dict[book_title][token]
            tf_dict[book_title][token] = idf_value * tf_value
            # tf_dict now keeps the score of the token instead of tf value
    return tf_dict


def calculate_normalization(score_dict: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
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


def cosine_simularity(query_scores: Dict[str, float], book_score: Dict[str, float]) -> float:
    val: float = 0
    for token in query_scores:
        if token in book_score:
            val += query_scores[token] * book_score[token]
    return val


def calculate_simularity(title: str, book_dict: Dict[str, Dict[str, List[str]]],
                         normalized_dict: Dict[str, Dict[str, float]],
                         genre_normalized_dict: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    result_dict: Dict[str, float] = {}
    alfa: float = 0.75
    for book in book_dict:
        if book != title:
            desc_sim: float = cosine_simularity(normalized_dict[title], normalized_dict[book])
            genre_sim: float = cosine_simularity(genre_normalized_dict[title], genre_normalized_dict[book])
            sim_value: float = alfa * desc_sim + (1 - alfa) * genre_sim
            result_dict[book] = sim_value
    return result_dict


def recommend_books(results: Dict[str, float]):
    recommendations: List[str] = sorted(results, key=results.get, reverse=True)[:18]
    print("Readers also enjoyed:")
    for book in recommendations:
        print(book)


if __name__ == '__main__':
    before_create_dict = time.time()
    book_dict: Dict[str, Dict[str, List[str]]] = create_dict()
    print("Book dictionary created. Time passed: {0}".format(time.time() - before_create_dict))

    genre_tf_dict: Dict[str, Dict[str, float]] = {}
    tf_dict: Dict[str, Dict[str, float]] = {}
    for book_title in book_dict:
        genre_tf_dict[book_title] = calculate_tf_weight(book_dict[book_title]["genres"])
        tf_dict[book_title] = calculate_tf_weight(book_dict[book_title]["tokens"])  # {title: {token: tf}}

    # book_vs_tokens = {dict.fromkeys(book_dict): book_dict["tokens"]} df için böyle bir şey oluşturabilirsin
    df_dict, genre_df_dict = calculate_df(book_dict)

    idf_dict: Dict[str, float] = calculate_idf(df_dict, len(book_dict))
    genre_idf_dict: Dict[str, float] = calculate_idf(genre_df_dict, len(book_dict))

    score_dict: Dict[str, Dict[str, float]] = calculate_score(tf_dict, idf_dict)
    genre_score_dict: Dict[str, Dict[str, float]] = calculate_score(genre_tf_dict, genre_idf_dict)

    normalized_dict: Dict[str, Dict[str, float]] = calculate_normalization(score_dict)
    genre_normalized_dict: Dict[str, Dict[str, float]] = calculate_normalization(genre_score_dict)

    query_url = "https://www.goodreads.com/book/show/4894.Who_Moved_My_Cheese_"
    simularity_results: Dict[str, float] = calculate_simularity(extract_data_from_url(query_url, True), book_dict,
                                                                normalized_dict, genre_normalized_dict)
    recommend_books(simularity_results)
    print("DONE!")
