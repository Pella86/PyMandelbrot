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

import os

from tkinter import (Tk, Canvas, PhotoImage, mainloop, LabelFrame, Frame, Entry,
                     Label, Button, END, filedialog, DISABLED, Checkbutton,
                     IntVar)

PIL_available = True
try:
    import PIL
    import PIL.ImageTk as itk
except ImportError:
    PIL_available = False

import Color
import Mandelbrot

#==============================================================================
# utilies
#==============================================================================

def get_pathname(path):
    ''' Little function to split the path in path, name, extension'''
    path, nameext = os.path.split(path)
    name, ext = os.path.splitext(nameext)
    return path, name, ext

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

    def draw_rectangle(self, coords, color):
        if self.ob_ids:
            for item_id in self.ob_ids:
                self.canvas.delete(item_id)
            self.ob_ids = []
        
        item_id = self.canvas.create_rectangle(coords[0], coords[1],
                                               coords[2], coords[3],
                                               outline=color.getcs(), fill="")
        self.ob_ids.append(item_id)

#==============================================================================
# Mandelbrot parameters
#==============================================================================

class LabelEntry:
    ''' class that constructs an entry text field plus label in front of it
    '''

    def __init__(self, rootf, name, def_value = "0"):
        self.frame = Frame(rootf)

        label = Label(self.frame, text=name)
        label.grid(row = 0, column = 0)

        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1)

        self.entry.insert(END, str(def_value))

    def set_color(self, color):
        self.entry.config({"background": color.getcs()})
        
    def set(self, value):
        self.entry.delete(0, END)
        self.entry.insert(END, str(value))

#==============================================================================
# Series of LabelEntries with input checking
#==============================================================================

class DataBoxes:
    
    def __init__(self, frame):
        self.frame = frame
        self.data_boxes = {}
        
        self.correct_format = True
        self.input_types = {}
        self.input_types["float"] = float
        self.input_types["int"] = int        
        
    
    def place_entry(self, name, def_value, row, col, colspan=1):
        self.data_boxes[name] = LabelEntry(self.frame, name, def_value)
        self.data_boxes[name].frame.grid(row = row,
                                         column = col,
                                         columnspan=colspan)  
    
    def get(self, name, input_type):

        # check if is valid
        try:
            item = self.data_boxes[name].entry.get()
            return self.input_types[input_type](item)
        except ValueError:
            # in case is wrong color the background of the box red
            self.data_boxes[name].set_color(Color.Color(255, 0, 0))

        # in case there is an unchecked exception this will set the format
        # to false so that doesnt trigger the rendering
        if self.correct_format:
            self.correct_format = False

        return None
    
    def get_string(self, name):
        return self.data_boxes[name].entry.get()
    
    def set(self, name, value):
        self.data_boxes[name].set(value)
        
    def reset(self):
        self.correct_format = True
        for key in self.data_boxes:
            self.data_boxes[key].set_color(Color.Color(255, 255, 255))
            
    


class ControlPanel:
    ''' class controlling the input data for the mandelbrot function'''

    def __init__(self, rootf, graph):
        self.frame = LabelFrame(rootf, text="Control panel")

        self.mandelbrot = None
        
        self.data_boxes = DataBoxes(self.frame)

        # parameters entries placement
        self.data_boxes.place_entry("x min", -2.0, 0, 0)
        self.data_boxes.place_entry("x max", 1.0, 0, 1)
        self.data_boxes.place_entry("y min", -1.25, 1, 0)
        self.data_boxes.place_entry("y max", 1.25, 1, 1)
        self.data_boxes.place_entry("max iterations", 25, 2, 0, 2)
        self.data_boxes.place_entry("mode", "iteration", 3, 0, 2)
        self.data_boxes.place_entry("colormap", "hot", 4, 0, 2)

        # place the buttons to render the image
        self.brender = Button(self.frame, text="Render",
                              command = lambda: self.render(graph))
        self.brender.grid(row = 5, column = 0)

        # place the button to save the image
        self.bsave = Button(self.frame, text = "Save image",
                            command = self.save_image)
        self.bsave.grid(row = 5, column = 1)
        if not Mandelbrot.matlib_available:
            self.bsave["state"] = DISABLED

    def render(self, graph):
        ''' this function renders the mandelbrot into the graph, using the
        parameters specified in the data boxes. If the input value is wrong
        the box will turn red
        '''

        self.data_boxes.reset()
        


        # gather the user inputs and check validity
        minx = self.data_boxes.get("x min", "float")
        maxx = self.data_boxes.get("x max", "float")
        miny = self.data_boxes.get("y min", "float")
        maxy = self.data_boxes.get("y max", "float")
        it   = self.data_boxes.get("max iterations", "int")
        
        # this user inputs are strings so they will always be in a valid
        # format.
        # yet they are keys into dictonaries, so if the key is missng
        # the error handling is inside the next body
        mode = self.data_boxes.get_string("mode")
        colormap = self.data_boxes.get_string("colormap")

        # run the render
        if self.data_boxes.correct_format:
            color_matrix = None
            # this will try to render the mandelbrot, if the mode or the
            # colormaps are wrong it will turn the boxes red
            try:
                bounds = Mandelbrot.Boundaries(WIDTH, HEIGHT,
                                               minx, maxx, miny, maxy)
                self.mandelbrot = Mandelbrot.Mandelbrot(bounds, it,
                                                        mode,
                                                        colormap)
                color_matrix = self.mandelbrot.get_color_matrix()
                
            except Mandelbrot.KeyErrorMode:
                self.data_boxes.data_boxes["mode"].set_color(Color.Color(255, 0, 0))

            except Mandelbrot.KeyErrorColormap:
                self.data_boxes.data_boxes["colormap"].set_color(Color.Color(255, 0, 0))
            
            if color_matrix is not None:
                graph.update_image(color_matrix)
                graph.draw()
                print("rendering done")

    def save_image(self):
        # asks for a filename
        path = filedialog.asksaveasfilename(initialdir = "./",
                                            title = "Save image as ...")

        # if the program was run and the path is valid
        if self.mandelbrot is not None and path is not None:
            _, _, ext = get_pathname(path)

            # if extention missing then attach a png to it
            if not ext:
                path += ".png"

            self.mandelbrot.save_image(path)
            
#==============================================================================
# Zoom-in function
#==============================================================================

class Zoom:
    
    def __init__(self, rootf, graph, control_panel):
        self.graph = graph
        self.control_panel = control_panel
        self.graph.canvas.bind("<Button-1>", lambda e : self.clicked(e))
        
        self.frame = LabelFrame(rootf, text="Zoom options")
        
        self.inputs = DataBoxes(self.frame) 

        self.inputs.place_entry("width", str(0), 0, 0)
        self.inputs.data_boxes["width"].entry.bind("<Return>", lambda e : self.update_rectangle(e, "width"))
        
        self.inputs.place_entry("height", str(0), 0, 1) 
        self.inputs.data_boxes["height"].entry.bind("<Return>", lambda e : self.update_rectangle(e, "height"))
        
        self.lsx = None
        self.lsy = None
        self.glsx = None
        self.glsy = None
        
        self.ratio = None
        
        self.calc_proportions()          
        
        self.inputs.place_entry("center_x", str(0), 1, 0)
        self.inputs.place_entry("center_y", str(0), 1, 1)
        
        self.center = (0, 0)
        
        bzoom_render = Button(self.frame, text="zoom and render", command= self.zoom_render)
        bzoom_render.grid(row = 2, column = 0, columnspan = 2)
        
        self.maintain_proportion = IntVar(value=1)
        
        check_prop = Checkbutton(self.frame, text = "maintain proportions", variable=self.maintain_proportion)
        check_prop.grid(row=3)
        
        

    def calc_proportions(self): 
        xmin = self.control_panel.data_boxes.get("x min", "float")
        xmax = self.control_panel.data_boxes.get("x max", "float")        
        ymin = self.control_panel.data_boxes.get("y min", "float")
        ymax = self.control_panel.data_boxes.get("y max", "float") 
        
        width = (xmax - xmin) / 10
        height = (ymax - ymin) / 10
        
        self.ratio = width / height
        
        self.inputs.set("width", width)
        self.inputs.set("height", height)
        
        self.lsx = Mandelbrot.Linspace(xmin, xmax, self.graph.width)
        self.lsy = Mandelbrot.Linspace(ymin, ymax, self.graph.height)
        
        self.glsx = Mandelbrot.RLinspace(xmin, xmax, self.graph.width)
        self.glsy = Mandelbrot.RLinspace(ymin, ymax, self.graph.height)
        
    
    def update_rectangle(self, e, name):
        print(e, name)
        
        if self.maintain_proportion.get() == 1:
            if name == "width":
                width = self.inputs.get("width", "float")
                self.inputs.set("height", width /self.ratio)
            if name == "height":
                height = self.inputs.get("height", "float")
                self.inputs.set("width", height * self.ratio)
        
        
        self.draw_rectangle()
    
    def draw_rectangle(self):

        half_w = self.inputs.get("width", "float") / 2 
        half_h = self.inputs.get("height", "float") / 2
        
        x_clicked = self.center[0]
        y_clicked = self.center[1]        
        
        x1 = x_clicked - half_w
        y1 = y_clicked - half_h
        x2 = x_clicked + half_w
        y2 = y_clicked + half_h
        
        x1 = int(self.glsx.get(x1))
        x2 = int(self.glsx.get(x2))
        y1 = int(self.glsy.get(y1))
        y2 = int(self.glsy.get(y2)) 
        
        
        self.graph.draw_rectangle((x1, y1, x2, y2), Color.Color(255, 0, 0))


          
    def clicked(self, event):
        print(event.x, event.y)
        # get the information from the control panel
        #  add in control panel class 
        # get_xmin, get_xmax, get_ymin, get_ymax
        #xmin = self.control_panel
        #lsx = Mandelbrot.Linespace()
        
        x_clicked = self.lsx.get(event.x)
        y_clicked = self.lsy.get(event.y)
        
        self.center = (x_clicked, y_clicked)
        
        print(x_clicked, y_clicked)
        
        self.inputs.set("center_x", x_clicked)
        self.inputs.set("center_y", y_clicked)  
        
        self.draw_rectangle()
        
        
#        half_w = self.inputs.get("width", "float") / 2 
#        half_h = self.inputs.get("height", "float") / 2
#        
#        x1 = x_clicked - half_w
#        y1 = y_clicked - half_h
#        x2 = x_clicked + half_w
#        y2 = y_clicked + half_h
#        
#        x1 = int(self.glsx.get(x1))
#        x2 = int(self.glsx.get(x2))
#        y1 = int(self.glsy.get(y1))
#        y2 = int(self.glsy.get(y2))      
#        
#        self.graph.draw_rectangle((x1, y1, x2, y2), Color.Color(255, 0, 0))
    
    def zoom_render(self):
        # set the values using the center and width from the boxes
        # start the render
        self.inputs.reset()
        
        x = self.inputs.get("center_x", "float")
        y = self.inputs.get("center_y", "float")
        
        w = self.inputs.get("width", "float") 
        h = self.inputs.get("height", "float")
        
        new_xmin = x - w / 2
        new_xmax = x + w / 2
        new_ymin = y - h / 2
        new_ymax = y + h / 2
        
        if self.inputs.correct_format:
        
            self.control_panel.data_boxes.set("x min", new_xmin)
            self.control_panel.data_boxes.set("x max", new_xmax)
            self.control_panel.data_boxes.set("y min", new_ymin)
            self.control_panel.data_boxes.set("y max", new_ymax)
            
            self.calc_proportions()
            
            self.control_panel.render(self.graph)
        
        
#==============================================================================
# Main program
#==============================================================================

#WIDTH, HEIGHT = 640, 480
WIDTH, HEIGHT = 640, 480
def main():
    
    root = Tk()
    root.title("Mandelbrot generator")


    graph_frame = LabelFrame(root, text="Graph area")
    graph = Graph(graph_frame, WIDTH, HEIGHT)
    graph.canvas.grid(row = 0, column = 0, rowspan = 2)
    

    cp = ControlPanel(graph_frame, graph)
    cp.frame.grid(row = 0, column = 1)

    graph_frame.pack()
    
    zoom = Zoom(graph_frame, graph, cp)
    zoom.frame.grid(row = 1, column = 1)

    mainloop()    


if __name__ == "__main__":
    main()

