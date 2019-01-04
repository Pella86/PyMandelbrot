# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 13:54:14 2019

@author: Mauro
"""

from tkinter import Tk, Canvas, PhotoImage, mainloop
from math import sin

import cmath

#WIDTH, HEIGHT = 640, 480
#
#window = Tk()
#canvas = Canvas(window, width=WIDTH, height=HEIGHT, bg="#000000")
#canvas.pack()
#img = PhotoImage(width=WIDTH, height=HEIGHT)
#canvas.create_image((WIDTH/2, HEIGHT/2), image=img, state="normal")
#
#for x in range(4 * WIDTH):
#    y = int(HEIGHT/2 + HEIGHT/4 * sin(x/80.0))
#    img.put("#ffffff", (x//4,y))
#
#mainloop()

def tohex(n):
    return '{:02X}'.format(n)


class Color:
    
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        
    def limit(self, n):
        limit0 = max(0, n)
        limit255 = min(255, limit0)
        return limit255
       
    def getcs(self):
        s = "#"
        s += tohex(self.limit(self.r))
        s += tohex(self.limit(self.g))
        s += tohex(self.limit(self.b))
        return s
    
class Linspace:
    
    def __init__(self, minv, maxv, nsteps):
        self.minv = minv
        self.maxv = maxv
        self.nsteps = nsteps
    
    def get(self, n):
        return (self.maxv - self.minv) / self.nsteps * n + self.minv

class MandelResult:
    
    def __init__(self, res, in_set):
        self.res = res
        self.in_set = in_set
    
class Mandelbrot:
    
    def __init__(self, w, h):
        self.input_matrix = Matrix(w, h)
        lsx = Linspace(-1.0, -0.5, w)
        lsy = Linspace(-0.25, 0.25, h)
        
        for i in range(self.input_matrix.width):
            for j in range(self.input_matrix.height):
                re = lsx.get(i)
                im = lsy.get(j)
                self.input_matrix.set(i, j, complex(re, im))
                
        print("calculating mandelbrot...")
        self.mandel_solution = Matrix(w, h)
        for i in range(self.input_matrix.width):
            for j in range(self.input_matrix.height):
                c = self.input_matrix.get(i, j)
                res = self.calc_mandelbrot(c);
                
                m = abs(res)
                #value = (cmath.phase(res)  + cmath.pi ) / (2 * cmath.pi) * 255
                value = abs(res)
                if m < 2:
                    mr = MandelResult(value, True)
                    self.mandel_solution.set(i, j, mr)
                else:
                    mr = MandelResult(value, False)
                    self.mandel_solution.set(i, j, mr)
            if (i*j) % 5 == 0:
                print("{:.2f}%".format(i*j / (self.input_matrix.height *self.input_matrix.width) ))
            

    def calc_mandelbrot(self, c):
        z = complex(0, 0)
        max_itr = 1000
        for i in range(max_itr):
            z = z * z + c
            if abs(z) > 2:
                break

        return z
    
    def convert_to_color_matrix(self):
        color_matrix = Matrix(self.input_matrix.width, self.input_matrix.height, Color(0, 0, 0))
        for i in range(self.mandel_solution.width):
            for j in range(self.mandel_solution.height):  
                if self.mandel_solution.get(i, j).in_set:
                    continue
                else:
                    try:
                        value = 255 / self.mandel_solution.get(i, j).res
                    except ZeroDivisionError:
                        value = 0
                    color_matrix.set(i, j, Color( 255, 255 - int(value), 255 - int(value)))
        
        return color_matrix

class Matrix:

    def __init__(self, width, height, init_element = 0):
        self.width = width
        self.height = height
        
        self.array = []
        for i in range(width * height):
            self.array.append(init_element)
    
    def calc_idx(self, x, y):
        return y * self.width + x
    
    def get(self, x, y):
        return self.array[self.calc_idx(x, y)]
    
    def set(self, x, y, v):
        self.array[self.calc_idx(x, y)] = v

 
class Graph:
    
    def __init__(self, rootf, width, height):
        
        self.width = width
        self.height = height
        
        bgcolor =  Color(0, 255, 0)
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



graph.update_image(m.convert_to_color_matrix())
graph.draw()

mainloop()


#WIDTH, HEIGHT = 100, 50
#root = Tk()
#graph = Graph(root, WIDTH, HEIGHT)
#graph.canvas.pack()
#
## create a color matrix
#
#colmat = Matrix(WIDTH, HEIGHT, Color(0, 0, 255))
#
#for x in range(10):
#    for y in range(10):
#        x_shift = x + 45
#        y_shift = y + 20
#        colmat.set(x_shift, y_shift, Color(255, 0, 0) )
#        
#graph.update_image(colmat)
#graph.draw()
#
#mainloop()

