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

from tkinter import (Tk, Canvas, PhotoImage, mainloop, LabelFrame, Frame, Entry,
                    Label, Button, END)

import Color
import Mandelbrot

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
    
    def __init__(self, rootf, name, def_value = "0"):
        self.frame = Frame(rootf)
        
        l = Label(self.frame, text=name)
        l.grid(row = 0, column = 0)
        
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1)
        
        self.entry.insert(END, str(def_value))
    
        

class ControlPanel:
    ''' class controlling the input data for the mandelbrot function'''
    
    def __init__(self, rootf, graph):
        self.frame = LabelFrame(rootf, text="Control panel")
        
        self.mandelbrot = None
        
        # insert the various parameters boxes
        self.data_boxes = {}
        
        def place_entry(text, def_value, row, col, colspan=1):
            self.data_boxes[text] = LabelEntry(self.frame, text, def_value)
            self.data_boxes[text].frame.grid(row = row, 
                                             column = col, 
                                             columnspan=colspan)
        
        place_entry("x min", -2.0, 0, 0)
        place_entry("x max", 0.5, 0, 1)
        place_entry("y min", -1.25, 1, 0)
        place_entry("y max", 1.25, 1, 1)
        place_entry("max iterations", 25, 2, 0, 2)
        place_entry("mode", "module", 3, 0, 2)
        place_entry("colormap", "hot", 4, 0, 2)
        
        # insert the buttons to render and save image
        self.brender = Button(self.frame, text="Render", 
                              command = lambda : self.render(graph))
        self.brender.grid(row = 5, column = 0)
        
        self.bsave = Button(self.frame, text = "Save image", 
                            command = self.save_image)
        self.bsave.grid(row = 5, column = 1)
    
    def render(self, graph):
        ''' this function renders the mandelbrot into the graph, using the 
        parameters specified in the data boxes
        '''
        
        correct_format = True
        
        try:
            minx = float(self.data_boxes["x min"].entry.get())
            maxx = float(self.data_boxes["x max"].entry.get())
            miny = float(self.data_boxes["y min"].entry.get())
            maxy = float(self.data_boxes["y max"].entry.get())
            it = int(self.data_boxes["max iterations"].entry.get())
            mode = str(self.data_boxes["mode"].entry.get())
            colormap = str(self.data_boxes["colormap"].entry.get())
        except ValueError:
            # add a dialog box
            print("data boxes have wrong format")
            correct_format = False
            pass
        
        if correct_format:
            bounds = Mandelbrot.Boundaries(WIDTH, HEIGHT, minx, maxx, miny, maxy)
            self.mandelbrot = Mandelbrot.Mandelbrot(bounds, it, mode)
            
            color_matrix = self.mandelbrot.convert_to_color_matrix()
            
            graph.update_image(color_matrix)
            graph.draw()        
        
    def save_image(self):
        if self.mandelbrot is not None:
            self.mandelbrot.save_image("./tests/test_saveimg.png")

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





