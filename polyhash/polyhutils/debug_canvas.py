
"""This file provides a real-time graphical display of our algorithm.
 It is an adapted version of Mr. Perreira Da Silva's program (sent via discord)

 Display:

 mountpoints = light blue
 mountpoint(s) with arm = dark blue
 targetpoint (for the current task of the robot) = red
 obstacles = brown
 assembly point(s) reached = green
 arm and gripper = black line and black square

 """


import tkinter as tk
from PIL import ImageTk, Image, ImageDraw
from grid import Grid
from task import Task
from robot import Robot


class DebugCanvas:

    final_images = []

    def __init__(self, grid: Grid, gif, cells_size: int = 10):
        self.cpt: int = 0
        self.grid: Grid = grid
        # tkinter main class
        self.master: tk.Tk = tk.Tk()
        self.master.title('Affichage en temps réel')
        # a few parameters
        self.cell_size: int = cells_size
        self.width: int = cells_size * grid.width
        self.height: int = cells_size * grid.height
        # the debug image will be drawn on a label
        self.label: tk.Label = tk.Label(self.master, width=self.width, height=self.height)
        #  a new PIL image of the right size. We'll draw on that one
        self.img = Image.new("RGB", (self.width, self.height))
        # the PIL class for drawing on PIL images
        self.draw = ImageDraw.Draw(self.img)
        # resize the label and make the TK windows (always) topmost
        self.label.pack()
        self.master.attributes('-topmost', 'true')

        # To speed up things, we draw the grid and other stuffs once for all
        # draw all the cells
        self.img.paste((255, 255, 255), [0, 0, self.img.size[0], self.img.size[1]])
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                self.draw.rectangle([x * self.cell_size, y * self.cell_size, x * self.cell_size + self.cell_size,
                                     y * self.cell_size + self.cell_size], outline='grey')

        # then assembly points
        task: Task
        all_tasks = Task.remaining + Task.current + Task.performed  # pas d'attribut grid.tasks dans notre programme
        for task in all_tasks:
            for pt in task.path:
                fill_c = 'yellow'
                self.draw.rectangle([pt[0] * self.cell_size + 1, pt[1] * self.cell_size + 1,
                                     pt[0] * self.cell_size + self.cell_size - 1,
                                     pt[1] * self.cell_size + self.cell_size - 1], fill=fill_c)

        # then mount points
        for pt in self.grid.mount_points:
            self.draw.ellipse([pt[0] * self.cell_size, pt[1] * self.cell_size, pt[0] * self.cell_size + self.cell_size,
                               pt[1] * self.cell_size + self.cell_size], fill=(105, 123, 241))
        self.update(gif)

    def update(self, gif):
        """To update the graphical display to each new movement"""
        # cpt is just an index used when saving the debug frames (to create a gif for example)
        self.cpt += 1
        # Copy the pre-rendred image on a new image
        img = self.img.copy()
        self.draw = ImageDraw.Draw(img)

        # debug : draw blocked cells in grey
        for pt in self.grid:
            if pt not in self.grid.mount_points:
                x = pt[0]
                y = pt[1]
                self.draw.rectangle([x * self.cell_size, y * self.cell_size, x * self.cell_size + self.cell_size,
                                     y * self.cell_size + self.cell_size], fill=(185, 116, 85))

        # then assembly points (color depends on their state)
        task: Task
        # non-reached targetpoint colored in red
        # reached targetpoint colored in green
        for task in Task.current:
            for pt in task.path:
                if pt in task.target_points:
                    fill_c = (255, 0, 0)
                else:
                    fill_c = (47, 147, 0)
                self.draw.rectangle([pt[0] * self.cell_size + 1, pt[1] * self.cell_size + 1,
                                     pt[0] * self.cell_size + self.cell_size - 1,
                                     pt[1] * self.cell_size + self.cell_size - 1], fill=fill_c)

        # reached assemblypoints colored in green (fixing issue when task has a single assembly point)
        for task in Task.performed:
            for pt in task.path:
                self.draw.rectangle([pt[0] * self.cell_size + 1, pt[1] * self.cell_size + 1,
                                     pt[0] * self.cell_size + self.cell_size - 1,
                                     pt[1] * self.cell_size + self.cell_size - 1], fill=(47, 147, 0))

        robot: Robot
        # arms mount points in  dark blue
        for robot in self.grid.robots:
            pt = robot.arm[0]
            self.draw.ellipse([pt[0] * self.cell_size, pt[1] * self.cell_size, pt[0] * self.cell_size + self.cell_size,
                               pt[1] * self.cell_size + self.cell_size], fill=(20, 43, 188))

        # draw the arm (black lines)
        for robot in self.grid.robots:
            first: bool = True
            previous = None
            for pt in Robot.arms[robot.id]:  # arm.history:
                if first:
                    first = False
                else:
                    self.draw.line([self.cell_size / 2 + previous[0] * self.cell_size,
                                    self.cell_size / 2 + previous[1] * self.cell_size,
                                    self.cell_size / 2 + pt[0] * self.cell_size,
                                    self.cell_size / 2 + pt[1] * self.cell_size], fill='black',
                                   width=self.cell_size // 3)
                previous = pt
            # draw gripper (black square)
            pt = robot.arm[-1]
            if len(Robot.arms[robot.id]) > 0:
                self.draw.line([self.cell_size / 2 + previous[0] * self.cell_size,
                                self.cell_size / 2 + previous[1] * self.cell_size,
                                self.cell_size / 2 + pt[0] * self.cell_size,
                                self.cell_size / 2 + pt[1] * self.cell_size], fill='black', width=self.cell_size // 3)
            self.draw.rectangle(
                [pt[0] * self.cell_size + 1, pt[1] * self.cell_size + 1, pt[0] * self.cell_size + self.cell_size - 1,
                 pt[1] * self.cell_size + self.cell_size - 1], fill='black', width=self.cell_size // 3)

        # ----------------------------------- end of drawing --------------------------------------#

        # We need to flip the image horizontally because because axis are not the same in my arrays and in images
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        # Create a new Photoimage from the PIL image
        self.PhotoImage = ImageTk.PhotoImage(img)
        # Update the image
        self.label.configure(image=self.PhotoImage)
        self.label.update()

        # To save the image and then create an animated GIF (for fast executions)
        if gif:
            img.save("../debug/images/{:4d} Movement.jpg".format(self.cpt-1))
            DebugCanvas.final_images.append(img)

    def compile_gif(self):
        """To create an animated GIF from images saved with every movement (for fast executions)
        file saved in "debug" directory """
        DebugCanvas.final_images[0].save("../debug/debug.gif", save_all=True,
                                         append_images=DebugCanvas.final_images[1:],
                                         optimize=False, duration=200, loop=0)
