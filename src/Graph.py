# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 07:56:37 2019

@author: Mauro
"""

from tkinter import Canvas, PhotoImage

PIL_available = True
try:
    import PIL
    import PIL.ImageTk as itk
except ImportError:
    PIL_available = False
    
import Color

#==============================================================================
# Graph
#==============================================================================

class Graph:
    ''' This class manages the drawing of the function. The function is
    converted in a PhotoImage object and then populated with various
    colors.
    '''

    def __init__(self, rootf, width, height):
        
        self.rootf = rootf

        self.width = width
        self.height = height

        # create a canvas with a green background
        bgcolor = Color.Color(0, 255, 125)
        self.canvas = Canvas(rootf, width = width, height= height,
                             bg= bgcolor.getcs(), bd = 0,
                             relief="ridge", highlightthickness=0)

        # append the photoimage to the root so it doesn't get
        # garbage colloected
        self.rootf.image = PhotoImage(width=width, height=height)
        self.image = rootf.image
        
        self.ob_ids = []

    def draw(self):
        ''' draws the image on the canvas'''
        dims = (self.width/2, self.height/2)
        self.canvas.create_image(dims, image=self.image)

    def update_image(self, matrix):
        ''' fills the PhotoImage with the color values
        color values have to be in the format '#FFAA00'
        '''
        if PIL_available:
            img = PIL.Image.new( 'RGB', (self.width, self.height), "black")
            pixmap = img.load()
            
            for j in range(self.height):
                for i in range(self.width):
                    color = matrix.get(i, j)
                    pixmap[i, j] = (color.r, color.g, color.b)
            
            self.rootf.image = itk.PhotoImage(image=img)
            self.image = self.rootf.image
        else:
            data = ""
            for j in range(matrix.height):
                data += "{"
                for i in range(matrix.width):
                
                    color = matrix.get(i, j)
                    data += color.getcs() + " "
                data = data [0: len(data) - 1]
                
                data += "} "
            
            data = data [0: len(data) - 1]
                
            self.image.put(data, to=(0, 0, self.width, self.height))
    
    def update_image_pil(self, pil_image):
        self.rootf.image = itk.PhotoImage(image=pil_image)
        self.image = self.rootf.image

    def draw_rectangle(self, coords, color):
        if self.ob_ids:
            for item_id in self.ob_ids:
                self.canvas.delete(item_id)
            self.ob_ids = []
        
        item_id = self.canvas.create_rectangle(coords[0], coords[1],
                                               coords[2], coords[3],
                                               outline=color.getcs(), fill="")
        self.ob_ids.append(item_id)
