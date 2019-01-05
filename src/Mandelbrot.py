# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 23:55:50 2019

@author: Mauro
"""

import matplotlib.image as mpimg
import numpy as np

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
    
    def __init__(self, width, height, max_iteration, boundaries):
        self.width = width
        self.height = height
        self.max_iteration = max_iteration
        
        input_matrix = Matrix.Matrix(self.width, self.height)
        
        lsx = Linspace(-1.5, 1, self.width)
        lsy = Linspace(-1, 1, self.height)
        
        for i in range(input_matrix.width):
            for j in range(input_matrix.height):
                re = lsx.get(i)
                im = lsy.get(j)
                input_matrix.set(i, j, complex(re, im))
                
        
        print("calculating mandelbrot...")
        
        self.mandel_solution = Matrix.Matrix(self.width, self.height)
        for i in range(input_matrix.width):
            for j in range(input_matrix.height):
                c = input_matrix.get(i, j)
                res = self.calc_mandelbrot(c);
                
                m = abs(res)
                #value = (cmath.phase(res)  + cmath.pi ) / (2 * cmath.pi) * 255
                value = abs(res)
                
                in_set = True if m < 2 else False
                mr = MandelResult(value, in_set)
                self.mandel_solution.set(i, j, mr)
            
            if (i*j) % 5 == 0:
                print("{:.2f}%".format(i*j / (self.height * self.width) ))
            

    def calc_mandelbrot(self, c):
        z = complex(0, 0)
        max_itr = 25
        for i in range(max_itr):
            z = z * z + c
            if abs(z) > 2:
                break

        return z
    
    def convert_to_color_matrix(self):
        bgcolor = Color.Color(0, 0, 0)
        color_matrix = Matrix.Matrix(self.width, self.height, bgcolor)
        for i in range(self.mandel_solution.width):
            for j in range(self.mandel_solution.height):  
                if not self.mandel_solution.get(i, j).in_set:
                    value = self.mandel_solution.get(i, j).res
                    color = self.color_function("red", value)
                    color_matrix.set(i, j, color)
#                    try:
#                        value = 255 / self.mandel_solution.get(i, j).res
#                    except ZeroDivisionError:
#                        value = 0
#                    color_matrix.set(i, j, Color.Color( 255, 255 - int(value), 255 - int(value)))
        
        return color_matrix
    
    def color_function(self, method, value):
        if method == "red":
            if value != 0:
                v = 255 / value
            else:
                v = 0
            color = Color.Color(255, 255 - int(v), 255 - int(v))
            
            return color
        
    
    def save_image(self, filename):
        color_matrix = self.convert_to_color_matrix()
        
        arr = np.zeros([self.height, self.width, 3], np.uint8)
        
        for i in range(self.width):
            for j in range(self.height):
                arr[j, i, 0] = color_matrix.get(i,j).r
                arr[j, i, 1] = color_matrix.get(i,j).g
                arr[j, i, 2] = color_matrix.get(i,j).b        
        mpimg.imsave(filename, arr)



if __name__ == "__main__":
    
    print("Hello")