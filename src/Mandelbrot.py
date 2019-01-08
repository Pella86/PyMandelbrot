# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 23:55:50 2019

@author: Mauro
"""

#==============================================================================
# Imports
#==============================================================================

# pyimports
import cmath

# matliplot/numpy
#  side note, these are unnecessary, used for colormap and save image
import matplotlib
import matplotlib.image as mpimg
import numpy as np

# user imports
import Matrix
import Color

#==============================================================================
# Linearization calss
#==============================================================================

class Linspace:
    '''Allows to space in equal step between two numbers'''
    
    def __init__(self, minv, maxv, nsteps):
        self.minv = minv
        self.maxv = maxv
        self.nsteps = nsteps
    
    def get(self, n):
        return (self.maxv - self.minv) / self.nsteps * n + self.minv

#==============================================================================
# Mandelbrot result object
#==============================================================================

class MandelResult:
    ''' the result of the mandelbrot function is stored in a value and a 
    boolean variable which tells if the number is in the set or not
    the operator overload allows the normalization and sorting of said values
    '''
    
    def __init__(self, res, in_set):
        self.res = res
        self.in_set = in_set

    def __lt__(self, other):
        return self.res < other.res
            
    def __le__(self, other):
        return self.res <= other.res
    
    def __eq__(self, other):
        return self.res == other.res
    
    def __ne__(self, other):
        return self.res != other.res
    
    def __gt__(self, other):
        return self.res >= other.res
    
    def __ge__(self, other):
        return self.res > other.res

    def __sub__(self, other):
        r = self.res - other.res
        return MandelResult(r, self.in_set)

    def __truediv__(self, other):
        r = self.res / other.res
        return MandelResult(r, self.in_set)

#==============================================================================
# A class to store the boundaries
#==============================================================================

class Boundaries:
    
    def __init__(self, width, height, minx, maxx, miny, maxy):
        self.linx = Linspace(minx, maxx, width)
        self.liny = Linspace(miny, maxy, height)
    
    def get_width(self):
        return self.linx.nsteps
    
    def get_height(self):
        return self.liny.nsteps

class Mandelbrot:
    
    def __init__(self, boundaries, max_iteration, mode, colormap):
        
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
                mr = self.calc_mandelbrot(c, mode);

                # structure that holds the in/out set value
                self.mandel_solution.set(i, j, mr)
    
    def value_mode(self, operation, value):
        operations = {}
        operations["module"] = abs(value)
        operations["phase"] = (cmath.phase(value)  + cmath.pi ) / (2 * cmath.pi)
        operations["imaginary"] = value.imag
        operations["real"] = value.real
        return operations[operation]
        
    def calc_mandelbrot(self, c, mode):
        z = complex(0, 0)
        
        in_set = True
        i = 0
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
        
        self.mandel_solution.normalize01()
        
        for i in range(self.mandel_solution.width):
            for j in range(self.mandel_solution.height):  
                if not self.mandel_solution.get(i, j).in_set:
                    value = self.mandel_solution.get(i, j).res
                    color = self.color_function("seismic", value)
                    color_matrix.set(i, j, color)
                else:
                    value = self.mandel_solution.get(i, j).res
                    color = self.color_function("black", value)
                    color_matrix.set(i, j, color)
        
        return color_matrix
    
    def color_function(self, method, value):
        if method == "red":
            if value != 0:
                v = int(255 * value)
            else:
                v = 0
            color = Color.Color(255, 255 - int(v), 255 - int(v))
            
            return color
        if method == 'blue':
            if value != 0:
                v = int(255 * value)
            else:
                v = 0
            color = Color.Color(255 - int(v), 255 - int(v), 255)
            
            return color  
        
        if method == "black":
            return Color.Color(0, 0, 0)
        
        if method == "yellow":
            
            v = int( value * 255 )
            color = Color.Color(255, v, 0)
            return color
        
        if method == "seismic":
            cmap = matplotlib.cm.get_cmap("hot")
            cmapv = cmap(value)
            val = lambda i : int(cmapv[i] * 255)
            color = Color.Color(val(0), val(1), val(2))
            return color
   
    
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
    width = 1024
    height = 786
    image_filename = r"C:\Users\Mauro\Desktop\Vita Online\Programming\PyMandelbrot\tests\\"
    
    bounds = Boundaries(width, height, -1.7, 0.7, -1, 1)
    mandelbrot = Mandelbrot(bounds, 25)
    mandelbrot.save_image(image_filename + "test_colors.png")
    
#    x_start = -1.5
#    x_end = 0.8
#    y_start = -1
#    y_end = 1
#    
#    zoom_x_start = -1.67
#    zoom_x_end = -1.634
#    zoom_y_start = -0.00001
#    zoom_y_end = 0.00001
#    
#    lsx_start = Linspace(x_start, zoom_x_start, n_frames)
#    lsx_end = Linspace(x_end, zoom_x_end, n_frames)
#    lsy_start = Linspace(y_start, zoom_y_start, n_frames)
#    lsy_end = Linspace(y_end, zoom_y_end, n_frames) 
#    lit = Linspace(50, 500, n_frames)
#    
#    ls = Linspace(-1.5, 1, n_frames)
#    for i in range( n_frames):
#        
#        bounds = Boundaries(width, height, lsx_start.get(i),
#                                           lsx_end.get(i),
#                                           lsy_start.get(i),
#                                           lsy_end.get(i))
#    
#        mandelbrot = Mandelbrot(bounds, int(lit.get(i)))
#        mandelbrot.save_image(image_filename + "test_" + str(i) + ".png")
    
    