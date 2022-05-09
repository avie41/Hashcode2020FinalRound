#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creating the Robot class defined by a position and an id (order of creation).
This object has a method to move. A sub-method has also been added in order to keep
track of the path covered by each robot.
"""
from polyhio import input_parsing
from task import Task
from typing import Tuple, List, Optional
from pathfinding import PathFinder

__all__ = ['Robot']


class Robot:

    nb_robots: int = 0
    arms: List[List[Tuple]] = []
    next_position: List[Optional[Tuple]] = []
    memory_paths: List[List[str]] = []
    tasks: List[Task] = []

    def __init__(self, position: Tuple, finder: PathFinder, g_height: int, g_width: int, task_limit: float = 1.0):
        """
        Defining a robot by its position and id.
        """
        self.arm: List[Tuple[int, int]] = [position]
        self.id: int = Robot.nb_robots
        self.tasks_performed = []
        self.finder = finder
        self.planned_path = []
        self.g_height = g_height
        self.g_width = g_width

        Robot.nb_robots += 1
        Robot.arms.append([position])
        Robot.next_position.append(None)
        Robot.memory_paths.append([])

        # Creating an internal timer to optimize global execution time
        self.max_wait_time: int = int(self.finder.nb_movements * 25/1000)
        self.current_max_wait_time: int = 1
        self.wait_time: int = 0

        # Setting the number of tasks to inspect before giving up
        if task_limit <= 1:
            self.task_limit = int(len(Task.remaining)*task_limit)
        else:
            self.task_limit = task_limit

        # Getting a task
        self.task: Optional[Task] = None
        self.get_task()
        Robot.tasks.append(self.task)

        print(self)

    def get_task(self) -> None:
        """
        Assigns a new task to a robot. Tasks with the best ratio always come first
        """

        print("There are {} tasks left".format(len(Task.remaining)))
        # Computing the ratios for each task
        for task in Task.remaining:
            task.compute_ratio([self.arm[0], self.arm[-1]], self.g_height, self.g_width, ratio_type='ratio')

        # Sorting remaining tasks
        possible_tasks: List[Task] = Task.remaining.copy()
        possible_tasks.sort(key=lambda x: x.ratio, reverse=True)

        found_task: bool = False
        for task in possible_tasks[:self.task_limit]:
            # Computing the path from the robot head to the last assembly point of the task
            computed_path: List[Tuple[int, int]] = self.finder.path(self.arm, task.target_points)

            if computed_path:
                # I we have found a viable path, we take it
                self.task = task
                self.task.change_status('active')  # we change the status of the task to 'active'
                self.planned_path = computed_path 

                # Internal timer is reset
                self.current_max_wait_time = 1
                self.wait_time = 0

                found_task = True
                break
            else:
                # print('Can\'t choose task {}.'.format(task.id))
                pass

        if found_task:
            # Next part of the task-taking process
            print("Robot {} is choosing task {}".format(self.id, self.task.id))
            # we check that the following task is not already completed
            # with the current position of the robot if it does the task is validated
            if len(self.task.path) == 1 and self.arm[-1] == self.task.path[0]:
                print('No movement required !')
                self.task.next_position(self.arm[-1])
                if self.task.status == 'done':
                    # The task is done so we take a new one
                    self.tasks_performed.append(self.task)
                    self.get_task()

        else:
            print('Robot {} can\'t do any task'.format(self.id))
            # No task was found. Internal timer is increased so that we wait longer before trying to get another task
            new_max_wait_time = min(2 * self.current_max_wait_time, self.max_wait_time)
            if new_max_wait_time != self.current_max_wait_time:
                self.current_max_wait_time = new_max_wait_time
            self.wait_time = self.current_max_wait_time

            self.task = None

    def compute_next_position(self, position: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        # If no position is provided
        if position is None and self.task is None:
            # print('Robot {} is retracting itself (task=None)'.format(self.id))
            return self.retract()
        else:
            return [position]

    def move(self) -> None:
        """
        Moves the robot arm according to the next position assigned to it
        (Assuming the following position is "valid" and consistent)
        """
        # We retract if we are supposed to wait
        if self.wait_time > 0:
            print('Waiting time = {} / {}'.format(self.wait_time, self.current_max_wait_time))
            self.wait_time -= 1
            self.planned_path = self.arm[::-1][1:]

        if not self.planned_path:
            # If there is no more planned path we compute a new one
            self.planned_path = self.compute_next_position()

        # We get the next position
        next_pos: Tuple[int, int] = self.planned_path[0]
        self.planned_path.pop(0)

        self.add_to_memory_path(next_pos)
        print("Robot {} is moving in {}".format(self.id, next_pos))

        # If robot needs to retract
        if [next_pos] == self.retract() and len(self.arm) > 1:
            self.arm.pop(-1)
        elif next_pos != self.arm[-1]:
            self.arm.append(next_pos)

        # Updating task (next position to be reached, status...)
        if self.task is not None:
            self.task.next_position(self.arm[-1])
            if self.task.status == 'done':
                self.tasks_performed.append(self.task)  # if the task is done, we add it to the list of performed tasks
                self.get_task()  # the robot then asks for a new task
        elif self.wait_time <= 0:
            self.get_task()

        # We update the global variable of Robot
        Robot.arms[self.id] = self.arm

    def retract(self) -> List[Tuple[int, int]]:
        """Returns the new position of the robot arm when retracting"""
        if len(self.arm) >= 2:
            return [self.arm[-2]]
        else:
            return [self.arm[0]]

    def add_to_memory_path(self, new_position: Tuple[int, int]) -> None:
        """
        Memorises the path traveled by the robot in a global variable (used to compile the output file)
        """
        position: Tuple[int, int] = self.arm[-1]
        if new_position[0] > position[0]:
            next_move = 'R'
        elif new_position[0] < position[0]:
            next_move = 'L'
        elif new_position[1] > position[1]:
            next_move = 'U'
        elif new_position[1] < position[1]:
            next_move = 'D'
        elif new_position == position:
            next_move = 'W'
        else:
            raise Exception('The requested position cannot be reached in one move!')

        Robot.memory_paths[self.id].append(next_move)

    def __str__(self) -> str:
        """str representation of the object for debugging purposes"""
        text: str = "Robot {} mounted at {}, ".format(self.id, self.arm[0])
        text += "task={}, position={}".format(self.task.id if self.task is not None else None, self.arm[-1])
        return text


if __name__ == "__main__":
    path: str = "../../input/a_example.txt"
    grid, tasks = input_parsing(path)
