# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 23:46:17 2019

@author: Mauro
"""

def tohex(n):
    return '{:02X}'.format(n)


class Color:
    ''' simple color class
    the values can be limited from 0 to 255
    '''

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def limit(self, n):
        ''' limits the values from 0 to 255 cutting off which is higher
        or lower
        '''
        limit0 = max(0, n)
        limit255 = min(255, limit0)
        return limit255

    def getcs(self):
        ''' gets the color string needed for the PhotoImage in tkinter in
        formtat #FFAA00
        '''
        s = "#"
        s += tohex(self.limit(self.r))
        s += tohex(self.limit(self.g))
        s += tohex(self.limit(self.b))
        return s

    def get_limited(self):
        '''limits the rgb values form 0 to 255'''
        r = self.limit(self.r)
        g = self.limit(self.g)
        b = self.limit(self.b)
        return (r, g, b)