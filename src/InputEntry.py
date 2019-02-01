# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 08:02:01 2019

@author: Mauro
"""

from tkinter import Frame, Entry, END, Label

import Color

#==============================================================================
# Labelled input
#==============================================================================

class InputEntry:
    ''' class that constructs an entry text field plus label in front of it
    '''

    def __init__(self, rootf, name, def_value = "0"):
        self.frame = Frame(rootf)

        label = Label(self.frame, text=name)
        label.grid(row = 0, column = 0)

        self.entry = Entry(self.frame, validate = "focusout", validatecommand=self.get_enter)
        self.entry.grid(row = 0, column = 1)
        #self.bind("<Return>", lambda e : self.set(self.entry.get()))
       
        self.set(def_value)

    def set_color(self, color):
        self.entry.config({"background": color.getcs()})
    
    def get(self):
        return self.value
    
    def get_enter(self):
        self.value = self.entry.get()
        return True
        
    def set(self, value):
        self.value = value
        self.entry.delete(0, END)
        self.entry.insert(END, str(value))
        
    def bind(self, button, function):
        self.entry.bind(button, function)
    
    def reset(self):
        self.set_color(Color.Color(255, 255, 255))
     

class InputEntryFloat(InputEntry):
    
    def __init__(self, rootf, name, def_value, fmt):
        self.fmt = fmt
        super().__init__(rootf, name, def_value)
        #self.bind("<Return>", lambda e : self.get_enter())
        
    
    def set(self, value):
        self.value = float(value)
        self.entry.delete(0, END)
        self.entry.insert(END, self.fmt.format(value))
    
    def get_enter(self):
        self.reset()
        try:
            item = self.entry.get()
            self.value = float(item)
            return True
        except ValueError:
            # in case is wrong color the background of the box red
            self.set_color(Color.Color(255, 0, 0))
            self.value = None
            return False
        return False

class InputEntryInteger(InputEntry):
    
    def __init__(self, rootf, name, def_value, fmt):
        self.fmt = fmt
        super().__init__(rootf, name, def_value)
        #self.bind("<Return>", lambda e : self.get_enter())

    def set(self, value):
        self.value = int(value)
        self.entry.delete(0, END)
        self.entry.insert(END, self.fmt.format(self.value))
    
    def get_enter(self):
        self.reset()
        try:
            item = self.entry.get()
            self.value = int(item)
            return True
        except ValueError:
            # in case is wrong color the background of the box red
            self.set_color(Color.Color(255, 0, 0))
            
            self.value = None
            return False
        return False

#==============================================================================
# Series of LabelEntries with input checking
#==============================================================================

class DataBoxes:
    
    def __init__(self, frame):
        self.frame = frame
        self.data_boxes = {}
        
        self.correct_format = True

    def bind(self, name, button, function):
        self.data_boxes[name].bind(button, function)

    def place_entry(self, name, def_value, vtype, row, col, colspan=1):

        if vtype == "float":
            self.data_boxes[name] = InputEntryFloat(self.frame, name, def_value, "{:.4g}")
        elif vtype == "int":
            self.data_boxes[name] = InputEntryInteger(self.frame, name, def_value, "{:d}")
        else:
            self.data_boxes[name] = InputEntry(self.frame, name, def_value)
            
        self.data_boxes[name].frame.grid(row = row,
                                         column = col,
                                         columnspan=colspan)  
    def get(self, name):
        return self.data_boxes[name].get()
    
    def get_enter(self, name):

        # check if is valid
        value = self.data_boxes[name].get_enter()
        
        # in case there is an unchecked exception this will set the format
        # to false so that doesnt trigger the rendering
        if self.correct_format and value is None:
            self.correct_format = False

        return value
    
    def set(self, name, value):
        self.data_boxes[name].set(value)
        
    def reset(self):
        self.correct_format = True
        for key in self.data_boxes:
            self.data_boxes[key].reset()
            
    
