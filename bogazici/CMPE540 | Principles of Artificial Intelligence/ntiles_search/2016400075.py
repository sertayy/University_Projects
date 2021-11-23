"""
Author: Sertay Akpinar 24.04.2021
"""
import sys
import logging
from typing import List
import copy
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

visited_matrices = []
search_type = ""
goal_matrix = []


class Node:
    def __init__(self, matrix, move_list, gn_cost, hn_cost=0):
        self.matrix = matrix
        self.move_list = move_list
        self.gn_cost = gn_cost
        self.hn_cost = hn_cost


def calculate_hn_astar(current_matrix) -> int:
    if search_type == "astar0":
        num_of_diff = 0
        for i in range(len(current_matrix)):
            for j in range(len(current_matrix[i])):
                if current_matrix[i][j] != goal_matrix[i][j] and \
                        (current_matrix[i][j].isnumeric() or "-" in current_matrix[i][j]):
                    num_of_diff += 1
        return num_of_diff
    elif search_type == "astar1":
        manh_distance = 0
        for i in range(len(current_matrix)):
            for j in range(len(current_matrix[i])):
                if not (current_matrix[i][j].isnumeric() or "-" in current_matrix[i][j]):
                    continue
                is_found = False
                for x in range(len(goal_matrix)):
                    for y in range(len(goal_matrix[i])):
                        if current_matrix[i][j] == goal_matrix[x][y]:
                            is_found = True
                            manh_distance += (abs(x - i) + abs(y - j))
                            break
                    if is_found:
                        break
        return manh_distance
    elif search_type == "my-astar-positive":
        manh_distance = 0
        for i in range(len(current_matrix)):
            for j in range(len(current_matrix[i])):
                if not (current_matrix[i][j].isnumeric() or "-" in current_matrix[i][j]):
                    continue
                is_found = False
                for x in range(len(goal_matrix)):
                    for y in range(len(goal_matrix[i])):
                        if current_matrix[i][j] == goal_matrix[x][y]:
                            is_found = True
                            manh_distance += ((abs(x - i) + abs(y - j)) * int(current_matrix[i][j]))
                            break
                    if is_found:
                        break
        return manh_distance
    elif search_type == "my-astar-all":
        manh_distance = 0
        for i in range(len(current_matrix)):
            for j in range(len(current_matrix[i])):
                if not (current_matrix[i][j].isnumeric() or "-" in current_matrix[i][j]):
                    continue
                is_found = False
                for x in range(len(goal_matrix)):
                    for y in range(len(goal_matrix[i])):
                        if current_matrix[i][j] == goal_matrix[x][y]:
                            is_found = True
                            manh_distance += ((abs(x - i) + abs(y - j)) * abs(int(current_matrix[i][j])))
                            break
                    if is_found:
                        break
        return manh_distance


def n_tiles_search(init_matrix):
    nodes_inserted = 1
    if "astar" in search_type:
        hn_cost = calculate_hn_astar(init_matrix)
        init_node = Node(init_matrix, [], 0, hn_cost)
    else:
        init_node = Node(init_matrix, [], 0)
    fringe: List[Node] = [init_node]
    while True:
        if len(fringe) == 0:
            logger.info("FAILURE")
            return None
        if search_type == "dfs":
            node = fringe.pop()
        else:
            node = fringe.pop(0)
        visited_matrices.append(node.matrix)
        if node.matrix == goal_matrix:
            return node, nodes_inserted
        childs: List[Node] = expand(node)
        nodes_inserted += len(childs)
        fringe += childs
        if search_type == "ucs":
            fringe.sort(key=lambda tile: tile.gn_cost, reverse=False)
        elif "astar" in search_type:
            fringe.sort(key=lambda tile: tile.gn_cost + tile.hn_cost, reverse=False)


def add_child_to_successor(i, j, x, y, node, successor, action_type):
    temp = copy.deepcopy(node)
    temp.matrix[i][j] = temp.matrix[x][y]
    temp.matrix[x][y] = "."
    if temp.matrix not in visited_matrices:
        temp.move_list.append("move {0} {1}".format(temp.matrix[i][j], action_type))
        child = Node(temp.matrix, temp.move_list, int(temp.matrix[i][j]) + temp.gn_cost)
        if "astar" in search_type:
            child.hn_cost = calculate_hn_astar(temp.matrix)
        successor.append(child)


def expand(node) -> List[Node]:
    node_matrix = node.matrix
    successor = []
    for i in range(len(node_matrix)):
        for j in range(len(node_matrix[i])):
            if not node_matrix[i][j].isnumeric() and "-" not in node_matrix[i][j]:
                continue
            if j > 0 and node_matrix[i][j-1] == ".":
                add_child_to_successor(i, j - 1, i, j, node, successor, "left")
            if j+1 < len(node_matrix[i]) and node_matrix[i][j+1] == ".":
                add_child_to_successor(i, j + 1, i, j, node, successor, "right")
            if i > 0 and node_matrix[i-1][j] == ".":
                add_child_to_successor(i - 1, j, i, j, node, successor, "up")
            if i + 1 < len(node_matrix) and node_matrix[i+1][j] == ".":
                add_child_to_successor(i + 1, j, i, j, node, successor, "down")
    return successor


def extract_matrix(infile: str) -> List[List[str]]:
    matrix = []
    with open(infile, 'r') as file:
        for line in file:
            matrix.append(line.split())
    return matrix


def write_soln(final_state, nodes_inserted, soln_file):
    actions = final_state.move_list
    total_cost = final_state.gn_cost + final_state.hn_cost
    if final_state is None:
        logger.error("No solution found.")
    else:
        with open(soln_file, "w") as outfile:
            for action in actions:
                outfile.write(action + "\n")
            outfile.write("nInsertedNodes: {0}\n".format(nodes_inserted))
            outfile.write("cost: {0}\n".format(total_cost))


def compare_matrices(init_matrix, goal_matrix):
    for i in range(len(init_matrix)):
        for j in range(len(init_matrix[i])):
            is_found = False
            for x in range(len(goal_matrix)):
                if init_matrix[i][j] in goal_matrix[x]:
                    is_found = True
                    break
            if not is_found:
                init_matrix[i][j] = "."
    return init_matrix


if __name__ == '__main__':
    search_type = sys.argv[1]
    init_file = sys.argv[2]
    goal_file = sys.argv[3]
    soln_file = sys.argv[4]
    goal_matrix = extract_matrix(goal_file)
    init_matrix = compare_matrices(extract_matrix(init_file), goal_matrix)
    final_state, nodes_inserted = n_tiles_search(init_matrix)
    write_soln(final_state, nodes_inserted, soln_file)
