import os
import collections
from typing import Dict, List
from math import log
from random import randint


def extract_data(directory: str, is_test: bool = False) -> (List[str], Dict[str, int], Dict[str, int], List[str],
                                                            List[str], Dict[str, int], Dict[str, int]) or \
                                                           (Dict[str, List[str]], Dict[str, List[str]]):
    test_leg_tokens: Dict[str, List[str]] = {}
    test_spam_tokens: Dict[str, List[str]] = {}
    legitimate_tokens: List[str] = []
    spam_tokens: List[str] = []
    leg_files_path: str = "./dataset/" + directory + "/legitimate/"
    spam_files_path: str = "./dataset/" + directory + "/spam/"
    leg_unique_tokens: List[str] = []  # per document for MI
    spam_unique_tokens: List[str] = []  # per document for MI

    for file in os.listdir(leg_files_path):
        try:
            with open(leg_files_path + file, "rb") as in_file:
                data_str: str = in_file.read().decode("utf-8")[8:]
                tokens = data_str.split()
                legitimate_tokens += tokens
                if is_test:
                    test_leg_tokens[file] = tokens
                leg_unique_tokens += list(set(tokens))  # for mutual info
        except UnicodeDecodeError as ex:
            print('\033[91m' + "(EXCEPTION HANDLED) --> An error occured while reading file: training/legitimate/{0} "
                               "--> {1}".format(file, ex) + '\033[0m')

    for file in os.listdir(spam_files_path):
        try:
            with open(spam_files_path + file, "rb") as in_file:
                data_str: str = in_file.read().decode("utf-8")[8:]
                tokens = data_str.split()
                spam_tokens += tokens
                if is_test:
                    test_spam_tokens[file] = tokens
                # for mutual info
                spam_unique_tokens += list(set(tokens))
        except UnicodeDecodeError as ex:
            print('\033[91m' + "(EXCEPTION HANDLED) --> An error occured while reading file: training/spam/{0} --> {1}"
                  .format(file, ex) + '\033[0m')

    if is_test:
        return test_leg_tokens, test_spam_tokens
    legitimate_token_freq: Dict[str, int] = dict(collections.Counter(legitimate_tokens))
    spam_token_freq: Dict[str, int] = dict(collections.Counter(spam_tokens))
    leg_doc_frequency: Dict[str, int] = dict(collections.Counter(leg_unique_tokens))
    spam_doc_frequency: Dict[str, int] = dict(collections.Counter(spam_unique_tokens))
    vocab: List[str] = legitimate_tokens + spam_tokens

    return vocab, legitimate_token_freq, spam_token_freq, legitimate_tokens, spam_tokens, leg_doc_frequency, \
           spam_doc_frequency


def conditional_probabilities(vocab: List[str], legitimate_token_freq: Dict[str, int], spam_token_freq: Dict[str, int],
                              total_leg_tokens: int, total_spam_tokens: int) -> (Dict[str, float], Dict[str, float]):
    legit_tokens_prob: Dict[str, float] = {}
    spam_tokens_prob: Dict[str, float] = {}
    vocab = list(set(vocab))
    vocab_size = len(vocab)
    leg_denominator = total_leg_tokens + vocab_size
    spam_denominator = total_spam_tokens + vocab_size
    for token in vocab:
        if token in legitimate_token_freq:
            legit_tokens_prob[token] = (legitimate_token_freq[token] + 1) / leg_denominator
        else:
            legit_tokens_prob[token] = 1 / leg_denominator
        if token in spam_token_freq:
            spam_tokens_prob[token] = (spam_token_freq[token] + 1) / spam_denominator
        else:
            spam_tokens_prob[token] = 1 / spam_denominator

    return legit_tokens_prob, spam_tokens_prob


def calculate_accuracy(leg_file_tokens: Dict[str, List[str]], spam_file_tokens: Dict[str, List[str]],
                       legit_tokens_prob: Dict[str, float], spam_tokens_prob: Dict[str, float], is_randomization=False):
    prior_prob: float = log(0.5)  # since the files are distributed equally
    correct_count: int = 0
    leg_asserted: int = 0
    spam_asserted: int = 0

    classification_dict = {}
    for file_name in leg_file_tokens:  # legimitate cikarsa dogru tahmin
        leg_prob = prior_prob
        spam_prob = prior_prob
        for token in leg_file_tokens[file_name]:
            if token in legit_tokens_prob:
                leg_prob += log(legit_tokens_prob[token])
            if token in spam_tokens_prob:
                spam_prob += log(spam_tokens_prob[token])
        if spam_prob < leg_prob:
            classification_dict[file_name] = 1  # legitimate
            correct_count += 1
        else:
            classification_dict[file_name] = 0  # spam
            spam_asserted += 1
    leg_corrects = correct_count

    for file_name in spam_file_tokens:
        leg_prob = prior_prob
        spam_prob = prior_prob
        for token in spam_file_tokens[file_name]:
            if token in legit_tokens_prob:
                leg_prob += log(legit_tokens_prob[token])
            if token in spam_tokens_prob:
                spam_prob += log(spam_tokens_prob[token])
        if spam_prob > leg_prob:
            classification_dict[file_name] = 0  # spam
            correct_count += 1
        else:
            classification_dict[file_name] = 1  # legitimate
            leg_asserted += 1

    spam_corrects = correct_count - leg_corrects
    leg_prec = leg_corrects / 240
    spam_prec = spam_corrects / 240
    leg_recall = leg_corrects / (leg_corrects + leg_asserted)
    spam_recall = spam_corrects / (spam_corrects + spam_asserted)
    avg_recall = (leg_recall + spam_recall) / 2
    leg_f = (2 * leg_prec * leg_recall) / (leg_prec + leg_recall)
    spam_f = (2 * spam_prec * spam_recall) / (spam_prec + spam_recall)

    if not is_randomization:
        print("Macro-averaged precision: {0}".format((leg_prec + spam_prec) / 2))
        print("Macro-averaged recall: {0}".format(avg_recall))
        print("Macro-averaged F-measure: {0}".format((leg_f + spam_f) / 2))
        print("Precision of legitimate class: {0}".format(leg_prec))
        print("Recall of legitimate class: {0}".format(leg_recall))
        print("F-Measure of legitimate class: {0}".format(leg_f))
        print("Precision of spam class: {0}".format(spam_prec))
        print("Recall of spam class: {0}".format(spam_recall))
        print("F-Measure of spam class: {0}".format(spam_f))

    return (leg_f + spam_f) / 2, classification_dict


def mutual_info(vocabulary: List[str], leg_doc_frequency: Dict[str, int], spam_doc_frequency: Dict[str, int],
                legitimate_tokens, spam_tokens):
    mi_value_dict: Dict[str, float] = {}
    i_value: float
    for token in vocabulary:
        i_value = 0
        if token in spam_doc_frequency:
            spam_class_freq = spam_doc_frequency[token]
        else:
            spam_class_freq = 0
        if token in leg_doc_frequency:
            leg_class_freq = leg_doc_frequency[token]
        else:
            leg_class_freq = 0

        if leg_class_freq != 0:
            i_value += (leg_class_freq / 480) * log((480 * leg_class_freq) / ((leg_class_freq + spam_class_freq) * 240))
        i_value += ((240 - leg_class_freq) / 480) * log((480 * (240 - leg_class_freq)) /
                                                        (((240 - leg_class_freq) + (240 - spam_class_freq)) * 240))
        if spam_class_freq != 0:
            i_value += (spam_class_freq / 480) * log((480 * spam_class_freq) /
                                                     ((leg_class_freq + spam_class_freq) * 240))
        i_value += ((240 - spam_class_freq) / 480) * log((480 * (240 - spam_class_freq)) /
                                                         (((240 - leg_class_freq) + (240 - spam_class_freq)) * 240))
        mi_value_dict[token] = i_value

    mi_value_dict = dict(collections.Counter(mi_value_dict).most_common(100))

    keys_mi_dict = list(mi_value_dict.keys())
    update_vocab = []
    update_leg_tokens = []
    update_spam_tokens = []
    for token in vocabulary:
        if token in keys_mi_dict:
            update_vocab.append(token)

    for token in legitimate_tokens:
        if token in keys_mi_dict:
            update_leg_tokens.append(token)

    for token in spam_tokens:
        if token in keys_mi_dict:
            update_spam_tokens.append(token)

    return update_vocab, update_leg_tokens, update_spam_tokens


def shuffle(classify_dict, mi_classify_dict, leg_file_names):
    """Shuffles the two versions"""
    leg_correct_count: int = 0
    spam_correct_count: int = 0
    leg_asserted: int = 0
    spam_asserted: int = 0
    mi_leg_correct_count: int = 0
    mi_spam_correct_count: int = 0
    mi_leg_asserted: int = 0
    mi_spam_asserted: int = 0
    for file_name in classify_dict:
        if randint(0, 1) == 1:
            temp = classify_dict[file_name]
            classify_dict[file_name] = mi_classify_dict[file_name]
            mi_classify_dict[file_name] = temp

    for file_name in mi_classify_dict:
        if file_name in leg_file_names:
            if mi_classify_dict[file_name] == 1:
                mi_leg_correct_count += 1
            else:
                mi_spam_asserted += 1
        else:  #
            if mi_classify_dict[file_name] == 0:
                mi_spam_correct_count += 1
            else:
                mi_leg_asserted += 1

    # regular
    for file_name in classify_dict:
        if file_name in leg_file_names:
            if classify_dict[file_name] == 1:
                leg_correct_count += 1
            else:
                spam_asserted += 1
        else:  # spam olmalı
            if classify_dict[file_name] == 0:
                spam_correct_count += 1
            else:
                leg_asserted += 1

    # for allword calc.
    leg_prec = leg_correct_count / 240
    spam_prec = spam_correct_count / 240
    leg_recall = leg_correct_count / (leg_correct_count + leg_asserted)
    spam_recall = spam_correct_count / (spam_correct_count + spam_asserted)
    # avg_recall = (leg_recall + spam_recall) / 2
    leg_f = (2 * leg_prec * leg_recall) / (leg_prec + leg_recall)
    spam_f = (2 * spam_prec * spam_recall) / (spam_prec + spam_recall)
    avg_f = (leg_f + spam_f) / 2

    # for mi calc.
    mi_leg_prec = mi_leg_correct_count / 240
    mi_spam_prec = mi_spam_correct_count / 240
    mi_leg_recall = mi_leg_correct_count / (mi_leg_correct_count + mi_leg_asserted)
    mi_spam_recall = mi_spam_correct_count / (mi_spam_correct_count + mi_spam_asserted)
    # mi_avg_recall = (mi_leg_recall + mi_spam_recall) / 2
    mi_leg_f = (2 * mi_leg_prec * mi_leg_recall) / (mi_leg_prec + mi_leg_recall)
    mi_spam_f = (2 * mi_spam_prec * mi_spam_recall) / (mi_spam_prec + mi_spam_recall)
    mi_avg_f = (mi_leg_f + mi_spam_f) / 2

    return abs(mi_avg_f - avg_f)


if __name__ == "__main__":
    # PART 1
    vocabulary, legitimate_token_freq, spam_token_freq, legitimate_tokens, spam_tokens, leg_doc_frequency, \
    spam_doc_frequency = extract_data("training")
    legit_tokens_prob, spam_tokens_prob = conditional_probabilities(vocabulary, legitimate_token_freq, spam_token_freq,
                                                                    len(legitimate_tokens), len(spam_tokens))
    test_leg_tokens, test_spam_tokens = extract_data("test", True)

    print('\033[32m' + "METHOD: ALL WORDS" + '\033[0m')
    f_measure, classify_dict = calculate_accuracy(test_leg_tokens, test_spam_tokens, legit_tokens_prob,
                                                  spam_tokens_prob)
    # PART 2
    vocabulary, update_leg_tokens, update_spam_tokens = mutual_info(vocabulary, leg_doc_frequency, spam_doc_frequency,
                                                                    legitimate_tokens, spam_tokens)
    mi_legit_tokens_prob, mi_spam_tokens_prob = conditional_probabilities(vocabulary, legitimate_token_freq,
                                                                          spam_token_freq, len(update_leg_tokens),
                                                                          len(update_spam_tokens))
    print('\033[32m' + "METHOD: MUTUAL INFORMATION" + '\033[0m')
    mi_f_measure, mi_classify_dict = calculate_accuracy(test_leg_tokens, test_spam_tokens, mi_legit_tokens_prob,
                                                        mi_spam_tokens_prob)

    diff_f = abs(f_measure - mi_f_measure)
    print("Difference of the F-measure values: {0}".format(diff_f))

    # RANDOMIZATION
    counter = 0
    for i in range(1000):
        f_measure, classify_dict = calculate_accuracy(test_leg_tokens, test_spam_tokens, legit_tokens_prob,
                                                      spam_tokens_prob, True)
        mi_f_measure, mi_classify_dict = calculate_accuracy(test_leg_tokens, test_spam_tokens, mi_legit_tokens_prob,
                                                            mi_spam_tokens_prob, True)

        new_diff_f = shuffle(classify_dict, mi_classify_dict, list(test_leg_tokens.keys()))

        if new_diff_f >= diff_f:
            counter += 1

    p_value = (counter + 1) / 1001

    print("Randomization test for R = 1000")
    print('\033[32m' + "P-value is: {0}".format(p_value) + '\033[0m')
