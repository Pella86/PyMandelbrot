# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 23:46:17 2019

@author: Mauro
"""

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
    
    def get_limited(self):
        r = self.limit(self.r)
        g = self.limit(self.g)
        b = self.limit(self.b)
        return (r, g, b)