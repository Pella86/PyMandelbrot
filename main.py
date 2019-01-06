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
                    Label, Button, StringVar, END)

import Color
import Mandelbrot

#==============================================================================
# Graph
#==============================================================================
 
class Graph:
    
    def __init__(self, rootf, width, height):
        
        self.width = width
        self.height = height
        
        bgcolor =  Color.Color(0, 255, 0)
        self.canvas = Canvas(rootf, width = width, height= height, bg= bgcolor.getcs(), bd = 0, relief="ridge", highlightthickness=0)
        
        rootf.image = PhotoImage(width=width, height=height)
        self.image = rootf.image
    
    def draw(self):
        dims = (self.width/2, self.height/2)
        self.canvas.create_image(dims, image=self.image, state="normal") 
    
    def update_image(self, matrix):
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
    
    def __init__(self, rootf, graph):
        self.frame = LabelFrame(rootf, text="Control panel")
        self.minx = LabelEntry(self.frame, "minx", -2.0)
        self.minx.frame.grid(row = 0, column = 0)

        self.maxx = LabelEntry(self.frame, "maxx", 0.5)
        self.maxx.frame.grid(row = 0, column = 1)        

        self.miny = LabelEntry(self.frame, "miny", -1.25)
        self.miny.frame.grid(row = 1, column = 0)          

        self.maxy = LabelEntry(self.frame, "maxy", 1.25)
        self.maxy.frame.grid(row = 1, column = 1)  
    
        self.it = LabelEntry(self.frame, "iterations", 25)
        self.it.frame.grid(row = 2, column = 0, columnspan= 2)   

        self.mode = LabelEntry(self.frame, "mode", "module")
        self.mode.frame.grid(row = 3, column = 0, columnspan= 2)
    
        self.brender = Button(self.frame, text="Render", command = lambda : self.render(graph))
        self.brender.grid(row = 4, column = 0, columnspan = 2)
    
    def render(self, graph):
        minx = float(self.minx.entry.get())
        maxx = float(self.maxx.entry.get())
        miny = float(self.miny.entry.get())
        maxy = float(self.maxy.entry.get())
        it = int(self.it.entry.get())
        mode = str(self.mode.entry.get())
        
        bounds = Mandelbrot.Boundaries(WIDTH, HEIGHT, minx, maxx, miny, maxy)
        m = Mandelbrot.Mandelbrot(bounds, it, mode)
        
        color_matrix = m.convert_to_color_matrix()
        
        graph.update_image(color_matrix)
        graph.draw()        
        
        
        

WIDTH, HEIGHT = 640, 480


root = Tk()
graph = Graph(root, WIDTH, HEIGHT)
graph.canvas.grid(row = 0, column = 0)

cp = ControlPanel(root, graph)
cp.frame.grid(row = 0, column = 1)

#entry = Entry(root)
#entry.pack()
#
#def get_float():
#    print(repr(entry.get()))
#
#button = Button(root, text="press me", command=get_float)
#button.pack()

mainloop()


#bounds = Mandelbrot.Boundaries(WIDTH, HEIGHT, -2, 0.5, -1.25, 1.25)
#m = Mandelbrot.Mandelbrot(bounds, 25)
#
#color_matrix = m.convert_to_color_matrix()
#
#graph.update_image(color_matrix)
#graph.draw()

#mainloop()


#WIDTH, HEIGHT = 100, 50
#root = Tk()
#graph = Graph(root, WIDTH, HEIGHT)
#graph.canvas.pack()
#
## create a color matrix
#
#colmat = Matrix.Matrix(WIDTH, HEIGHT, Color.Color(0, 0, 255))
#
#for x in range(10):
#    for y in range(10):
#        x_shift = x + 45
#        y_shift = y + 20
#        colmat.set(x_shift, y_shift, Color.Color(255, 0, 0) )
#        
#graph.update_image(colmat)
#graph.draw()
#
#mainloop()

