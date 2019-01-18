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

from tkinter import (Tk, Canvas, PhotoImage, mainloop, LabelFrame, Frame, Entry,
                     Label, Button, END, filedialog, DISABLED, Checkbutton,
                     IntVar, Listbox)

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
        
    def bind(self, button, function):
        self.entry.bind(button, function)

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

    def bind(self, name, button, function):
        self.data_boxes[name].bind(button, function)
        
    
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
        self.inputs = DataBoxes(self.frame) 
        
        self.inputs.place_entry("width", str(0), 0, 0)
        self.inputs.bind(
                "width",
                "<Return>",
                lambda e : 
                    self.update_rectangle(e, "width"))
        
        self.inputs.place_entry("height", str(0), 0, 1) 
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
        
        self.mandel_coords_x = Mandelbrot.Linspace(xmin, xmax, self.graph.width)
        self.mandel_coords_y = Mandelbrot.Linspace(ymin, ymax, self.graph.height)
        
        self.graph_coords_x = Mandelbrot.RLinspace(xmin, xmax, self.graph.width)
        self.graph_coords_y = Mandelbrot.RLinspace(ymin, ymax, self.graph.height)
        
    
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
        
        
#        half_w = self.inputs.get("width", "float") / 2 
#        half_h = self.inputs.get("height", "float") / 2
#        
#        x1 = x_clicked - half_w
#        y1 = y_clicked - half_h
#        x2 = x_clicked + half_w
#        y2 = y_clicked + half_h
#        
#        x1 = int(self.graph_coords_x.get(x1))
#        x2 = int(self.graph_coords_x.get(x2))
#        y1 = int(self.graph_coords_y.get(y1))
#        y2 = int(self.graph_coords_y.get(y2))      
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
        
        self.frame_n = LabelEntry(self.frame, "frame number", 0)
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
        
        v_xmin = Mandelbrot.Linspace(bd_start.linx.minv, bd_end.linx.minv, n_frames)
        v_xmax = Mandelbrot.Linspace(bd_start.linx.maxv, bd_end.linx.maxv, n_frames)
        v_ymin = Mandelbrot.Linspace(bd_start.liny.minv, bd_end.liny.minv, n_frames)
        v_ymax = Mandelbrot.Linspace(bd_start.liny.maxv, bd_end.liny.maxv, n_frames)    
        
        v_it = Mandelbrot.Linspace(frame_start.iteration,frame_end.iteration, n_frames)    
        
        w_start = bd_start.linx.maxv - bd_start.linx.minv
        w_end = bd_end.linx.maxv - bd_end.linx.minv
        w_ratio = w_end / w_start

        h_start = bd_start.liny.maxv - bd_start.liny.minv
        h_end = bd_end.liny.maxv - bd_end.liny.minv
        h_ratio = h_end / h_start

        for n in range(n_frames + 1):
            if n != 0:
                k_w = 1/pow(w_ratio, 1/ n)
                k_h = 1/pow(h_ratio, 1/ n) 
            else:
                k_w, k_h = 1, 1
                
            
            
            minx = v_xmin.get(n) * k_w
            maxx = v_xmax.get(n) * k_w
            miny = v_ymin.get(n) * k_h
            maxy = v_ymax.get(n) * k_h
            
            print("w:", maxx - minx)
            
            bounds = Mandelbrot.Boundaries(
                        bd_start.get_width(), 
                        bd_start.get_height(),
                        minx, maxx, miny, maxy)
            
            it = int(v_it.get(n))
            
            mandelbrot = Mandelbrot.Mandelbrot(
                            bounds, it,
                            frame_start.mode,
                            frame_start.colormap)
            
            mandelbrot.save_image(self.folder + "test_image_" + str(n) + ".png")
            
        
        
        
# add on click display picture
# add frame insertion control
# add linearize and render functions
       
        

#==============================================================================
# Main program
#==============================================================================

WIDTH, HEIGHT = 640, 480

def main():
    
    root = Tk()
    root.title("Mandelbrot generator")


    graph_frame = LabelFrame(root, text="Graph area")
    graph = Graph(graph_frame, WIDTH, HEIGHT)
    graph.canvas.grid(row = 0, column = 0, rowspan = 2)
    

    cp = ControlPanel(graph_frame, graph)
    cp.frame.grid(row = 0, column = 1)

    graph_frame.grid(row = 0, column = 0)
    
    zoom = Zoom(graph_frame, graph, cp)
    zoom.frame.grid(row = 1, column = 1)
    
    ani = Animation(root, cp, graph)
    ani.frame.grid(row = 0, column = 1)

    mainloop()    


if __name__ == "__main__":
    main()

