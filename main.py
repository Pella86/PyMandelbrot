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

from tkinter import Tk, Canvas, PhotoImage, mainloop

import matplotlib.image as mpimg
import numpy as np

import Color



#==============================================================================
# 
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

WIDTH, HEIGHT = 640, 480

m = Mandelbrot(WIDTH, HEIGHT)

root = Tk()
graph = Graph(root, WIDTH, HEIGHT)
graph.canvas.pack()

color_matrix = m.convert_to_color_matrix()

m.save_image("test_1.png")

graph.update_image(color_matrix)
graph.draw()

mainloop()


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

