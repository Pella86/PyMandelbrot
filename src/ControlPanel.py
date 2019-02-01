# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 09:35:42 2019

@author: Mauro
"""

#==============================================================================
# imports
#==============================================================================

import os

from tkinter import (LabelFrame, Button, DISABLED, filedialog, Checkbutton,
                     IntVar)

import InputEntry
import Mandelbrot
import Color

#==============================================================================
# utilies
#==============================================================================

def get_pathname(path):
    ''' Little function to split the path in path, name, extension'''
    path, nameext = os.path.split(path)
    name, ext = os.path.splitext(nameext)
    return path, name, ext


#==============================================================================
# Mandelbrot parameters
#==============================================================================

class ControlPanel:
    ''' class controlling the input data for the mandelbrot function'''

    def __init__(self, rootf, graph):
        self.frame = LabelFrame(rootf, text="Control panel")

        self.mandelbrot = None
        
        self.data_boxes = InputEntry.DataBoxes(self.frame)

        # parameters entries placement
        self.data_boxes.place_entry("x min",         -2.0,  "float", 0, 0)
        self.data_boxes.place_entry("x max",          1.0,  "float", 0, 1)
        self.data_boxes.place_entry("y min",         -1.25, "float", 1, 0)
        self.data_boxes.place_entry("y max",          1.25, "float", 1, 1)
        self.data_boxes.place_entry("max iterations", 25,   "int",   2, 0, 2)
        self.data_boxes.place_entry("mode",    "iteration", "str",   3, 0, 2)
        self.data_boxes.place_entry("colormap",      "hot", "str",   4, 0, 2)

        # place the buttons to render the image
        self.brender = Button(self.frame, text="Render",
                              command = lambda: self.render(graph))
        self.brender.grid(row = 5, column = 0)

        # place the button to save the image
        self.bsave = Button(self.frame, text = "Save image",
                            command = self.save_image)
        self.bsave.grid(row = 5, column = 1)
        if not Mandelbrot.matlib_available:
            self.bsave["state"] = DISABLED

    def render(self, graph):
        ''' this function renders the mandelbrot into the graph, using the
        parameters specified in the data boxes. If the input value is wrong
        the box will turn red
        '''

        # gather the user inputs and check validity
        minx = self.data_boxes.get("x min")
        maxx = self.data_boxes.get("x max")
        miny = self.data_boxes.get("y min")
        maxy = self.data_boxes.get("y max")
        it   = self.data_boxes.get("max iterations")
        
        # this user inputs are strings so they will always be in a valid
        # format.
        # yet they are keys into dictonaries, so if the key is missng
        # the error handling is inside the next body
        mode = self.data_boxes.data_boxes["mode"].entry.get()
        colormap = self.data_boxes.data_boxes["colormap"].entry.get()

        print("start rendering...")
        print("max iteration: " + str(it))
        
        # run the render
        correct_format = [True if v is not None else False for v in [minx, maxx, miny, maxy, it]]
        
        if any(correct_format) :
            color_matrix = None
            # this will try to render the mandelbrot, if the mode or the
            # colormaps are wrong it will turn the boxes red
            try:
                bounds = Mandelbrot.Boundaries(graph.width, graph.height,
                                               minx, maxx, miny, maxy)
                self.mandelbrot = Mandelbrot.Mandelbrot(bounds, it,
                                                        mode,
                                                        colormap)
                color_matrix = self.mandelbrot.get_color_matrix()
                
            except Mandelbrot.KeyErrorMode:
                self.data_boxes.data_boxes["mode"].set_color(Color.Color(255, 0, 0))

            except Mandelbrot.KeyErrorColormap:
                self.data_boxes.data_boxes["colormap"].set_color(Color.Color(255, 0, 0))
            
            if color_matrix is not None:
                graph.update_image(color_matrix)
                graph.draw()
                print("rendering done")

    def save_image(self):
        # asks for a filename
        path = filedialog.asksaveasfilename(initialdir = "./",
                                            title = "Save image as ...")

        # if the program was run and the path is valid
        if self.mandelbrot is not None and path is not None:
            _, _, ext = get_pathname(path)

            # if extention missing then attach a png to it
            if not ext:
                path += ".png"

            self.mandelbrot.save_image(path)
            
#==============================================================================
# Zoom-in function
#==============================================================================

class Zoom:
    ''' the class manages the zooming in function and relative red square on
    the graph
    '''
    
    def __init__(self, rootf, graph, control_panel):
        
        # keep a reference of the graph area and control paknel
        self.graph = graph
        self.graph.canvas.bind("<Button-1>", lambda e : self.clicked(e))
        
        self.control_panel = control_panel
        
        # create the frame for the buttons
        self.frame = LabelFrame(rootf, text="Zoom options")
        
        # create the input boxes
        self.inputs = InputEntry.DataBoxes(self.frame) 
        
        # create the entries for the zoomed width and height
        self.inputs.place_entry("width", 0.0, "float", 0, 0)
        self.inputs.bind(
                "width",
                "<Return>",
                lambda e : 
                    self.update_rectangle(e, "width"))
        
        self.inputs.place_entry("height", 0.0, "float", 0, 1) 
        self.inputs.bind(
                "height",
                "<Return>", 
                lambda e : 
                    self.update_rectangle(e, "height"))
        
        # have variables that describe the coordinates between the mandelbrot
        # coordinates and the graph coordinates
        self.mandel_coords_x = None
        self.mandel_coords_y = None
        self.graph_coords_x = None
        self.graph_coords_y = None
        
        # store the ratio, useful for maintain proportions
        self.ratio = None

        self.maintain_proportion = IntVar(value=1)
        
        check_prop = Checkbutton(self.frame, text = "maintain proportions", variable=self.maintain_proportion)
        check_prop.grid(row=1, columnspan=2)
        
        # place the center
        self.inputs.place_entry("center_x", 0.0, "float", 2, 0)
        self.inputs.place_entry("center_y", 0.0, "float", 2, 1)
        
        self.center = (0, 0)

        #update the data boxes 
        self.calc_proportions() 
        
        # zoom and render
        bzoom_render = Button(self.frame, text="zoom and render", command= self.zoom_render)
        bzoom_render.grid(row = 3, column = 0, columnspan = 2)


    def calc_proportions(self): 
        xmin = self.control_panel.data_boxes.get("x min")
        xmax = self.control_panel.data_boxes.get("x max")        
        ymin = self.control_panel.data_boxes.get("y min")
        ymax = self.control_panel.data_boxes.get("y max") 
        print(xmin, xmax, ymin, ymax)
        
        zoom_width = (xmax - xmin) / 10
        zoom_height = (ymax - ymin) / 10
        
        self.ratio = zoom_width / zoom_height
        
        self.inputs.set("width", zoom_width)
        self.inputs.set("height", zoom_height)
        self.inputs.set("center_x", zoom_width / 2)
        self.inputs.set("center_y", zoom_height / 2)
        
        self.mandel_coords_x = Mandelbrot.Linspace(xmin, xmax, self.graph.width)
        self.mandel_coords_y = Mandelbrot.Linspace(ymin, ymax, self.graph.height)
        
        self.graph_coords_x = Mandelbrot.RLinspace(xmin, xmax, self.graph.width)
        self.graph_coords_y = Mandelbrot.RLinspace(ymin, ymax, self.graph.height)
        
    
    def update_rectangle(self, e, name):
        
        if self.maintain_proportion.get() == 1:
            if name == "width":
                width = self.inputs.get("width")
                self.inputs.set("width", width)
                self.inputs.set("height", width / self.ratio)
            if name == "height":
                height = self.inputs.get("height")
                self.inputs.set("height", height)
                self.inputs.set("width", height * self.ratio)
        
        
        self.draw_rectangle()
    
    def draw_rectangle(self):

        half_w = self.inputs.get("width") / 2 
        half_h = self.inputs.get("height") / 2
        
        x_clicked = self.center[0]
        y_clicked = self.center[1]        
        
        x1 = x_clicked - half_w
        y1 = y_clicked - half_h
        x2 = x_clicked + half_w
        y2 = y_clicked + half_h
        
        x1 = int(self.graph_coords_x.get(x1))
        x2 = int(self.graph_coords_x.get(x2))
        y1 = int(self.graph_coords_y.get(y1))
        y2 = int(self.graph_coords_y.get(y2)) 
        
        
        self.graph.draw_rectangle((x1, y1, x2, y2), Color.Color(255, 0, 0))

    def clicked(self, event):
        
        x_mandel = self.mandel_coords_x.get(event.x)
        y_mandel = self.mandel_coords_y.get(event.y)
        
        self.center = (x_mandel, y_mandel)
        
        self.inputs.set("center_x", x_mandel)
        self.inputs.set("center_y", y_mandel)  
        
        self.draw_rectangle()
    
    def zoom_render(self):
        # set the values using the center and width from the boxes
        # start the render
        self.inputs.reset()
        
        x = self.inputs.get("center_x")
        y = self.inputs.get("center_y")
        
        w = self.inputs.get("width") 
        h = self.inputs.get("height")
        
        new_xmin = x - w / 2
        new_xmax = x + w / 2
        new_ymin = y - h / 2
        new_ymax = y + h / 2
        
        
        correct_format = [True if v is not None else False for v in [new_xmin, new_xmax, new_ymin, new_ymax]]        
        
        
        if all(correct_format):
        
            self.control_panel.data_boxes.set("x min", new_xmin)
            self.control_panel.data_boxes.set("x max", new_xmax)
            self.control_panel.data_boxes.set("y min", new_ymin)
            self.control_panel.data_boxes.set("y max", new_ymax)
            
            self.calc_proportions()
            
            self.control_panel.render(self.graph)
