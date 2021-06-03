import logging
import sys
import pandas as pd
from math import log2
from typing import List
from libsvm.svmutil import *
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NUM_OF_SAMPLES = 80
MAX_DEPTH = 6
KERNEL_TYPES = {
    0: "linear",
    1: "polynomial",
    2: "radial basis function",
    3: "sigmoid"
}
C_VALUES = [3, 22, 80, 300, 1000]


class DecisionTree:
    def __init__(self, root, boundary, columns):
        self.root: str = root
        self.boundary = boundary
        self.left_class = None
        self.right_class = None
        self.left_node: pd.DataFrame or DecisionTree = pd.DataFrame(columns=columns)
        self.right_node: pd.DataFrame or DecisionTree = pd.DataFrame(columns=columns)


def calc_entropy(prob1, prob2):
    if prob1 == 0 or prob2 == 0:
        return 0
    return - prob1 * log2(prob1) - prob2 * log2(prob2)


def calc_prob(value_list):
    counter = 0
    for val in value_list:
        if val == 1:
            counter += 1
    return counter / len(value_list)


def calc_entropy_after(tree):
    left_prob1 = calc_prob(tree.left_node['class'])
    right_prob1 = calc_prob(tree.right_node['class'])
    entropy_after = ((len(tree.left_node) / NUM_OF_SAMPLES) * calc_entropy(left_prob1, 1 - left_prob1)
                     + (len(tree.right_node) / NUM_OF_SAMPLES) * calc_entropy(right_prob1, 1 - right_prob1))
    return entropy_after


def gain_ratio(tree, info_gain):
    left_leaf_ratio = len(tree.left_node) / NUM_OF_SAMPLES
    right_leaf_ratio = len(tree.right_node) / NUM_OF_SAMPLES
    ratio = left_leaf_ratio * log2(left_leaf_ratio) + right_leaf_ratio * log2(right_leaf_ratio)
    return info_gain / -ratio


def rec_search(data, entropy_before, step_num):
    info_criteria = 0  # information gain or gain ratio
    result_entropy = None
    chosen_tree = None
    for column in data.columns[1:-1]:
        unique_vals = sorted(list(set(data[column])))[1:-1]  # except min and max values
        for val in unique_vals:
            left_list, right_list = [], []
            tree = DecisionTree(column, val, data.columns)
            for (index, row) in data.iterrows():
                if row.loc[column] < val:
                    left_list.append(row.tolist())
                else:
                    right_list.append(row.tolist())
            tree.left_node = tree.left_node.append(pd.DataFrame(left_list, columns=data.columns), ignore_index=True)
            tree.right_node = tree.right_node.append(pd.DataFrame(right_list, columns=data.columns), ignore_index=True)
            entropy_after = calc_entropy_after(tree)
            info_gain = entropy_before - entropy_after
            if step_num == "step2":
                info_gain = gain_ratio(tree, info_gain)  # actually gain ratio
            if info_criteria < info_gain:
                info_criteria = info_gain
                chosen_tree = tree
                result_entropy = entropy_after
                if result_entropy == 0:  # data is distributed accurately, no need to check for the other thresholds
                    return chosen_tree, result_entropy
    return chosen_tree, result_entropy


def decide_class_node(final_tree):
    counter = 0
    for (index, row) in final_tree.left_node.iterrows():
        if row['class'] == 1:
            counter += 1
    accuracy = counter / len(final_tree.left_node)
    if accuracy > 0.5:
        final_tree.left_class = 1
        final_tree.right_class = 0
    else:
        final_tree.left_class = 0
        final_tree.right_class = 1
    final_tree.left_node = pd.DataFrame(columns=final_tree.left_node.columns)
    final_tree.right_node = pd.DataFrame(columns=final_tree.right_node.columns)
    return final_tree


def apply_dt(train_df: pd.DataFrame, step_num):
    entropy_before = 1
    depth = 0
    fringe: List[pd.DataFrame] = [train_df]  # used in DFS
    final_tree: DecisionTree or None = None
    while True:
        if not fringe:
            break
        data = fringe.pop()
        chosen_tree, entropy_after = rec_search(data, entropy_before, step_num)
        if depth == 0:
            final_tree = chosen_tree
        else:
            if isinstance(final_tree.left_node, pd.DataFrame):
                final_tree.left_node = chosen_tree
            else:
                final_tree.right_node = chosen_tree
        depth += 1
        if entropy_after == 0 or depth == MAX_DEPTH:
            continue
        fringe += [chosen_tree.right_node, chosen_tree.left_node]
    return decide_class_node(final_tree)


def calc_test_acc(trained_dt, test_df):
    counter = 0
    for (index, row) in test_df.iterrows():
        if row[trained_dt.root] < trained_dt.boundary and row['class'] == trained_dt.left_class:
            counter += 1
        elif row[trained_dt.root] >= trained_dt.boundary and row['class'] == trained_dt.right_class:
            counter += 1
    return round(counter / len(test_df), 2)


def normalize_df(df):
    for column in df.columns:
        df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
    return df


def apply_svm(y, x, c_val=None, t_val=None):
    if t_val is None:
        model = svm_train(y, x, '-c {0} -t 0 -q'.format(c_val))
    else:
        model = svm_train(y, x, '-c 3 -t {0} -q'.format(t_val))
    return model


def part1(step_num):
    df = pd.read_csv("input/iris.csv").replace({'class': {'Iris-setosa': 0, 'Iris-versicolor': 1}})
    train_df = df[:40].append(df[50:-10]).reset_index()
    test_df = df[40:50].append(df[-10:]).reset_index()
    if step_num == "step1" or step_num == "step2":
        trained_dt = apply_dt(train_df, step_num)
    else:
        log_helper()
        return
    print("DT {0} {1}".format(trained_dt.root, calc_test_acc(trained_dt, test_df)))


def part2(step_num):
    df = pd.read_csv("input/wbcd.csv").drop(columns='id').replace({'diagnosis': {'M': 0, 'B': 1}})
    train_df = df[:400]
    test_df = df[400:]
    x_test = normalize_df(test_df.drop(columns='diagnosis')).to_numpy()
    y_test = list(test_df['diagnosis'])
    x_train = normalize_df(train_df.drop(columns='diagnosis')).to_numpy()
    y_train = list(train_df['diagnosis'])
    output = ""
    if step_num == "step1":
        for c_val in C_VALUES:
            trained_svm = apply_svm(y_train, x_train, c_val)
            p_acc = svm_predict(y_test, x_test, trained_svm, '-q')[1]
            if c_val == C_VALUES[-1]:
                output += "SVM kernel=linear C={0} acc={1} n={2}".format(c_val, round(p_acc[0], 2),
                                                                         len(trained_svm.get_SV()))
            else:
                output += "SVM kernel=linear C={0} acc={1} n={2}\n".format(c_val, round(p_acc[0], 2),
                                                                           len(trained_svm.get_SV()))
    elif step_num == "step2":
        for i in range(4):
            trained_svm = apply_svm(y_train, x_train, t_val=i)
            p_acc = svm_predict(y_test, x_test, trained_svm, '-q')[1]
            if i == 3:
                output += "SVM kernel={0} C=3 acc={1} n={2}".format(KERNEL_TYPES[i], round(p_acc[0], 2),
                                                                    len(trained_svm.get_SV()))
            else:
                output += "SVM kernel={0} C=3 acc={1} n={2}\n".format(KERNEL_TYPES[i], round(p_acc[0], 2),
                                                                      len(trained_svm.get_SV()))
    else:
        log_helper()
    print(output)


def log_helper():
    logger.error("Wrong commands...")
    logger.info("Command format: python3 assignment1.py part<n> step<n>")


if __name__ == "__main__":
    part_num = sys.argv[1]
    step_num = sys.argv[2]
    if part_num == "part1":
        part1(step_num)
    elif part_num == "part2":
        part2(step_num)
    else:
        log_helper()
