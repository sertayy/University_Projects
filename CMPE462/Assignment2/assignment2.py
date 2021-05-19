"""
Author: Sertay Akpinar
Date: 19.05.2021
"""
import logging
import sys
import pandas as pd
import numpy as np
import time
from matplotlib import pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
EPOCHS = 15
ITERATION_M = 3500
STEP_SIZES = [0.1, 0.5, 0.9]
K_FOLD = 5


def predict_values(X, Y, W):
    train_acc = []
    test_acc = []
    for i in range(K_FOLD):
        piece = int(len(X) / K_FOLD)
        training_X = np.concatenate((X[:len(X) - piece*(i+1), :], X[len(X) - piece*i:, :]))
        test_X = X[len(X) - piece*(i+1):len(X) - piece*i, :]
        training_Y = np.concatenate((Y[:len(Y) - piece*(i+1)], Y[len(Y) - piece*i:]))
        test_Y = Y[len(Y) - piece*(i+1):len(Y) - piece*i]
        train_prediction = training_X.dot(W)
        test_prediction = test_X.dot(W)
        acc = 0
        for j in range(len(training_Y)):
            if (training_Y[j] == 1 and train_prediction[j] > 0) or (training_Y[j] == -1 and train_prediction[j] < 0):
                acc += 1
        train_acc.append(acc / len(training_Y))
        acc = 0
        for j in range(len(test_Y)):
            if (test_Y[j] == 1 and test_prediction[j] > 0) or (test_Y[j] == -1 and test_prediction[j] < 0):
                acc += 1
        test_acc.append(acc / len(test_Y))

    return sum(train_acc) / len(train_acc), sum(test_acc) / len(test_acc)


def plot_all_in_one_graph(errors_list, step_num):
    if step_num == 1:
        plt.title("Full Batch Gradient Descent")
    else:
        plt.title("Mini Batch Stochastic Gradient Descent")
    plt.xlabel('Iteration')
    plt.ylabel('Loss')
    plt.plot(errors_list[0], color="#0000FF", label="Step Size = {0}".format(STEP_SIZES[0]))
    plt.plot(errors_list[1], color="#FFFF00", label="Step Size = {0}".format(STEP_SIZES[1]))
    plt.plot(errors_list[2], color="#FF0000", label="Step Size = {0}".format(STEP_SIZES[2]))
    plt.legend(loc='upper right')
    plt.savefig('output/part1_step{0}.png'.format(step_num), bbox_inches='tight')


def output_results(n, iter_m, time_spent, train_acc, test_acc):
    print("------ Step Size = {0} ------".format(n))
    print("Number of iterations: {0}".format(iter_m))
    print("Time spent: {:.2f}".format(time_spent))
    print("Train accuracy: {0}".format(train_acc))
    print("Test accuracy: {0}".format(test_acc))


def log_regression(X, Y, step_num):
    errors_list = []
    for n in STEP_SIZES:
        if step_num == 2:
            errors, W, iter_m, time_spent = stochastic_batch_gd(X, Y, n)
        else:
            errors, W, iter_m, time_spent = full_batch_gd(X, Y, n)
        train_acc, test_acc = predict_values(X, Y, W)
        output_results(n, iter_m, time_spent, train_acc, test_acc)
        errors_list.append(errors)
    plot_all_in_one_graph(errors_list, step_num)


def calc_gradient(xn, yn, w):
    return yn * xn.dot(1 / (1 + np.exp(yn * w.T.dot(xn))))


def calc_error(xn, yn, w):
    return np.log(1 + np.exp(-yn * w.T.dot(xn)))


def full_batch_gd(X, Y, n):
    row_count = X.shape[0]
    W = np.zeros(X.shape[1], dtype=float)
    err_list = []
    iteration_m = 0
    begin = time.time()
    for i in range(ITERATION_M):  # should be changed to 'while True:' if you want see the convergence difference between steps
        iteration_m += 1
        G = 0
        err = 0
        for j in range(row_count):
            G += calc_gradient(X[j], Y[j], W)
            err += calc_error(X[j], Y[j], W)
        err_list.append(err / row_count)
        W += n * (G / row_count)
        if len(err_list) != 1 and abs(err_list[-1] - err_list[-2]) < 0.00001:
            break
    end = time.time()
    return err_list, W, iteration_m, end - begin


def stochastic_batch_gd(X, Y, n):
    mini_batch_size = 20
    W = np.zeros(X.shape[1], dtype=float)
    row_count = X.shape[0]
    data = np.insert(X, X.shape[1], values=Y, axis=1)
    err_list = []
    num_of_batches = int(row_count / mini_batch_size)
    mod = row_count % num_of_batches
    if mod != 0:
        last_batch = data[-mod:, :]
        data = data[:-mod, :]
        batches = np.split(data, num_of_batches)
        batches.append(last_batch)
    else:
        batches = np.split(data, num_of_batches)
    is_finished = False
    iteration_m = 0
    begin = time.time()
    for i in range(EPOCHS):  # 'should be changed to while True:' if you want see the convergence difference between steps
        iteration_m += 1
        if is_finished:
            break
        np.random.shuffle(batches)
        for i in range(len(batches)):
            G = 0
            err = 0
            for j in range(len(batches[i])):
                G += calc_gradient(batches[i][j][:-1], int(batches[i][j][-1:]), W)
                err += calc_error(batches[i][j][:-1], int(batches[i][j][-1:]), W)
            err_list.append(err / len(batches[i]))
            W += n * (G / len(batches[i]))
            if len(err_list) != 1 and abs(err_list[-1] - err_list[-2]) < 0.00001:
                is_finished = True
                break
    end = time.time()
    return err_list, W, iteration_m, end - begin


def normalize_df():
    vehicle_df = pd.read_csv("input/vehicle.csv")
    vehicle_df = vehicle_df[vehicle_df["Class"].isin(["saab", "van"])].reset_index().drop('index', axis=1)
    for column in vehicle_df.columns[:-1]:
        vehicle_df[column] = (vehicle_df[column] - vehicle_df[column].min()) / (vehicle_df[column].max()
                                                                                - vehicle_df[column].min())
    Y = vehicle_df["Class"].map({"saab": 1, "van": -1}).to_numpy()
    X = vehicle_df.drop(['Class'], axis=1).to_numpy()
    return X, Y


def part1(step_num):
    X, Y = normalize_df()
    if step_num == "step1":
        log_regression(X, Y, 1)
    elif step_num == "step2":
        log_regression(X, Y, 2)
    else:
        log_helper()


def log_helper():
    logger.error("Wrong commands...")
    logger.info("Command format: python3 assignment1.py part<n> step<n>")


if __name__ == "__main__":
    part_num = sys.argv[1]
    step_num = sys.argv[2]
    if part_num == "part1":
        part1(step_num)
    else:
        log_helper()
