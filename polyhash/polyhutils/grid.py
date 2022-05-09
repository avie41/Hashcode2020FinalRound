#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creating the grid object from the information of the input file
"""

from typing import List, Dict, Tuple, Set
from robot import Robot
from task import Task
from pathfinding import PathFinder
from polyhio import input_parsing
from distances import manhattan
import re


__all__ = ['Grid']


class Grid(set):
    """
    Set of points which constitute the obstacles
    Type : Set[Tuple[int,int]]
    This object inherits the set object.
    """

    def __init__(self, grid_file_name: str, robot_percent=1, task_limit=1, pathfinder=0.5):
        """Grid initialisation"""

        set.__init__(self)
        # Keeping file name in memory for output
        pattern: str = r'/._'
        self.grid_name: str = re.findall(pattern, grid_file_name)[0][1]
        self.features: List = [robot_percent, task_limit, pathfinder]

        # Getting information of the grid
        grid, tasks = input_parsing(grid_file_name)

        self.width, self.height = grid[0], grid[1]
        self.nb_robots: int = int(grid[2] * robot_percent)  # Maximum number of robots on the Grid
        self.step_nb: int = grid[3]  # maximum number of steps
        self.missions: List[List[Tuple[int, int]]] = tasks[1]  # list of missions (a mission = list of several points)
        self.scores_missions: List[int] = tasks[0]  # list of mission scores (in the same order as self.missions)
        self.mount_points: List[Tuple[int, int]] = grid[4]  # list containing the coordinates of the mounting points

        print("Global tasks score: ", (sum(self.scores_missions)))

        # We add the coordinates of the mounting points as obstacles
        for point in self.mount_points:
            self.add(point)

        print("Grid of {}x{}".format(self.width, self.height))
        print("{} tasks, {} robots & {} mounting points.".format(len(self.missions), self.nb_robots,
                                                                 len(self.mount_points)))
        print('Possible mounting points: ', self.mount_points)

        self.finder = PathFinder(self, (self.width, self.height, self.step_nb), limit=pathfinder)

        # Tasks initialisation
        for i in range(len(self.scores_missions)):
            Task(self.missions[i], self.scores_missions[i])

        # Robots initialisation
        self.sort_mount_points()
        self.robots: List = []
        for i in range(self.nb_robots):
            self.robots.append(Robot(tuple(self.mount_points[i]), self.finder, self.height, self.width, task_limit=task_limit))
            # Update the obstacles
            self.update_obstacles()

    def sort_mount_points(self) -> None:
        """
        Chooses the mounting points closest to the task to be carried out in order to optimize the robot's path.
        The distances between the mounting points and the first assembly point of the tasks are compared.
        """

        mount_points_value: List[int] = [0] * len(self.mount_points)

        # Calculating, for every task, which is the closest mounting point to their first assembly point
        for i, task in enumerate(Task.remaining):
            distances: List[Tuple[Tuple, int]] = [(mp, manhattan(mp, task.path[0])) for mp in self.mount_points]
            distances.sort(key=lambda a: a[1])
            closest_mp: Tuple[int, int] = distances[0][0]  # closest mounting point to the 1st assembly pt of the task
            # counting for each mounting point the number of occurrences as the closest point to a task
            mount_points_value[self.mount_points.index(closest_mp)] += 1   
        # Sorting the mounting points based on the number of assembly points nearby
        auxiliary: List[Tuple[Tuple, int]] = sorted(list(zip(self.mount_points, mount_points_value)),
                                                    key=lambda a: a[1], reverse=True)
        self.mount_points: List[Tuple[int, int]] = [a for a, _ in auxiliary]

    def move_robots(self) -> None:
        """
        Computing next_position and resolving conflicts
        """
        # Sorting by score, putting the robots without task at the end
        # in order to let the robots having a task move first
        robots_no_tasks: List[Robot] = [robot for robot in self.robots if robot.task is None]
        robots_others: List[Robot] = [robot for robot in self.robots if robot.task is not None]
        robots_others.sort(key=lambda r: r.task.ratio, reverse=True)
        self.robots: List[Robot] = robots_others + robots_no_tasks

        for robot in self.robots:
            # Actually moving the robots
            robot.move()
            # Updating the obstacles now that robots have moved
            self.update_obstacles()

        # Decreasing the number of movements left
        self.finder.nb_movements -= 1

    def update_obstacles(self) -> None:
        """
        Retrieves the positions of the arms in order to fill the obstacles for the next_round.
        """
        # One movement has passed so we have to update obstacles
        self.clear()  # The set of obstacles is reset
        self.update(self.mount_points)
        for robot in self.robots:
            # adding points currently in the planned path of each robot or in their arm
            for obstacles in robot.planned_path + robot.arm[1:]:
                if obstacles not in self:
                    self.add(obstacles)

        self.finder.update_obstacles(self)

    def compile_output(self, filename: str) -> None:
        """Compiles the output file"""
        final_score: int = 0
        # Number of robotic arms used
        active_robots: List[Robot] = [robot for robot in self.robots if len(robot.tasks_performed) > 0]
        txt: str = str(len(active_robots))
        for r in active_robots:
            # Mounting point of the arm
            txt += '\n' + str(r.arm[0][0]) + ' ' + str(r.arm[0][1]) + ' '
            # Number of tasks, number of movements
            txt += str(len(r.tasks_performed)) + ' ' + str(len(Robot.memory_paths[r.id])) + '\n'
            # Tasks performed
            txt += ' '.join([str(t.id) for t in r.tasks_performed])

            for t in r.tasks_performed:
                final_score += t.score

            txt += '\n' + str(" ".join(Robot.memory_paths[r.id]))

        # We decided to hardcode the simulation parameters in the file name.
        filename = "{}_{}_{}_{}_{}_{}.txt".format(self.grid_name, *self.features, filename, final_score)
        with open(filename, 'w') as f:
            f.write(txt)

        print('Score = ', final_score)


if __name__ == '__main__':
    path: str = "../../input/a_example.txt"
    grid: Grid = Grid(path)
    for i in range(grid.step_nb):
        print("\n####### {} Movement #######".format(i))
        grid.move_robots()
    # grid.compile_output('output')
