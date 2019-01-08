# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 13:54:14 2019

@author: Mauro
"""

# append the src folder in the "searched paths"
import sys
sys.path.append("./src")

#==============================================================================
# Imports
#==============================================================================

import os

from tkinter import (Tk, Canvas, PhotoImage, mainloop, LabelFrame, Frame, Entry,
                    Label, Button, END, filedialog)

import Color
import Mandelbrot

#==============================================================================
# utility
#==============================================================================

def get_pathname(path):
    ''' Little function to split the path in path, name, extension'''
    path, nameext = os.path.split(path)
    name, ext = os.path.splitext(nameext)
    return path, name, ext

#==============================================================================
# Graph
#==============================================================================
      
class Graph:
    ''' This class manages the drawing of the function. The function is 
    converted in a PhotoImage object and then populated with various 
    colors.
    '''
    
    def __init__(self, rootf, width, height):
        
        self.width = width
        self.height = height
        
        # create a canvas with a green background
        bgcolor =  Color.Color(0, 255, 125)
        self.canvas = Canvas(rootf, width = width, height= height, bg= bgcolor.getcs(), bd = 0, relief="ridge", highlightthickness=0)
        
        # append the photoimage to the root so it doesn't get
        # garbage colloected
        rootf.image = PhotoImage(width=width, height=height)
        self.image = rootf.image
    
    def draw(self):
        ''' draws the image on the canvas'''
        dims = (self.width/2, self.height/2)
        self.canvas.create_image(dims, image=self.image, state="normal") 
    
    def update_image(self, matrix):
        ''' fills the PhotoImage with the color values
        color values have to be in the format '#FFAA00'
        '''
        for x in range(matrix.width):
            for y in range(matrix.height):
                color = matrix.get(x, y) 
                self.image.put(color.getcs(), (x,y)) 

class LabelEntry:
    ''' class that constructs an entry text field plus label in front of it
    '''
    
    def __init__(self, rootf, name, def_value = "0"):
        self.frame = Frame(rootf)
        
        l = Label(self.frame, text=name)
        l.grid(row = 0, column = 0)
        
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1)
        
        self.entry.insert(END, str(def_value))
        
    def set_color(self, color):
        self.entry.config({"background": color.getcs()})
    
        

class ControlPanel:
    ''' class controlling the input data for the mandelbrot function'''
    
    def __init__(self, rootf, graph):
        self.frame = LabelFrame(rootf, text="Control panel")
        
        self.mandelbrot = None
        
        # insert the various parameters boxes
        self.data_boxes = {}
        
        # function to initialize a labelled entry and put it in the right
        # position
        def place_entry(text, def_value, row, col, colspan=1):
            self.data_boxes[text] = LabelEntry(self.frame, text, def_value)
            self.data_boxes[text].frame.grid(row = row, 
                                             column = col, 
                                             columnspan=colspan)
        # parameters entries placement
        place_entry("x min", -2.0, 0, 0)
        place_entry("x max", 1.0, 0, 1)
        place_entry("y min", -1.25, 1, 0)
        place_entry("y max", 1.25, 1, 1)
        place_entry("max iterations", 25, 2, 0, 2)
        place_entry("mode", "iteration", 3, 0, 2)
        place_entry("colormap", "hot", 4, 0, 2)
        
        # place the buttons to render the image
        self.brender = Button(self.frame, text="Render", 
                              command = lambda : self.render(graph))
        self.brender.grid(row = 5, column = 0)
        
        # place the button to save the image
        self.bsave = Button(self.frame, text = "Save image", 
                            command = self.save_image)
        self.bsave.grid(row = 5, column = 1)
    
    def render(self, graph):
        ''' this function renders the mandelbrot into the graph, using the 
        parameters specified in the data boxes. If the input value is wrong
        the box will turn red
        '''
        # set the variables needed for input correctness
        correct_format = True
        
        # reset all entry box background to white
        for key in self.data_boxes.keys():
            self.data_boxes[key].set_color(Color.Color(255, 255, 255))
        
        # define input checking functions
        input_types = {}
        input_types["float"] = float
        input_types["int"] = int
        
        # if the input needs to be converted to a number
        def check_input(data_box_name, input_type):
            # this will be false if the format is not correct
            nonlocal correct_format
            
            # check if is valid
            try:
                item = self.data_boxes[data_box_name].entry.get()
                return input_types[input_type](item)
            except ValueError:
                # in case is wrong color the background of the box red
                self.data_boxes[data_box_name].set_color(Color.Color(255, 0, 0))
                return None
            
            # in case there is an unchecked exception this will set the format
            # to false so that doesnt trigger the rendering
            if correct_format:
                correct_format = False
        
        # this checks if the validity of the input by verifiying if it exist
        # as a possibility
        def check_presence(data_box_name, possibilities):
            nonlocal correct_format
            
            item = self.data_boxes[data_box_name].entry.get()
            if item in possibilities:
                return item
            else:
                self.data_boxes[data_box_name].set_color(Color.Color(255, 0, 0))
                if correct_format:
                    correct_format = False
            
        # gather the user inputs    
        minx = check_input("x min", "float")
        maxx = check_input("x max", "float")
        miny = check_input("y min", "float")
        maxy = check_input("y max", "float")
        it   = check_input("max iterations", "int")
        mode = check_presence("mode", Mandelbrot.available_modes)
        colormap = check_presence("colormap", Mandelbrot.available_colormaps)
        
        # run the render
        if correct_format:
            bounds = Mandelbrot.Boundaries(WIDTH, HEIGHT, minx, maxx, miny, maxy)
            self.mandelbrot = Mandelbrot.Mandelbrot(bounds, it, mode, colormap)
            
            color_matrix = self.mandelbrot.get_color_matrix()
            
            graph.update_image(color_matrix)
            graph.draw()     
            print("rendering done")
        
    def save_image(self):
        # asks for a filename
        path = filedialog.asksaveasfilename(initialdir = "./",
                                            title = "Save image as ...")
        
        # if the program was run and the path is valid
        if self.mandelbrot is not None and path is not None:
            p, name, ext = get_pathname(path)
            
            # if extention missing then attach a png to it
            if not ext:
                path += ".png"
                
            self.mandelbrot.save_image(path)

#==============================================================================
# Main program
#==============================================================================


if __name__ == "__main__":
    WIDTH, HEIGHT = 640, 480
    
    root = Tk()
    
    graph_frame = LabelFrame(root, text="Graph area")
    graph = Graph(graph_frame, WIDTH, HEIGHT)
    graph.canvas.grid(row = 0, column = 0)
    
    cp = ControlPanel(graph_frame, graph)
    cp.frame.grid(row = 0, column = 1)  
    
    graph_frame.pack()
    
    
    mainloop()






