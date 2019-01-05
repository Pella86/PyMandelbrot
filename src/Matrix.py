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