"""
Author: Sertay Akpinar 11.05.2021
"""
import sys
import copy
from typing import List

visited_matrices = []
goal_matrix = []
soln_file = sys.argv[5]
n_actions = int(sys.argv[4])
search_type = sys.argv[1]
util_calls = 0


class Node:
    def __init__(self, matrix, move_list):
        self.matrix = matrix
        self.move_list = move_list


def minimax_decision(root_node) -> (Node, float):
    max_val = float("-inf")
    chosen_node = None
    actions: List[Node] = expand(root_node, 1)
    for action in actions:
        child_node, utility_val = min_value(action, 3 * n_actions - 1)
        if utility_val > max_val:
            max_val = utility_val
            chosen_node = child_node
    return chosen_node, max_val


def a_b_minimax_decision(root_node, alpha, beta) -> (Node, float):
    max_val = float("-inf")
    chosen_node = None
    actions: List[Node] = expand(root_node, 1)
    for action in actions:
        child_node, utility_val = a_b_min_value(action, 3 * n_actions - 1,  alpha, beta)
        if utility_val > max_val:
            max_val = utility_val
            chosen_node = child_node
        alpha = max(alpha, utility_val)
        if beta <= alpha:
            break
    return chosen_node, max_val


def a_b_max_value(node, depth, agent_num, alpha, beta) -> (Node, float):
    if depth == 0:
        return node, calc_utility(node.matrix)
    max_val = float("-inf")
    chosen_node = None
    actions: List[Node] = expand(node, agent_num)
    for action in actions:
        if agent_num == 3:
            child_node, utility_val = a_b_max_value(action, depth-1, 1, alpha, beta)
        else:
            child_node, utility_val = a_b_min_value(action, depth - 1, alpha, beta)
        if utility_val > max_val:
            max_val = utility_val
            chosen_node = child_node
        alpha = max(alpha, utility_val)
        if beta <= alpha:
            break
    return chosen_node, max_val


def a_b_min_value(node, depth, alpha, beta) -> (Node, float):
    max_val = float("inf")
    chosen_node = None
    actions: List[Node] = expand(node, 2)
    for action in actions:
        child_node, utility_val = a_b_max_value(action, depth-1, 3, alpha, beta)
        if utility_val < max_val:
            max_val = utility_val
            chosen_node = child_node
        beta = min(beta, utility_val)
        if beta <= alpha:
            break
    return chosen_node, max_val


def max_value(node, depth, agent_num) -> (Node, float):
    if depth == 0:
        return node, calc_utility(node.matrix)
    max_val = float("-inf")
    total_val = 0
    chosen_node = None
    actions: List[Node] = expand(node, agent_num)
    for action in actions:
        if agent_num == 3:
            child_node, utility_val = max_value(action, depth-1, 1)
            if search_type == "minimax_rand":
                total_val += utility_val
                if action == actions[0]:
                    chosen_node = child_node
            else:
                if utility_val > max_val:
                    max_val = utility_val
                    chosen_node = child_node
        else:
            child_node, utility_val = min_value(action, depth - 1)
            if utility_val > max_val:
                max_val = utility_val
                chosen_node = child_node
    if search_type == "minimax_rand" and agent_num == 3:
        return chosen_node, total_val / len(actions)
    return chosen_node, max_val


def min_value(node, depth) -> (Node, float):
    min_val = float("inf")
    chosen_node = None
    actions: List[Node] = expand(node, 2)
    total_val = 0
    for action in actions:
        child_node, utility_val = max_value(action, depth-1, 3)
        if search_type == "minimax_rand":
            total_val += utility_val
            if action == actions[0]:
                chosen_node = child_node
        else:
            if utility_val < min_val:
                min_val = utility_val
                chosen_node = child_node
    if search_type == "minimax_rand":
        return chosen_node, total_val / len(actions)
    return chosen_node, min_val


def calc_utility(current_matrix) -> int:
    global util_calls
    util_calls += 1
    util = 0
    for i in range(len(current_matrix)):
        for j in range(len(current_matrix[i])):
            if not current_matrix[i][j].isnumeric() and "-" not in current_matrix[i][j]:
                continue
            if current_matrix[i][j] == goal_matrix[i][j]:
                if int(current_matrix[i][j]) % 2 == 1:
                    util += int(current_matrix[i][j])
                else:
                    util -= int(current_matrix[i][j])
    return util


def add_child_to_successor(i, j, x, y, node, successor, action_type, agent_num):
    temp = copy.deepcopy(node)
    temp.matrix[i][j] = temp.matrix[x][y]
    temp.matrix[x][y] = "."
    temp.move_list.append("AGENT{0} move {1} {2}".format(agent_num, temp.matrix[i][j], action_type))
    child = Node(temp.matrix, temp.move_list)
    successor.append(child)


def expand(node, agent_num) -> List[Node]:
    node_matrix = node.matrix
    successor = []
    for i in range(len(node_matrix)):
        for j in range(len(node_matrix[i])):
            if not node_matrix[i][j].isnumeric() and "-" not in node_matrix[i][j]:
                continue
            if (agent_num == 1 and int(node_matrix[i][j]) % 2 == 1) \
                    or (agent_num == 2 and int(node_matrix[i][j]) % 2 == 0) or agent_num == 3:
                if j > 0 and node_matrix[i][j-1] == ".":
                    add_child_to_successor(i, j - 1, i, j, node, successor, "left", agent_num)
                if j+1 < len(node_matrix[i]) and node_matrix[i][j+1] == ".":
                    add_child_to_successor(i, j + 1, i, j, node, successor, "right", agent_num)
                if i > 0 and node_matrix[i-1][j] == ".":
                    add_child_to_successor(i - 1, j, i, j, node, successor, "up", agent_num)
                if i + 1 < len(node_matrix) and node_matrix[i+1][j] == ".":
                    add_child_to_successor(i + 1, j, i, j, node, successor, "down", agent_num)
    return successor


def extract_matrix(infile: str) -> List[List[str]]:
    matrix = []
    with open("input/" + infile, 'r') as file:
        for line in file:
            matrix.append(line.split())
    return matrix


def write_soln(max_val, actions, util_calls):
    with open("output/" + soln_file, "w") as outfile:
        for action in actions:
            outfile.write(action + "\n")
        outfile.write("Value: {:.2f}\n".format(max_val))
        outfile.write("Util calls: {0}\n".format(util_calls))


if __name__ == '__main__':
    init_file = sys.argv[2]
    goal_file = sys.argv[3]
    init_matrix = extract_matrix(init_file)
    goal_matrix = extract_matrix(goal_file)
    if search_type == "alpha_beta_pruning":
        max_node, max_val = a_b_minimax_decision(Node(init_matrix, []), float('-inf'), float('inf'))
    else:
        max_node, max_val = minimax_decision(Node(init_matrix, []))
    write_soln(max_val, max_node.move_list, util_calls)
