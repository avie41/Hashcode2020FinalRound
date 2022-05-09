#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from polyhutils.grid import Grid

__all__ = ['main_model']


def main_model(grid_file: str, drawing: bool = False, gif: bool = False):
    """
    grid_file : input file containing google_hash data
    drawing : boolean value enabling Real-time graphical display (helps debugging, but leads to long execution times)
    gif : boolean value allowing the compiling of a GIF image at the end of the execution (short execution times)
    """

    grid: Grid = Grid(grid_file, robot_percent=0.1, task_limit=2, pathfinder=0.1)

    if drawing:
        from debug_canvas import DebugCanvas
        debug: DebugCanvas = DebugCanvas(grid, gif)

    for i in range(grid.step_nb):
        print("\n####### {} Movement #######".format(i))

        if drawing:
            debug.update(gif)

        grid.move_robots()

    grid.compile_output('output')

    if gif:
        # compiles the GIF when we chose to save the images (in debug_canvas)
        debug.compile_Gif()


if __name__ == "__main__":
    main_model('../input/d_tight_schedule.txt', drawing=True, gif=False)
