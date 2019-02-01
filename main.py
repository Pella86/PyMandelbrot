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
                     Listbox, StringVar, Label, Frame, messagebox)
import PIL

import Mandelbrot
import Graph
import InputEntry
import ControlPanel



#==============================================================================
# Animation manager        
#==============================================================================

# Parameters and image corresponding to one frame
class AniFrame:
    
    def __init__(self, bd, iteration, colormap, mode, frame_n, image_name):
        self.boundaries = bd
        self.iteration = iteration
        self.colormap = colormap
        self.mode = mode
        self.frame_n = frame_n
        self.image_name = image_name

# askdir
class AskDir:

    def __init__(self, rootf, title, def_dir):
        self.frame = Frame(rootf)
        
        # the name of the entry box
        label = Label(self.frame, text=title)
        label.grid(row=0, column=0)
        
        # the path pointed to
        self.folder_complete = def_dir
        self.folder_var = StringVar()
        self.set(self.folder_complete)
        
        label_folder = Label(self.frame, textvariable=self.folder_var)
        label_folder.grid(row=1, column=0)
        
        # ask dir button
        ask_dir_name_button = Button(self.frame, text="Browse dir", command=self.askdir)
        ask_dir_name_button.grid(row=0, column=1, rowspan=2)
        
    
    def askdir(self):
        dir_pick = filedialog.askdirectory(initialdir=self.folder_var.get())
        print("dir:", dir_pick)
        if dir_pick:
            self.set(dir_pick)
    
    def set(self, folder_str):
        self.folder_complete = folder_str
        charmax = 25

        if len(folder_str) > charmax:
            folder_str = folder_str[::-1]
            folder_str = folder_str[0: charmax]
            folder_str = "..." + folder_str[::-1]
        self.folder_var.set(folder_str)

    def get(self):
        return self.folder_complete

class Animation:

    def __init__(self, rootf, control_panel, graph, zoom):
        self.frame = LabelFrame(rootf, text = "Animation")
        
        self.control_panel = control_panel
        self.graph = graph
        self.zoom = zoom
        
        # holds the frame serie
        self.frames = {}

        # default folder
        def_folder = "./tests/animation/"
        if not os.path.isdir(def_folder):
            os.mkdir(def_folder)     
        
        # folder
        self.ani_dir = AskDir(self.frame, "Animation folder", def_folder)
        self.ani_dir.frame.grid(row = 0, column = 0, columnspan = 2)

        # buttons to save the frame
        bsave_key_frame = Button(self.frame, text = "save key frame",
                                 command = self.save_frame)
        bsave_key_frame.grid(row = 1, column = 0)

        bload = Button(self.frame, text = "load frame",
                       command = lambda : self.load_aniframe())
        bload.grid(row = 1, column = 1)
        
        self.frame_n = InputEntry.InputEntryInteger(self.frame,
                                                    "frame number", 0, "{:d}")        
        
        self.frame_n.frame.grid(row = 2, column = 0, columnspan = 2)
        
        binter_render = Button(self.frame, text="interpolate and render", command = self.render_interpolation)
        binter_render.grid(row = 3, column = 0, columnspan = 2)
        
        self.timeline = Listbox(self.frame)
        self.timeline.bind("<Double-Button-1>", lambda e : self.item_select(e))
        self.timeline.grid(row = 0, column = 2, rowspan = 4)

        self.image_name_base = "ani_frame_image_"

    def save_aniframe(self, frame_name):
        name = "ani_frame_" + str(self.frames[frame_name].frame_n) + ".mlf"
        filename = os.path.join(self.ani_dir.get(), name)
        with open(filename, "wb") as f:
            pickle.dump(self.frames[frame_name], f)
        
    def load_aniframe(self):
        filename = filedialog.askopenfilename(initialdir = self.ani_dir.get(), title="select a frame", filetypes=(("mandelbrot frame", "*.mlf"), ("all files", "*.*")))

        if filename:
            with open(filename, "rb") as f:
                frame = pickle.load(f)
                self.add_frame(frame)
        
    def add_frame(self, aniframe):
        """ the frame is added to the list in order by frame number,
        if the frame has the same frame number as one existing, the existing
        one will be overwritten
        """
        
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
        if self.control_panel.mandelbrot is None:
            messagebox.showinfo("Animation", "no mandelbrot found")
            return
     
        # boundaries, iterations, colormap
        # frame_n, image_name
        bd = self.control_panel.mandelbrot.boundaries
        iteration = self.control_panel.mandelbrot.max_iteration
        colormap = self.control_panel.mandelbrot.color_function.colormap_name
        mode = self.control_panel.mandelbrot.mode
        frame_n = int(self.frame_n.entry.get())
        name = self.image_name_base + str(frame_n) + ".png"
        image_name = os.path.join(self.ani_dir.get(), name)
           
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
        print("rendring animation...")
        names = self.timeline.get(0, END)
        
        if len(names) < 2:
            messagebox.showinfo("Animation", "Too few frames")
        else:
            frame_pairs = []
            prev_name = names[0]
            for name in names[1:]:
                frame_pairs.append((prev_name, name))
                prev_name = name
            
            for name_pair in frame_pairs:
                self.render_inter_frame(name_pair[0], name_pair[1])
    
    def calc_proportions(self, start_vmin, start_vmax, end_vmin, end_vmax, n_frames):

        start_center = (start_vmax + start_vmin) / 2
        end_center = (end_vmax + end_vmin) / 2
        
        start_dist = start_vmax - start_vmin
        end_dist = end_vmax - end_vmin
        ratio = start_dist/ end_dist
        zoom_factor = pow(ratio, 1 / n_frames)        
        
        
        return start_center, end_center, start_dist, end_dist, zoom_factor
        
    
    def render_inter_frame(self, start_frame_name, end_frame_name):
        # get the frames
        frame_start = self.frames[start_frame_name]
        frame_end = self.frames[end_frame_name]
        
        # calculate how many frames btween start and end
        n_frames = frame_end.frame_n - frame_start.frame_n 
        
        # select the boundaries
        bd_start = frame_start.boundaries
        bd_end = frame_end.boundaries
        
        # calculate x coordinates
        start_xmin = bd_start.linx.minv
        start_xmax = bd_start.linx.maxv
        
        end_xmin = bd_end.linx.minv
        end_xmax = bd_end.linx.maxv
        
        start_xcenter, end_xcenter, start_width, end_width, x_zoom_factor = self.calc_proportions(start_xmin, start_xmax, end_xmin, end_xmax, n_frames)

        # calculate y coordinates
        start_ymin = bd_start.liny.minv
        start_ymax = bd_start.liny.maxv
        
        end_ymin = bd_end.liny.minv
        end_ymax = bd_end.liny.maxv

        start_ycenter, end_ycenter, start_height, end_height, y_zoom_factor = self.calc_proportions(start_ymin, start_ymax, end_ymin, end_ymax, n_frames) 
        
        # calculate iterations linear spacing
        v_it = Mandelbrot.Linspace(frame_start.iteration, frame_end.iteration, n_frames)
        
        # calculate the serie
        cd = start_width
        cdy = start_height
        for frame in range(n_frames):
            # calculate the width, then center, then adjust the center 
            # for witdth
            cd /= x_zoom_factor
            c = (cd - start_width) / (end_width - start_width)
            ccx = end_xcenter * c + start_xcenter * (1 - c)
            xmin = ccx - cd / 2
            xmax = ccx + cd / 2
            
            # for height
            cdy /= y_zoom_factor
            cy = (cdy - start_height) / (end_height - start_height)
            ccy = end_ycenter * cy + start_ycenter * (1 - cy)
            ymin = ccy - cdy / 2
            ymax = ccy + cdy / 2 

            # prepare the mandelbrot boundaries
            bounds = Mandelbrot.Boundaries(
                        bd_start.get_width(), 
                        bd_start.get_height(),
                        xmin, xmax, ymin, ymax)
            
            # get the iterations (could increase non linearly)
            it = int(v_it.get(frame))
            
            # generate the mandelbrot
            mandelbrot = Mandelbrot.Mandelbrot(
                            bounds, it,
                            frame_start.mode,
                            frame_start.colormap)
            
            # save the image
            actual_frame = frame + frame_start.frame_n
            print(f"frame {actual_frame} rendered.")
            name = "test_image_" + str(actual_frame) + ".png"
            filename = os.path.join(self.ani_dir.get(), name)
            mandelbrot.save_image(filename)

# add frame name
# add image frame name
# move stuff when a new directory is selected
#  insert a overwrite warning
# colormap and mode mixer
# rotations?
# bilinear interpolation
# bumpmap and potential map
# link C program to python program
# manage screen size and images bigger of screen size
# 


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

    graph = Graph.Graph(root, WIDTH, HEIGHT)
    graph.canvas.grid(row = 0, column = 0, rowspan = 3)
    

    cp = ControlPanel.ControlPanel(root, graph)
    cp.frame.grid(row = 0, column = 1)

    zoom = ControlPanel.Zoom(root, graph, cp)
    zoom.frame.grid(row = 1, column = 1)
    
    ani = Animation(root, cp, graph, zoom)
    ani.frame.grid(row = 2, column = 1)

    mainloop()    


if __name__ == "__main__":
    main()

