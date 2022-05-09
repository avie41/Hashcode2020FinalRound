#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Module handling inputs & outputs.
    Works on ASCII files.

    Usage:
    # >>> from polyhash import input_parsing
    # >>> grid, tasks = input_parsing('../../input/a_example.txt')
"""

from typing import List, Tuple

__all__ = ['input_parsing']  # add to this list all importable symbols


def input_parsing(data) -> Tuple[List, List]:
    """Extracting all useful information for initializing the grid from a given input file (.txt)"""
    with open(data, 'r') as f:
        text_input: List[List[str]] = []
        for line in f:
            # Reading the file line by line
            # We remove '\n' and we split according to spaces
            line = line.replace('\n', '').split(' ')
            text_input.append(line)
        # turning all values into integer type
        text_input: List[List[int]] = [[int(j) for j in i] for i in text_input]

    # Collecting various information contained in the file
    width, height, arms_nb, mount_points_nb, task_nb, step_nb = text_input[0]
    mount_points: List = text_input[1:mount_points_nb+1]
    mount_points: List = [tuple(a) for a in mount_points]
    scores = [text_input[i][0] for i in range(mount_points_nb+1, len(text_input)-1, 2)]

    # Creating a list of tuple assembly points
    assembly_points: List = []
    for a in text_input[mount_points_nb+2:len(text_input):2]:
        pts: List[Tuple[int, int]] = [(a[i], a[i+1]) for i in range(0, len(a) - 1, 2)]
        assembly_points.append(pts)

    return [width, height, arms_nb, step_nb, mount_points], [scores, assembly_points]


if __name__ == "__main__":
    grid, tasks = input_parsing("../../input/a_example.txt")
    print(grid, tasks)
