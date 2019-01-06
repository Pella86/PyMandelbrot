# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 23:54:42 2019

@author: Mauro
"""

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

    def normalize01(self):
        # values in the mandel solution have to be normalized from 0 to 1
        max_sol = max(self.array)
        min_sol = min(self.array)
        for i in range(self.width):
            for j in range(self.height):
                norm_value = (self.get(i, j) - min_sol ) / (max_sol - min_sol)
                self.set(i, j, norm_value)