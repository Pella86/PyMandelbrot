# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 23:55:50 2019

@author: Mauro
"""

import cmath

import matplotlib.image as mpimg
import numpy as np

import matplotlib

import Matrix
import Color

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
        

class Boundaries:
    
    def __init__(self, width, height, minx, maxx, miny, maxy):
        self.linx = Linspace(minx, maxx, width)
        self.liny = Linspace(miny, maxy, height)
    

class Mandelbrot:
    
    def __init__(self, boundaries, max_iteration):
        
        self.width = boundaries.linx.nsteps
        self.height = boundaries.liny.nsteps
        self.max_iteration = max_iteration
        self.color_matrix = None
        self.mandel_solution = None
        
        input_matrix = Matrix.Matrix(self.width, self.height)
 
        for i in range(input_matrix.width):
            for j in range(input_matrix.height):
                re = boundaries.linx.get(i)
                im = boundaries.liny.get(j)
                input_matrix.set(i, j, complex(re, im))

        print("calculating mandelbrot...")
        
        self.mandel_solution = Matrix.Matrix(self.width, self.height)
        for i in range(input_matrix.width):
            for j in range(input_matrix.height):
                c = input_matrix.get(i, j)
                # complex result of the iterations
                mr = self.calc_mandelbrot(c, "module");

                # structure that holds the in/out set value
                self.mandel_solution.set(i, j, mr)
    
    def value_mode(self, operation, value):
        if operation == "module":
            return abs(value)
        elif operation == "phase":
            return (cmath.phase(value)  + cmath.pi ) / (2 * cmath.pi) * 255
        elif operation == "imaginary":
            return value.imag
        elif operation == "real":
            return value.real
        
    def calc_mandelbrot(self, c, mode):
        z = complex(0, 0)
        
        in_set = True
        for i in range(self.max_iteration):
            z = z * z + c
            if abs(z) > 2:
                in_set = False
                break

        if mode == "iteration":
            val = i
        else:
            val = self.value_mode(mode, z)        
        
        mr = MandelResult(val, in_set)
        return mr
    
    def get_color_matrix(self):
        if self.color_matrix is None:
            self.color_matrix = self.convert_to_color_matrix()
        return self.color_matrix
    
    def convert_to_color_matrix(self):
        bgcolor = Color.Color(0, 0, 0)
        color_matrix = Matrix.Matrix(self.width, self.height, bgcolor)
        for i in range(self.mandel_solution.width):
            for j in range(self.mandel_solution.height):  
                if not self.mandel_solution.get(i, j).in_set:
                    value = self.mandel_solution.get(i, j).res
                    color = self.color_function("red", value)
                    color_matrix.set(i, j, color)
                else:
                    value = self.mandel_solution.get(i, j).res
                    color = self.color_function("blue", value)
                    color_matrix.set(i, j, color)
        
        return color_matrix
    
    def color_function(self, method, value):
        if method == "red":
            if value != 0:
                v = 255 / value
            else:
                v = 0
            color = Color.Color(255, 255 - int(v), 255 - int(v))
            
            return color
        if method == 'blue':
            if value != 0:
                v = 255 / value
            else:
                v = 0
            color = Color.Color(255 - int(v), 255 - int(v), 255)
            
            return color  
        
        if method == "black":
            return Color(0, 0, 0)
   
    
    def save_image(self, filename):
        color_matrix = self.get_color_matrix()
        
        arr = np.zeros([self.height, self.width, 3], np.uint8)
        
        for i in range(self.width):
            for j in range(self.height):
                color = color_matrix.get(i,j).get_limited()
                
                arr[j, i, 0] = color[0]
                arr[j, i, 1] = color[1]
                arr[j, i, 2] = color[2]   
        mpimg.imsave(filename, arr)



if __name__ == "__main__":
    
    print("Hello")
    n_frames = 50
    width = 640
    height = 480
    image_filename = r"C:\Users\Mauro\Desktop\Vita Online\Programming\PyMandelbrot\tests\anitest\\"
    
    x_start = -1.5
    x_end = 0.8
    y_start = -1
    y_end = 1
    
    zoom_x_start = -1.67
    zoom_x_end = -1.634
    zoom_y_start = -0.00001
    zoom_y_end = 0.00001
    
    lsx_start = Linspace(x_start, zoom_x_start, n_frames)
    lsx_end = Linspace(x_end, zoom_x_end, n_frames)
    lsy_start = Linspace(y_start, zoom_y_start, n_frames)
    lsy_end = Linspace(y_end, zoom_y_end, n_frames) 
    lit = Linspace(50, 500, n_frames)
    
    ls = Linspace(-1.5, 1, n_frames)
    for i in range( n_frames):
        
        bounds = Boundaries(width, height, lsx_start.get(i),
                                           lsx_end.get(i),
                                           lsy_start.get(i),
                                           lsy_end.get(i))
    
        mandelbrot = Mandelbrot(bounds, int(lit.get(i)))
        mandelbrot.save_image(image_filename + "test_" + str(i) + ".png")
    
    