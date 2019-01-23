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

from tkinter import (Tk, mainloop, LabelFrame, Button, END, filedialog,
                     Listbox)
                     

PIL_available = True
try:
    import PIL
except ImportError:
    PIL_available = False

import Mandelbrot
import Graph
import InputEntry
import ControlPanel



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

    def __init__(self, rootf, control_panel, graph, zoom):
        self.frame = LabelFrame(rootf, text = "Animation")
        
        self.control_panel = control_panel
        self.graph = graph
        self.zoom = zoom
        
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
        
        # load the data
        self.control_panel.data_boxes.set("x min", frame.boundaries.linx.minv)
        self.control_panel.data_boxes.set("x max", frame.boundaries.linx.maxv)
        self.control_panel.data_boxes.set("y min", frame.boundaries.liny.minv)
        self.control_panel.data_boxes.set("y max", frame.boundaries.liny.maxv)
        self.control_panel.data_boxes.set("max iterations", frame.iteration)
        self.control_panel.data_boxes.set("mode", frame.mode)
        self.control_panel.data_boxes.set("colormap", frame.colormap) 
        
        self.frame_n.set(frame.frame_n)
        
        # load the image
        if os.path.isfile(frame.image_name):
            # add imread option
            img = PIL.Image.open(frame.image_name)
            self.graph.update_image_pil(img)
            self.graph.draw() 
        
        # adjust the zoom values
        self.zoom.calc_proportions()
    
    
    
    def render_interpolation(self):
        names = self.timeline.get(0, END)
        
        frame_pairs = []
        prev_name = names[0]
        for name in names[1:]:
            frame_pairs.append((prev_name, name))
            prev_name = name
        
        print(frame_pairs)
        
        for name_pair in frame_pairs:
            self.render_inter_frame(name_pair[0], name_pair[1])
        
    
    def render_inter_frame(self, start_frame_name, end_frame_name):

        frame_start = self.frames[start_frame_name]
        frame_end = self.frames[end_frame_name]
        
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
            
            print(f"--- {frame + frame_start.frame_n} ---")
            cd /= z
            c = (cd - sd) / (ed - sd)
            ccx = ecx * c + scx * (1 - c)
            xmin = ccx - cd / 2
            xmax = ccx + cd / 2
            
            print( ("{:.2f} "*4).format(xmin, xmax, xmax - xmin, sd / (xmax - xmin)))
            
            cdy /= zy
            if edy - sdy == 0:
                cy = 1
            else:
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
            
            actual_frame = frame + frame_start.frame_n
            mandelbrot.save_image(self.folder + "test_image_" + str(actual_frame) + ".png")


        
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
    

    cp = ControlPanel.ControlPanel(graph_frame, graph)
    cp.frame.grid(row = 0, column = 1)

    graph_frame.grid(row = 0, column = 0)
    
    zoom = ControlPanel.Zoom(graph_frame, graph, cp)
    zoom.frame.grid(row = 1, column = 1)
    
    ani = Animation(root, cp, graph, zoom)
    ani.frame.grid(row = 0, column = 1)

    mainloop()    


if __name__ == "__main__":
    main()

