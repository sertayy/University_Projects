"""
Author: Sertay Akpinar, 27.04.2021
"""
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from numpy.linalg import inv
from math import sqrt
import time
import logging
import sys
import tqdm
import random
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
x_points: np.ndarray = np.ndarray([])
y_points: np.ndarray = np.ndarray([])
c_zero_x = []
c_zero_y = []
c_one_x = []
c_one_y = []
weight = [0, 1, 1]


def classify():
    global c_zero_x, c_zero_y, c_one_x, c_one_y
    c_zero_x = []
    c_zero_y = []
    c_one_x = []
    c_one_y = []
    for i in range(len(x_points)):
        x_val = x_points[i]
        y_val = y_points[i]
        if y_points[i] < (-3 * x_val + 1):
            c_zero_x.append(x_val)
            c_zero_y.append(y_val)
        elif y_points[i] > (-3 * x_val + 1):
            c_one_x.append(x_val)
            c_one_y.append(y_val)


def pla():
    weight_vec = weight
    iteration = 0
    while True:
        iteration += 1
        is_misclassified = False
        for i in range(len(c_zero_x)):
            weight_vec = np.array(weight_vec)
            result = weight_vec.T.dot(np.array([1, c_zero_x[i], c_zero_y[i]]))
            if result > 0:
                weight_vec[0] += (-1) * 1
                weight_vec[1] += (-1) * c_zero_x[i]
                weight_vec[2] += (-1) * c_zero_y[i]
                if not is_misclassified:
                    is_misclassified = True
        for i in range(len(c_one_x)):
            weight_vec = np.array(weight_vec)
            result = weight_vec.T.dot(np.array([1, c_one_x[i], c_one_y[i]]))
            if result < 0:
                weight_vec[0] += 1
                weight_vec[1] += c_one_x[i]
                weight_vec[2] += c_one_y[i]
                if not is_misclassified:
                    is_misclassified = True
        if not is_misclassified:
            return iteration, weight_vec


def generate_random_points(range_size, size):
    global x_points, y_points
    x_list = []
    y_list = []
    for i in range(1, size+1):
        while True:
            rand_val = random.randint(1, range_size)
            if rand_val not in x_list:
                x_list.append(rand_val)
                break
    for i in range(1, size+1):
        while True:
            rand_val = random.randint(-3*range_size+1, -2)
            """if i == size:
                pass"""
            if rand_val != -3*x_list[i-1]+1:
                y_list.append(rand_val)
                break
    x_points = np.array(x_list)
    y_points = np.array(y_list)


def show_graph(weight, part_num, step_num):
    new_y_points = (-weight[1] / weight[2]) * x_points + (-weight[0] / weight[2]) * 1
    plt.xlabel('Y - axis')
    plt.ylabel('X - axis')
    plt.title("Part {0} & Step {1}".format(part_num, step_num))
    plt.plot(x_points, new_y_points, color="#800080", label="Decision Boundary")
    plt.plot(x_points, -3 * x_points + 1, color="#008000", label="Target Separating Function")
    plt.scatter(c_zero_x, c_zero_y, s=10, color="#FF0000", label="Zero Class")
    plt.scatter(c_one_x, c_one_y, s=10, color="#0000FF", label="One Class")
    plt.legend(loc='upper right')
    plt.savefig('output/part{0}_step{1}.png'.format(part_num, step_num))


def apply_crossval(csv_file):
    data = pd.read_csv(csv_file, header=None)
    values = data.values
    np.random.shuffle(values)
    lambda_values = []
    rms_values = []
    logger.info('\033[32m' + "Applying Cross-Validation step please wait..." + '\033[0m')
    for i in tqdm.tqdm(range(3700, 4700)):
        lambda_val: float = i / 10
        spec_rms_values = []
        for j in range(5):
            if j == 0:
                training, test = values[:800, :], values[800:, :]
            elif j == 1:
                training = np.concatenate((values[:600, :], values[800:, :]))
                test = values[600:800, :]
            elif j == 2:
                training = np.concatenate((values[:400, :], values[600:, :]))
                test = values[400:600, :]
            elif j == 3:
                training = np.concatenate((values[:200, :], values[400:, :]))
                test = values[200:400, :]
            else:
                training, test = values[200:, :], values[:200, :]
            x_train = []
            train_target = []
            x_test = []
            test_target = []

            for k in range(training.shape[0]):
                x_train.append((training[k][:-1]).tolist())
                train_target.append(training[k][-1])
            for k in range(test.shape[0]):
                x_test.append((test[k][:-1]).tolist())
                test_target.append(test[k][-1])

            train_target = np.array(train_target)
            test_target = np.array(test_target)
            x_train = np.concatenate((np.ones((len(x_train), 1)), x_train), axis=1)
            x_test = np.concatenate((np.ones((len(x_test), 1)), x_test), axis=1)
            identity = np.identity((len(x_train[0])))
            weight = np.matmul(np.matmul(inv(np.matmul(x_train.T, x_train) + lambda_val*identity), x_train.T),
                               train_target)
            prediction = x_test.dot(weight)
            error = 0
            for k in range(len(prediction)):
                error += (prediction[k] - test_target[k])**2
            rms = sqrt(error/len(prediction))
            spec_rms_values.append(rms)
        mean_rms = sum(spec_rms_values) / len(spec_rms_values)
        lambda_values.append(lambda_val)
        rms_values.append(mean_rms)

    print("RMSe value: {0}".format(min(rms_values)))
    print("Lambda value: {0}".format(lambda_values[rms_values.index(min(rms_values))]))
    plt.xlabel('Lambda values')
    plt.ylabel('Rms values')
    plt.title("Part 2 & Step 3")
    plt.plot(lambda_values, rms_values, color="#800080")
    plt.savefig('output/part2_step3.png', bbox_inches='tight')


def calc_weight(csv_file, lambda_val=None):
    data = pd.read_csv(csv_file, header=None)
    values = data.values
    x_matrix = []
    t_target = []
    shape = data.shape
    for i in range(shape[0]):
        x_matrix.append((values[i][:-1]).tolist())
        t_target.append(values[i][-1])
    m = np.ones((len(x_matrix), 1))
    X = np.concatenate((m, x_matrix), axis=1)
    if lambda_val:
        identity = np.identity((len(X[0])))
        np.matmul(np.matmul(inv(np.matmul(X.T, X) + lambda_val * identity), X.T), t_target)
    else:
        np.matmul(np.matmul(inv(np.matmul(X.T, X)), X.T), t_target)


def time_in_msec(time):
    return int(round(time * 1000))


def part1(step_num):
    if step_num == "step1":
        generate_random_points(100, 50)
        classify()
        iter_p1_s1, new_weight = pla()
        print("Total number of iteration needed for step 1: {0}".format(iter_p1_s1))
        show_graph(new_weight, 1, 1)
    elif step_num == "step2":
        generate_random_points(200, 100)
        classify()
        iter_p1_s2, new_weight = pla()
        print("Total number of iteration needed for step 2: {0}".format(iter_p1_s2))
        show_graph(new_weight, 1, 2)
    elif step_num == "step3":
        generate_random_points(10000, 5000)
        classify()
        iter_p1_s3, new_weight = pla()
        print("Total number of iteration needed for step 3: {0}".format(iter_p1_s3))
        show_graph(new_weight, 1, 3)
    else:
        log_helper()


def part2(step_num):
    if step_num == "step1":
        begin = time.time()
        calc_weight("input/ds1.csv")
        print("Time to complete step 1: {0} msec".format(time_in_msec(time.time() - begin)))
    elif step_num == "step2":
        begin = time.time()
        calc_weight("input/ds2.csv")
        print("Time to complete step 2: {0} msec".format(time_in_msec(time.time() - begin)))
    elif step_num == "step3":
        begin = time.time()
        calc_weight("input/ds2.csv", 401.9)  # comment this line if you want to apply cross validation
        # apply_crossval("ds2.csv")  # delete comment and apply cross-valid. to find the lambda with the min RMSe value
        print("Time to complete step 3: {0} msec".format(time_in_msec(time.time() - begin)))
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
    elif part_num == "part2":
        part2(step_num)
    else:
        log_helper()
