#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Largely inspired by https://github.com/hbock-42/Pathfinder-AStar/
from typing import List, Tuple, Set, Dict


__all__ = ['PathFinder']


def _distance(start: Tuple[int, int], target: Tuple[int, int]) -> int:
    """Computes the distance between two points using the Manhattan distance"""
    return abs(start[0] - target[0]) + abs(start[1] - target[1])


def _heuristic(start: Tuple[int, int], target: Tuple[int, int]) -> int:
    """Returns the heuristic of A*, aka the Manhattan distance between the current point and the target"""
    return _distance(start, target)


def _get_node_with_best_f_score(open_set: Set[Tuple[int, int]], f_score: Dict[int, float]) -> Tuple[int, int]:
    """Returns the cell having the lowest score"""
    return min(open_set, key=lambda a: f_score[hash(a)])


def _is_sublist_in_list(array: List, subarray: List) -> bool:
    """
    Checks if a list is contained in another.
    Exemple:
    >>> _is_sublist_in_list([1, 2, 3, 4, 5, 6, 7], [3, 4, 5])
    True
    >>> _is_sublist_in_list([1, 2, 3, 4, 5, 6, 7], [4, 3])
    False
    """
    for i in range(len(array) - len(subarray) + 1):
        if subarray == [array[z] for z in range(i, i + len(subarray))]:
            return True
    return False


def _is_wall(obstacles, arm, parent: Tuple[int, int], cell: Tuple[int, int]) -> bool:
    """
    Checks whether a given cell is a wall or not.
    If it is defined as a wall, it may as well be its own arm.
    If so, The movement may be allowed if it has retracted enough : retracting is allowed, but
    crossing its own arm is definitely not. This is where we used _is_sublist_in_list
    """
    # print(arm, cell, parent)
    if cell in arm:
        # If the parent is not in the arm, then it is a wall
        piece_of_arm = [cell, parent]
        return not _is_sublist_in_list(arm, piece_of_arm)

    return cell in obstacles


def _is_inside(size: Tuple[int, int], cell: Tuple[int, int]) -> bool:
    """
    Checks that all the indexes are in range and not outside of the grid or outside of timing
    """
    for i in range(2):
        if not (size[i] > cell[i] >= 0):
            return False
    return True


def _check_neighbours(obstacles, size, arm: List[Tuple[int, int]], cell: Tuple[int, int], neigh: List) -> List:
    """Uses previous functions to determine if a neighbour is walkable."""
    return [n for n in neigh if _is_inside(size, n) and not _is_wall(obstacles, arm, cell, n)]


def _retrace_path(current, came_from, _hash_vector_table) -> List[Tuple[int, int]]:
    """
    Returns the actual path to follow. It starts from the end, and goes back up according to the relative parents.
    """
    cell: Tuple[int, int] = current
    path: List[Tuple[int, int]] = [cell]
    while hash(cell) in came_from.keys():
        parent_hash: str = came_from[hash(cell)]
        cell: Tuple[int, int] = _hash_vector_table[parent_hash]
        path.append(cell)

    return path[::-1]


class PathFinder:
    """
    Object used to compute the path needed to go from a point of
    a given grid to another.
    """

    def __init__(self, obstacles: Set[Tuple[int, int]], size: Tuple[int, int, int], limit=1):
        """
        Only the grid is needed as a parameter.
        """
        self.obstacles: Set[Tuple[int, int]] = obstacles.copy()
        self.size: Tuple[int, int] = size[:2]
        self.arm: List[Tuple[int, int]] = []
        self.nb_movements: int = size[2]
        self.memory: List = []
        self.limit: float = limit

    def path(self, arm: List[Tuple[int, int]], targets: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Returns the list of coordinates linking start to target
        """
        # Checking the memory
        selection = [m for m in self.memory if m[0] == arm and m[1] == targets]
        if selection:
            print('PATHFINDER: Used memory')
            return selection[0][2]

        self.arm: List[Tuple[int, int]] = arm
        computed_path: List = []
        for target in targets:
            self.arm: List[Tuple[int, int]] = arm + computed_path
            current_path: List[Tuple] = self.find_path(arm + computed_path, target)
            computed_path += current_path

            if len(computed_path) > self.nb_movements or current_path == []:
                return []

        self.memory.append([arm, targets, computed_path])

        return computed_path

    def update_obstacles(self, obstacles: Set[Tuple[int, int]]) -> None:
        """Resets the obstacles variables according to the value of obstacles"""
        if self.obstacles != obstacles:
            self.obstacles: Set[Tuple[int, int]] = obstacles.copy()
            self.memory: List = []

    def find_path(self, arm: List[Tuple[int, int]], target: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Returns the path from the end of the arm to the target.
        If there isn't any path, an empty list is returned.
        """
        start = arm[-1]

        if start == target:
            return [start]

        path = self._find_path(start, target)

        return path[1:]

    def _find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Actual implementation of the A* algorithm.
        """
        # Initiating the various variables needed
        # Hash table is used to create a correspondence between two hashes.
        # Rather than storing tuples, we store their hash representation.
        _hash_vector_table: Dict[int, Tuple[int, int]] = dict()

        closed_set: Set[Tuple[int, int]] = set()
        open_set: Set[Tuple[int, int]] = {start}

        # Dictionary linking cells to their parents.
        came_from: Dict[int, int] = dict()

        # Dictionaries storing g & f scores of each cell
        g_score: Dict[int, float] = dict()
        f_score: Dict[int, float] = dict()

        g_score[hash(start)] = 0
        f_score[hash(start)] = _heuristic(start, end)

        _hash_vector_table[hash(start)] = start

        # Computing number of walkable cells
        walkable_cells = self.size[0]*self.size[1] - len(self.obstacles)

        while len(open_set) > 0:
            # We always get the cell having the lowest score overall
            current: Tuple[int, int] = _get_node_with_best_f_score(open_set, f_score)

            if current == end:
                # Path found, we retrace our steps
                # percentage = len(closed_set) * 100 / walkable_cells
                # if percentage > 10:
                #     print('Examined {} percent of the map.'.format(round(percentage, 2)))
                return _retrace_path(current, came_from, _hash_vector_table)

            # Stopping condition: if more than self.limit % cells have been explored.
            if len(closed_set) >= self.limit * walkable_cells:
                return []

            open_set.remove(current)
            closed_set.add(current)

            for neighbour in self.get_neighbours(current):
                # If the neighbour is considered as closed, we skip the next part
                if neighbour in closed_set:
                    continue

                if neighbour not in open_set:
                    open_set.add(neighbour)

                # If it has not been explored yet, we had it to the tables.
                if hash(neighbour) not in g_score.keys():
                    g_score[hash(neighbour)] = float('inf')
                    _hash_vector_table[hash(neighbour)] = neighbour

                # If it is more expensive to go to that cell from the current one than before, we continue.
                tentative_g_score: float = g_score[hash(current)] + _distance(current, neighbour)
                if tentative_g_score >= g_score[hash(neighbour)]:
                    continue

                # If it cheaper to go to that cell from the current one, we update both scores.
                came_from[hash(neighbour)] = hash(current)
                g_score[hash(neighbour)] = tentative_g_score
                weight: int = 2
                # If the neighbour is the arm, the weight is lower. this way, we first go down the arm.
                if neighbour in self.arm:
                    weight: int = 1
                f_score[hash(neighbour)] = g_score[hash(neighbour)] + weight * _heuristic(neighbour, end)

        return []

    def get_neighbours(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Returns the four neighbours of any given cell
        """
        offsets: List[Tuple[int, int]] = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        neighbours: List[Tuple[int, int]] = [(cell[0] + a, cell[1] + b) for a, b in offsets]
        return _check_neighbours(self.obstacles, self.size, self.arm, cell, neighbours)


if __name__ == "__main__":
    obs: Set = set()
    finder: PathFinder = PathFinder(obs, (3, 3, 100))

    robot_arm: List[Tuple[int, int]] = [(0, 1), (0, 2)]
    current_target: List[Tuple[int, int]] = [(1, 0)]
    print(finder.path(robot_arm, current_target))
