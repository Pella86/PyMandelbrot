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
import pickle

from tkinter import (Tk, mainloop, LabelFrame, Frame, Entry, Label, Button,
                     END, filedialog, DISABLED, Checkbutton, IntVar, Listbox)
                     

PIL_available = True
try:
    import PIL
except ImportError:
    PIL_available = False

import Color
import Mandelbrot
import Graph
import InputEntry

#==============================================================================
# utilies
#==============================================================================

def get_pathname(path):
    ''' Little function to split the path in path, name, extension'''
    path, nameext = os.path.split(path)
    name, ext = os.path.splitext(nameext)
    return path, name, ext


#==============================================================================
# Mandelbrot parameters
#==============================================================================

class ControlPanel:
    ''' class controlling the input data for the mandelbrot function'''

    def __init__(self, rootf, graph):
        self.frame = LabelFrame(rootf, text="Control panel")

        self.mandelbrot = None
        
        self.data_boxes = InputEntry.DataBoxes(self.frame)

        # parameters entries placement
        self.data_boxes.place_entry("x min",         -2.0,  "float", 0, 0)
        self.data_boxes.place_entry("x max",          1.0,  "float", 0, 1)
        self.data_boxes.place_entry("y min",         -1.25, "float", 1, 0)
        self.data_boxes.place_entry("y max",          1.25, "float", 1, 1)
        self.data_boxes.place_entry("max iterations", 25,   "int",   2, 0, 2)
        self.data_boxes.place_entry("mode",    "iteration", "str",   3, 0, 2)
        self.data_boxes.place_entry("colormap",      "hot", "str",   4, 0, 2)

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
        minx = self.data_boxes.get("x min")
        maxx = self.data_boxes.get("x max")
        miny = self.data_boxes.get("y min")
        maxy = self.data_boxes.get("y max")
        it   = self.data_boxes.get("max iterations")
        
        # this user inputs are strings so they will always be in a valid
        # format.
        # yet they are keys into dictonaries, so if the key is missng
        # the error handling is inside the next body
        mode = self.data_boxes.get("mode")
        colormap = self.data_boxes.get("colormap")

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
    ''' the class manages the zooming in function and relative red square on
    the graph
    '''
    
    def __init__(self, rootf, graph, control_panel):
        
        # keep a reference of the graph area and control paknel
        self.graph = graph
        self.graph.canvas.bind("<Button-1>", lambda e : self.clicked(e))
        
        self.control_panel = control_panel
        
        # create the frame for the buttons
        self.frame = LabelFrame(rootf, text="Zoom options")
        
        # create the input boxes
        self.inputs = InputEntry.DataBoxes(self.frame) 
        
        self.inputs.place_entry("width", 0.0, "float", 0, 0)
        self.inputs.bind(
                "width",
                "<Return>",
                lambda e : 
                    self.update_rectangle(e, "width"))
        
        self.inputs.place_entry("height", 0.0, "float", 0, 1) 
        self.inputs.bind(
                "height",
                "<Return>", 
                lambda e : 
                    self.update_rectangle(e, "height"))
        
        self.mandel_coords_x = None
        self.mandel_coords_y = None
        self.graph_coords_x = None
        self.graph_coords_y = None
        
        self.ratio = None
        
        self.calc_proportions()          
        
        self.inputs.place_entry("center_x", 0.0, "float", 1, 0)
        self.inputs.place_entry("center_y", 0.0, "float", 1, 1)
        
        self.center = (0, 0)
        
        bzoom_render = Button(self.frame, text="zoom and render", command= self.zoom_render)
        bzoom_render.grid(row = 2, column = 0, columnspan = 2)
        
        self.maintain_proportion = IntVar(value=1)
        
        check_prop = Checkbutton(self.frame, text = "maintain proportions", variable=self.maintain_proportion)
        check_prop.grid(row=3)
        
        

    def calc_proportions(self): 
        xmin = self.control_panel.data_boxes.get("x min")
        xmax = self.control_panel.data_boxes.get("x max")        
        ymin = self.control_panel.data_boxes.get("y min")
        ymax = self.control_panel.data_boxes.get("y max") 
        print(xmin, xmax, ymin, ymax)
        
        width = (xmax - xmin) / 10
        height = (ymax - ymin) / 10
        
        self.ratio = width / height
        
        self.inputs.set("width", width)
        self.inputs.set("height", height)
        
        self.mandel_coords_x = Mandelbrot.Linspace(xmin, xmax, self.graph.width)
        self.mandel_coords_y = Mandelbrot.Linspace(ymin, ymax, self.graph.height)
        
        self.graph_coords_x = Mandelbrot.RLinspace(xmin, xmax, self.graph.width)
        self.graph_coords_y = Mandelbrot.RLinspace(ymin, ymax, self.graph.height)
        
    
    def update_rectangle(self, e, name):
        print(e, name)
        
        if self.maintain_proportion.get() == 1:
            if name == "width":
                width = self.inputs.get_enter("width")
                self.inputs.set("width", width)
                self.inputs.set("height", width / self.ratio)
            if name == "height":
                height = self.inputs.get_enter("height")
                self.inputs.set("height", height)
                self.inputs.set("width", height * self.ratio)
        
        
        self.draw_rectangle()
    
    def draw_rectangle(self):

        half_w = self.inputs.get("width") / 2 
        half_h = self.inputs.get("height") / 2
        
        x_clicked = self.center[0]
        y_clicked = self.center[1]        
        
        x1 = x_clicked - half_w
        y1 = y_clicked - half_h
        x2 = x_clicked + half_w
        y2 = y_clicked + half_h
        
        x1 = int(self.graph_coords_x.get(x1))
        x2 = int(self.graph_coords_x.get(x2))
        y1 = int(self.graph_coords_y.get(y1))
        y2 = int(self.graph_coords_y.get(y2)) 
        
        
        self.graph.draw_rectangle((x1, y1, x2, y2), Color.Color(255, 0, 0))


          
    def clicked(self, event):
        
        x_mandel = self.mandel_coords_x.get(event.x)
        y_mandel = self.mandel_coords_y.get(event.y)
        
        self.center = (x_mandel, y_mandel)
        
        self.inputs.set("center_x", x_mandel)
        self.inputs.set("center_y", y_mandel)  
        
        self.draw_rectangle()
    
    def zoom_render(self):
        # set the values using the center and width from the boxes
        # start the render
        self.inputs.reset()
        
        x = self.inputs.get("center_x")
        y = self.inputs.get("center_y")
        
        w = self.inputs.get("width") 
        h = self.inputs.get("height")
        
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
# Animation manager        
#==============================================================================



class AniFrame:
    
    def __init__(self, bd, iteration, colormap, mode, frame_n, image_name):
        self.boundaries = bd
        self.iteration = iteration
        self.colormap = colormap
        self.mode = mode
        self.frame_n = frame_n
        self.image_name = image_name
        

class Animation:

    def __init__(self, rootf, control_panel, graph):
        self.frame = LabelFrame(rootf, text = "Animation")
        
        self.control_panel = control_panel
        self.graph = graph
        
        self.frames = {}
        
        
        bsave_key_frame = Button(self.frame, text = "save key frame", command = self.save_frame)
        bsave_key_frame.grid(row = 0, column = 0)
        
        bload = Button(self.frame, text = "load frame", command = lambda : self.load_aniframe())
        bload.grid(row = 0, column = 1)
        
        self.frame_n = InputEntry.InputEntryInteger(self.frame, "frame number", 0, "{:d}")
        self.frame_n.frame.grid(row = 1, column = 0, columnspan = 2)
        
        binter_render = Button(self.frame, text="interpolate and render", command = self.render_interpolation)
        binter_render.grid(row = 2, column = 0, columnspan = 2)
        
        self.timeline = Listbox(self.frame)
        self.timeline.bind("<Double-Button-1>", lambda e : self.item_select(e))
        self.timeline.grid(row = 0, column = 2, rowspan = 3)
        
        self.folder = "./tests/animation/"
        self.image_name_base = "ani_frame_image_"
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder)
     
    def save_aniframe(self, frame_name):
        filename = self.folder + "ani_frame_" + str(self.frames[frame_name].frame_n) + ".mlf"
        with open(filename, "wb") as f:
            pickle.dump(self.frames[frame_name], f)
        
    def load_aniframe(self):
        filename = filedialog.askopenfilename(initialdir = self.folder, title="select a frame", filetypes=(("mandelbrot frame", "*.mlf"), ("all files", "*.*")))
        print(filename)
        
        if filename:
            with open(filename, "rb") as f:
                frame = pickle.load(f)
                self.add_frame(frame)
        
    def add_frame(self, aniframe):
        positions = self.timeline.get(0, END)
        
        frame_n = aniframe.frame_n
        
        inserted = False
        
        for i, position in enumerate(positions):
            
            if self.frames[position].frame_n == frame_n:
                self.frames[position] = aniframe
                inserted = True
                break
            
            elif self.frames[position].frame_n > frame_n:
                self.add_element(frame_n, aniframe, i)
                inserted = True
                break
        
        if not inserted:
            self.add_element(frame_n, aniframe)
        

    def save_frame(self):
        # read all the control panel data and store them in self.frames
        
        # boundaries, iterations, colormap
        # frame_n, image_name
        bd = self.control_panel.mandelbrot.boundaries
        iteration = self.control_panel.mandelbrot.max_iteration
        colormap = self.control_panel.mandelbrot.color_function.colormap_name
        mode = self.control_panel.mandelbrot.mode
        frame_n = int(self.frame_n.entry.get())
        image_name = self.folder + self.image_name_base + str(frame_n) + ".png"
       
        # save the image
        self.control_panel.mandelbrot.save_image(image_name)
        aniframe = AniFrame(bd, iteration, colormap, mode, frame_n, image_name)

        self.add_frame(aniframe)
        
        self.save_aniframe(self.get_frame_name(aniframe))
        
    def get_frame_name(self, aniframe):
        return  "frame_" + str(aniframe.frame_n)

    def add_element(self, frame_n, aniframe, index = END):
        frame_name = self.get_frame_name(aniframe)
        self.frames[frame_name] = aniframe 
        self.timeline.insert(index, frame_name)    
        
    
    def item_select(self, event):
        # retrive the selected item 
        item = self.timeline.curselection()
        names = self.timeline.get(0, END)

        frame_name = names[int(item[0])]
        frame = self.frames[frame_name]
        if os.path.isfile(frame.image_name):
            # add imread option
            img = PIL.Image.open(frame.image_name)
            self.graph.update_image_pil(img)
            self.graph.draw() 
    
    def render_interpolation(self):
        names = self.timeline.get(0, 1)
        
        frame_start_name = names[0]
        frame_end_name = names[1]
        
        frame_start = self.frames[frame_start_name]
        frame_end = self.frames[frame_end_name]
        
        n_frames = frame_end.frame_n - frame_start.frame_n 
        
        bd_start = frame_start.boundaries
        bd_end = frame_end.boundaries

        smx = bd_start.linx.minv
        sMx = bd_start.linx.maxv
        
        emx = bd_end.linx.minv
        eMx = bd_end.linx.maxv

        scx = (sMx + smx) / 2
        ecx = (eMx + emx) / 2
        
        sd = sMx - smx
        ed = eMx - emx
        f = sd / ed
        z = pow(f, 1 / n_frames)

        print("initial x")
        print( ("{:.2f} "*4).format(smx, sMx, sMx - smx, sd / (sMx - smx)))
        print( ("{:.2f} "*4).format(emx, eMx, eMx - emx, sd / (eMx - emx)))        

 

        smy = bd_start.liny.minv
        sMy = bd_start.liny.maxv
        
        emy = bd_end.liny.minv
        eMy = bd_end.liny.maxv

        scy = (sMy + smy) / 2
        ecy = (eMy + emy) / 2
        
        sdy = sMy - smy
        edy = eMy - emy
        fy = sdy / edy
        zy = pow(fy, 1 / n_frames)

        print("initial y")
        print( ("{:.2f} "*4).format(smy, sMy, sMy - smy, sdy / (sMy - smy)))
        print( ("{:.2f} "*4).format(emy, eMy, eMy - emy, sdy / (eMy - emy)))  
        
        v_it = Mandelbrot.Linspace(frame_start.iteration, frame_end.iteration, n_frames)
        
        cd = sd
        cdy = sdy
        for frame in range(n_frames):
            print("---")
            cd /= z
            c = (cd - sd) / (ed - sd)
            ccx = ecx * c + scx * (1 - c)
            xmin = ccx - cd / 2
            xmax = ccx + cd / 2
            
            print( ("{:.2f} "*4).format(xmin, xmax, xmax - xmin, sd / (xmax - xmin)))
            
            cdy /= zy
            cy = (cdy - sdy) / (edy - sdy)
            ccy = ecy * cy + scy * (1 - cy)
            ymin = ccy - cdy / 2
            ymax = ccy + cdy / 2 

            print( ("{:.2f} "*4).format(ymin, ymax, ymax - ymin, sdy / (ymax - ymin)))   
            
            bounds = Mandelbrot.Boundaries(
                        bd_start.get_width(), 
                        bd_start.get_height(),
                        xmin, xmax, ymin, ymax)
            
            it = int(v_it.get(frame))
            
            mandelbrot = Mandelbrot.Mandelbrot(
                            bounds, it,
                            frame_start.mode,
                            frame_start.colormap)
            
            mandelbrot.save_image(self.folder + "test_image_" + str(frame) + ".png")


        
# add on click display picture
# add frame insertion control
# add linearize and render functions
       
        

#==============================================================================
# Main program
#==============================================================================

WIDTH, HEIGHT = 640, 480

def load_frame(animation, filename):
    with open(filename, "rb") as f:
        frame = pickle.load(f)
        animation.add_frame(frame)

def main():
    
    root = Tk()
    root.title("Mandelbrot generator")


    graph_frame = LabelFrame(root, text="Graph area")
    graph = Graph.Graph(graph_frame, WIDTH, HEIGHT)
    graph.canvas.grid(row = 0, column = 0, rowspan = 2)
    

    cp = ControlPanel(graph_frame, graph)
    cp.frame.grid(row = 0, column = 1)

    graph_frame.grid(row = 0, column = 0)
    
    zoom = Zoom(graph_frame, graph, cp)
    zoom.frame.grid(row = 1, column = 1)
    
    ani = Animation(root, cp, graph)
    ani.frame.grid(row = 0, column = 1)
    
    load_frame(ani, "./tests/animation/ani_frame_0.mlf")
    #load_frame(ani, "./tests/animation/ani_frame_50.mlf")

    mainloop()    


if __name__ == "__main__":
    main()

