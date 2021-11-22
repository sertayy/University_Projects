import sys
import logging
import os
from typing import List


def levenshtein(org_str: str, target_str: str) -> (List[str], List[List[int]], int):
    edit_table = [[0 for x in range(len(target_str) + 1)] for y in range(len(org_str) + 1)]
    operation_list: List[str] = []
    i = 0
    j = 0
    len_org = len(org_str)
    len_target = len(target_str)
    for i in range(len_org + 1):
        edit_table[i][0] = i
    for j in range(len_target + 1):
        edit_table[0][j] = j

    for i in range(1, len_org + 1):
        for j in range(1, len_target + 1):
            if target_str[j - 1] == org_str[i - 1]:
                edit_table[i][j] = min(edit_table[i - 1][j] + 1, edit_table[i][j - 1] + 1, edit_table[i - 1][j - 1])
            else:
                edit_table[i][j] = min(edit_table[i - 1][j] + 1, edit_table[i][j - 1] + 1, edit_table[i - 1][j - 1] + 1)

    while i != 0 or j != 0:
        if i == 0:
            operation_list.insert(0, "Insert " + target_str[j - 1])
            j -= 1
            continue
        if j == 0:
            operation_list.insert(0, "Delete " + org_str[i - 1])
            i -= 1
            continue

        min_cell = min(edit_table[i - 1][j], edit_table[i][j - 1], edit_table[i - 1][j - 1])
        if min_cell == edit_table[i - 1][j - 1]:
            if min_cell < edit_table[i][j]:
                operation_list.insert(0, "Replace " + org_str[i - 1] + " to " + target_str[j - 1])
            elif min_cell == edit_table[i][j]:
                operation_list.insert(0, "Copy " + org_str[i - 1])
            j -= 1
            i -= 1
        elif min_cell == edit_table[i - 1][j]:
            operation_list.insert(0, "Delete " + org_str[i - 1])
            i -= 1
        else:
            operation_list.insert(0, "Insert " + target_str[j - 1])
            j -= 1

    return operation_list, edit_table, edit_table[len(org_str)][len(target_str)]


def damerau(org_str: str, target_str: str) -> (List[str], List[List[int]], int):
    edit_table = [[0 for x in range(len(target_str) + 1)] for y in range(len(org_str) + 1)]
    operation_list: List[str] = []
    i = 0
    j = 0
    len_org = len(org_str)
    len_target = len(target_str)
    for i in range(len_org + 1):
        edit_table[i][0] = i
    for j in range(len_target + 1):
        edit_table[0][j] = j

    for i in range(1, len_org + 1):
        for j in range(1, len_target + 1):
            if target_str[j - 1] == org_str[i - 1]:
                edit_table[i][j] = min(edit_table[i - 1][j] + 1, edit_table[i][j - 1] + 1, edit_table[i - 1][j - 1])
                if i > 1 and j > 1 and org_str[i-1] == target_str[j-2] and org_str[i-2] == target_str[j-1]:
                    edit_table[i][j] = min(edit_table[i][j], edit_table[i-2][j-2])
            else:
                edit_table[i][j] = min(edit_table[i - 1][j] + 1, edit_table[i][j - 1] + 1, edit_table[i - 1][j - 1] + 1)
                if i > 1 and j > 1 and org_str[i-1] == target_str[j-2] and org_str[i-2] == target_str[j-1]: # for transpose
                    edit_table[i][j] = min(edit_table[i][j], edit_table[i-2][j-2] + 1)

    while i != 0 or j != 0:
        if i == 0:
            operation_list.insert(0, "Insert " + target_str[j - 1])
            j -= 1
            continue
        if j == 0:
            operation_list.insert(0, "Delete " + org_str[i - 1])
            i -= 1
            continue

        min_cell = min(edit_table[i - 1][j], edit_table[i][j - 1], edit_table[i - 1][j - 1])
        if min_cell == edit_table[i - 1][j - 1]:
            if i > 1 and j > 1 and org_str[i - 1] == target_str[j - 2] and org_str[i - 2] == target_str[j - 1]:  # for transpose
                if edit_table[i - 2][j - 2] < edit_table[i][j]:
                    operation_list.insert(0, "Transpose " + org_str[i - 1] + " and " + org_str[i - 2])
                    i -= 2
                    j -= 2
                    continue
            if min_cell < edit_table[i][j]:
                operation_list.insert(0, "Replace " + org_str[i - 1] + " to " + target_str[j - 1])
            elif min_cell == edit_table[i][j]:
                operation_list.insert(0, "Copy " + org_str[i - 1])
            j -= 1
            i -= 1
        elif min_cell == edit_table[i - 1][j]:
            operation_list.insert(0, "Delete " + org_str[i - 1])
            i -= 1
        else:
            operation_list.insert(0, "Insert " + target_str[j - 1])
            j -= 1

    return operation_list, edit_table, edit_table[len(org_str)][len(target_str)]


if __name__ == '__main__':
    original_str = sys.argv[1]
    destination_str = sys.argv[2]
    try:
        output_path: str = os.path.join(os.path.join(os.path.dirname(__file__), "outputs"), "output.txt")
        with open(output_path, "w") as out_file:
            for i in range(2):
                if i == 0:
                    seq_of_operations, edit_table, edit_distance = levenshtein(original_str, destination_str)
                    out_file.write("------------------------ Levenshtein Part ------------------------\n")
                else:
                    seq_of_operations, edit_table, edit_distance = damerau(original_str, destination_str)
                    out_file.write("\n\n------------------------ Damerau Part ------------------------\n")
                out_file.write("Edit distance = {0}\n".format(str(edit_distance)))
                for row in edit_table:
                    out_file.write(' '.join([str(a) for a in row]) + '\n')
                out_file.write("Sequence of operations: {0}".format(seq_of_operations))
    except Exception as ex:
        logging.error(ex)
