#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creating the Task object.
A task is assigned to a robot according to its ratio
(which depends on the list of points to be reached and the task score)
"""

from __future__ import annotations
from typing import List, Tuple
from distances import manhattan

__all__ = ['Task']


class Task:

    performed: List[Task] = []
    remaining: List[Task] = []
    current: List[Task] = []

    def __init__(self, path: List[Tuple[int, int]], score):
        """
        Initiating a task with a list of its assembly points and its score
        """
        self.status: str = 'na'  # task's status (na,active,done)
        self.path: List[Tuple[int, int]] = path
        self.target_points: List[Tuple[int, int]] = path.copy()
        self.score: int = score
        self.ratio: int = 0

        Task.remaining.append(self)
        self.id: int = Task.remaining.index(self)

        print(self)

    def change_status(self, new_status: str) -> None:
        """
        Changes the status of the task. Moves the task in and out of the global lists according to new_status.
        new_status can take the values ["na", "active", "done"]
        """
        if new_status == 'active':
            Task.remaining.remove(self)
            Task.current.append(self)
        elif new_status == 'done':
            Task.current.remove(self)
            Task.performed.append(self)
        elif new_status == 'na':
            Task.remaining.append(self)
            Task.current.remove(self)
            self.target_points = self.path.copy()
        else:
            raise NameError('Invalid Status')

        self.status = new_status

    def next_position(self, position) -> None:
        """
        Finds the next point of the task when the robot reached one assembly point.
        Executed in the Robot class.
        """
        if self.target_points[0] == position:
            # if the robot has reached the assembly point, the target point is modified
            self.target_points.pop(0)
            if len(self.target_points) == 0:
                # If there are no assembly point left, the task is done. Hence, the status is changed.
                self.target_points = None
                self.change_status('done')
                print("Task n°{} is completed, adding {} more point(s) to the score".format(self.id, self.score))

    def compute_ratio(self, points: List[Tuple[int, int]], g_height: int,
                      g_width: int, ratio_type: str = 'ratio') -> None:
        """
        Computes the ratio of the task
        """
        # Moving cost of a possible path to achieve the task
        dist: int = 0
        # Additional calculations for the ratio
        # bord = 0
        # # Sum/Average of distances between the arm's mount point and each assembly point of the task
        # dist_mp_ap: int = 0
        # for i, point in enumerate(self.path):
        #     dist_mp_ap += manhattan(points[0], point)
        #     bord += min(point[0], point[1], abs(g_height - point[1]), abs(g_width - point[0]))
        #
        #     bord /= (i + 1)
        # bord = 1 / bord if bord != 0 else 1
        #
        # dist_average = dist_mp_ap / (i + 1)

        for (src, target) in zip([points[1]] + self.path[:len(self.path) - 1], self.path):
            dist += manhattan(src, target)

        if ratio_type == 'ratio':
            self.ratio = (self.score / dist**0.865) if dist > 0 else self.score
        elif ratio_type == 'score':
            self.ratio = self.score
        elif ratio_type == 'distance':
            self.ratio = dist
        else:
            raise ValueError('ratio_type \"{}\" not in {}'.format(ratio_type, ['ratio', 'score', 'distance']))

    def __str__(self) -> str:
        """str representation of the object for debugging purpose"""
        return "Task n°{}, score={}, assembly_pts={}".format(self.id, self.score, self.path)
