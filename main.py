__version__ = '1.9.0'
'''
Created on 2 May 2015

@author: David Tober, Jamie Smeets, Stephen Philp
'''
import kivy
import math
import copy
import time
import os
import xml.etree.cElementTree as ET
from math import sqrt
kivy.require('1.0.8')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, Rectangle, Ellipse, Line, Triangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.effects.scroll import ScrollEffect
from kivy.core.text.markup import MarkupLabel
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from plyer import email

class Tape(Widget):
    def __init__(self):
        self.head = 0
        self.tapelist = ["_"]
        
    def __len__(self):
        return len(self.tapelist)
    
    def __iter__(self):
        return iter(self.tapelist)
    
    def extend_left(self):
        self.tapelist = ["_"] + self.tapelist
        
    def extend_right(self):
        self.tapelist.append("_")
        
    def move(self, direction):
        if direction == "R":
            self.head += 1
            if self.head > len(self.tapelist):
                self.extend_right()
        elif direction == "L":
            self.head -= 1
            if self.head < 0:
                self.extend_left()
                self.head = 0
    
    def read(self):
        if self.head < len(self.tapelist) and self.head>=0:
            return self.tapelist[self.head]
        elif self.head<0:
            self.extend_left()
            return '_'
        else:
            self.extend_right()
            return '_'
    
    def write(self, newchar, pos=""):
        if pos == "":
            pos = self.head
        self.tapelist[pos] = newchar
        TuringMachineApp.build_tape(app)#re-layout the tape
    
    def sethead(self, newhead):
        self.head = newhead
    

alphabet = ['0', '1' , 'X', '_']
mode = 1
tape = Tape()
scroll_tape = ScrollView(size_hint=(None, None), height = 60, do_scroll_y=False, effect_x= ScrollEffect(), width=Window.width)
root=FloatLayout(width = Window.width, height = Window.height, size_hint =(None, None))
buttons = []
state_name = 0
turing_machine = None
action_list = []
run_speed = '1x'
class TuringMachineApp(App):
    
    def build(self):
        global root
        global turing_machine
        global app 
        app = self
        turing_machine = TuringCanvas(size_hint = (None, 1))
        #main_scroll = ScrollView(pos=(110, 60), size_hint=(None, None), height = Window.height-110, width = Window.width-110)
        #main_scroll.add_widget(turing_machine)
        s = ScrollView(pos=(0,60),size_hint=(None, None), height= Window.height-110, width= 110)
        layout = GridLayout(cols=1, padding=5, spacing=10, size_hint=(None, None), width=110, pos=(0,0))
        layout.bind(minimum_height=layout.setter('height'))
        turing_machine.top_bar = TopBar()
        for child in turing_machine.top_bar.children[:]:
            child.pos=(0, Window.height-50)
            child.width=Window.width
        
        root.add_widget(turing_machine.top_bar)
        def clear_selection(self):
            if turing_machine.selected_state is not None:
                turing_machine.selected_state.deselect()
                turing_machine.selected_state = None;
                turing_machine.redraw()
        
        btn1 = ToggleButton(size=(100, 100), id='add_states', size_hint=(None, None), group='mode', text='Add states')
        btn1.bind(on_press = clear_selection)
       
        layout.add_widget(btn1)
        btn2 = ToggleButton(size=(100, 100), id='add_transitions', size_hint=(None, None), group='mode', text= 'Add Transition')
        btn2.bind(on_press = clear_selection)
        layout.add_widget(btn2)
        btn3 = ToggleButton(size=(100, 100), size_hint=(None, None), id='final_states', group='mode', text='Select final\n states')
        btn3.bind(on_press = clear_selection)
        
        layout.add_widget(btn3)
        btn4 = ToggleButton(size=(100, 100), size_hint=(None, None),id='start_states', group='mode', text= 'Select start\nstates')
        btn4.bind(on_press = clear_selection)
        layout.add_widget(btn4)
        btn5 = ToggleButton(size=(100, 100), size_hint=(None, None), id='delete', group='mode', text= 'Delete')
        btn5.bind(on_press = clear_selection)
        layout.add_widget(btn5)
        s.add_widget(layout)
        root.add_widget(turing_machine)
        root.add_widget(s)
        
        def execute(self):
            turing_machine.run_turing()
        
        #root.add_widget(run_btn)
        TuringMachineApp.build_tape(self)
        global tape
        tape.head = 0
        root.add_widget(scroll_tape)
        
        return root

    #This function builds and redraws the tape on the screen
    def build_tape(self):
        cell_width = (Window.width)/11
        tape_cells=GridLayout(rows=1, padding=(5,5), spacing = 10, size_hint=(None, None), height=60)
        scroll_tape.clear_widgets(children = None)
        def edit_cell(self):
            p=InputPopup(pos_hint={'top': 0.3})
            global tape
            tape.sethead(self.list_pos)
            #TuringMachineApp.build_tape(app)#re-layout the tape
            p.initialize(self)
            p.bind(on_dismiss=app.build_tape())
            p.open()
        
        def add_cell_right(self):
            global tape
            tape.extend_right()
            TuringMachineApp.build_tape(app)#re-layout the tape
            
        def add_cell_left(self):
            global tape
            tape.extend_left()
            TuringMachineApp.build_tape(app)#re-layout the tape
        
        add_left_btn = Button(text='+')
        add_left_btn.bind(on_press = add_cell_left)
        tape_cells.add_widget(add_left_btn)
        if len(tape)<Window.width/cell_width:
            tape_cells.width=Window.width
            for i in range(int(math.floor(Window.width/cell_width))-len(tape)):
                tape.extend_right()
        else:
            tape_cells.width = len(tape)*(cell_width+10)
        count=0
        for i in tape:
            cell = Button(text=i)#Initialize all cells to tape value
            if count == tape.head:
                cell.background_color= [1,1,0,1]#Make head of tape visually distinct
            cell.bind(on_press = edit_cell)
            cell.list_pos = count
            count=count+1
            tape_cells.add_widget(cell)
        
        add_right_btn = Button(text='+')
        add_right_btn.bind(on_press = add_cell_right)
        tape_cells.add_widget(add_right_btn)
        scroll_tape.add_widget(tape_cells)
          
class Action():
    def __init__(self, instruction, widget, cascaded_effects):
        self.instruction = instruction;
        self.widget = widget
        self.cascaded_effects = cascaded_effects
        
class InputPopup(Popup):
    def initialize(self, trigger):
        root = self
        layout = ScrollView(size_hint=(None, None), height = 50, width=215, do_scroll_y=False, effect_x= ScrollEffect())
        grid = GridLayout(rows=1, size_hint=(None, None), height=50, width=len(alphabet)*60, padding =(5,5), spacing =10)
        def make_selection(self):
            global tape
            trigger.text = self.text
            global tape
            tape.write(self.text, tape.head)
            root.dismiss()
            
        for letter in alphabet:
            btn = Button(text=letter, width=40)
            btn.bind(on_press = make_selection)
            grid.add_widget(btn)
        layout.add_widget(grid)
        self.content = layout
        
        
class Cell(Widget):
    pass

class TuringCanvas(FloatLayout):
    def __init__(self, **kwargs):
        super(TuringCanvas, self).__init__(**kwargs)
        self.state_list = []
        #The following are used to implement stepping backwards during execution
        self.step_list = []
        self.visited_states = []
        #The bound objects are used to improve dragging responsiveness 
        self.bound_state = None
        self.bound_transition = None
        self.selected_state = None
        self.selected_transition = None
        self.redraw()
        
    def on_touch_down(self, touch):
        if touch.y>(Window.height-50):
            return
        selection = False
        items = ToggleButton.get_widgets('mode')
        for btn in items:
            if btn.state=='down':
                selection = True
                side_button = btn
                break
                
        del(items)
        if selection:
            if(side_button.id == 'add_states'):
                self.add_state(touch)
            elif(side_button.id == 'add_transitions'):
                self.add_transition(touch)
            elif(side_button.id == 'final_states'):
                self.select_final_state(touch)
            elif(side_button.id == 'start_states'):
                self.select_start_state(touch)
            elif(side_button.id == 'delete'):
                self.delete(touch)
        else:
            self.select_only(touch)
        self.redraw()
    
    def select_only(self, touch):
        collision = False
        for s in self.state_list:
            if s.collision(touch):
                collision = True
                if(self.selected_state is not None):
                    self.selected_state.deselect()
                s.select()
                self.selected_state = s
                break
        if not collision:
            trans = self.transition_collision(touch)
            self.bound_transition = trans
            if self.selected_state is not None:
                self.selected_state.deselect()
                self.selected_state = None
        
    def add_state(self, touch):
        global action_list
        collision = False
        for s in self.state_list:
            if s.collision(touch):
                collision = True
                if(self.selected_state is not None):
                    self.selected_state.deselect()
                s.select()
                self.selected_state = s
                break
        if not collision:
            if(self.selected_state is not None):
                self.selected_state.deselect()
                self.selected_state = None
            if(len(self.state_list) == 0):
                new_state = State(center=(touch.x, touch.y), size=(50,50), color=Color(1,0,0))   
            else:
                new_state = State(center=(touch.x, touch.y), size=(50,50), color=Color(0,1,0))    
            self.state_list.append(new_state)
            action_list.append(Action('add', new_state, None))
            
    def add_transition(self, touch):
        collision = False
        for s in self.state_list:
            if s.collision(touch):
                collision = True
                if(self.selected_state is not None):
                    
                    trans = Transition(self.selected_state, s)
                    action_list.append(Action('add', trans, None))
                    self.selected_state.deselect()
                    self.selected_state = None
                else:
                    s.select()
                    self.selected_state = s
                break
        if(self.selected_state is not None and collision == False):
            self.selected_state.deselect()
            self.selected_state = None
            
    def select_final_state(self, touch):
        collision = False
        for s in self.state_list:
            if s.collision(touch):
                if s.is_final():
                    action_list.append(Action('final',s, None))
                    s.set_not_final()
                else:
                    action_list.append(Action('final', s, None))
                    s.set_final()
                break
    
    def select_start_state(self, touch):
        collision = False
        for i in range(len(self.state_list)):
            if self.state_list[i].collision(touch):
                if(self.selected_state is not None):
                    if(self.selected_state is self.state_list[i]):
                        tempState = self.state_list[0]
                        tempState.changeColor(Color(0,1,0))
                        tempState.draw(self.canvas)
                        self.selected_state.changeColor(Color(1,0,0))
                        self.state_list[0] = self.selected_state
                        self.state_list[i] = tempState
                        tempState.deselect()
                        self.selected_state.deselect()
                        self.selected_state = None
                    else:
                        self.selected_state.deselect()
                        self.selected_state = None
                    break
                       
                else:
                    self.state_list[i].select()
                    self.selected_state = self.state_list[i]
                break
    
    def delete(self, touch):
        for state in self.state_list:
            if state.collision(touch):
                self.state_list.remove(state)
                action = self.delete_inbound_transitions(state)
                action_list.append(action)
                break
            for trans in state.transition_list:
                if trans.collision(touch):
                    action_list.append(Action('del', trans, None))
                    state.transition_list.remove(trans)
                    break
        self.redraw()
      
    def delete_inbound_transitions(self, deleted_state):
        cas = []
        for s in self.state_list:
            for trans in s.transition_list:
                if trans.end is deleted_state:
                    s.transition_list.remove(trans)
                    cas.append(trans)
        return Action('del', deleted_state, cas)
    def on_touch_move(self, touch):
        if self.bound_state is not None:
            self.bound_state.set_center(touch.pos)
        elif self.bound_transition is not None:
            self.bound_transition.set_bend(touch)
        else:
            trans = self.transition_collision(touch)
            if self.selected_state is not None and self.selected_state.collision(touch):
                self.selected_state.set_center(touch.pos)
                self.bound_state = self.selected_state
            elif trans is not None:
                trans.set_bend(touch)
                self.bound_transition = trans
        self.redraw()

    def on_touch_up(self, touch):
        self.bound_state=None
        self.bound_transition=None

    # Clear canvas and call draw on all states.
    def redraw(self):
        self.canvas.clear()
        global buttons
        for b in buttons:
            root.remove_widget(b)
        buttons=[]
        for s in self.state_list:
            s.draw_transitions(self.canvas)
        for s in self.state_list:
            s.draw(self.canvas)
        
            
    def transition_collision(self, touch):
        for state in self.state_list:
            trans = state.transition_collision(touch)
            if trans is not None:
                return trans        
        return None
                  

class State(object):
    def __init__(self, **kwargs):
        self.transition_list = []
        self.final = False
        global state_name
        self.name = str(state_name)#Use default state name
        state_name = state_name+1#Increment default state name
        if "center" in kwargs:
           self.center = kwargs['center']
        else:
            raise(Exception("Center must be defined when State is instantiated:\nE.g. center=(0,0)"))

        if "color" in kwargs:
            self.color = kwargs['color']
            self.standard_color = self.color
        else:
            raise(Exception("Color must be defined when State is instantiated:\nE.g. color=Color(1,1,1)"))

        if "size" in kwargs:
            self.size = kwargs['size']
        else:
            raise(Exception("Size must be defined when State is instantiated:\nE.g. size=(50, 50)"))
        
    def transition_collision(self, touch):
        for trans in self.transition_list:
            if trans.collision(touch):
                return trans
    # Is the touch within the ellipse
    def collision(self, touch):
        r = ((self.center[0] - touch.x)/(self.size[0]/2))**2 + ((self.center[1] - touch.y)/(self.size[1]/2))**2

        if r <= 1:
            return True

        return False

    # Change colour of selected state
    def select(self):
        self.color = Color(0, 0, 1)

    # Change colour back
    def deselect(self):
        self.color = self.standard_color

    # Set the central location of the node.
    def set_center(self, center):
        if len(center) != 2:
            raise AttributeError("State position can only take tuple of size 2")
        self.center = center

    def get_center(self):
        return self.center

    def changeColor(self, inColor):
        self.standard_color = inColor
        
    def is_final(self):
        return self.final
    
    def set_final(self):
        self.final = True
        
    def set_not_final(self):
        self.final = False
        
    def get_transition(self, read):
        for t in self.transition_list:
            if read == t.read():
                write = t.write()
                direction = t.move()
                next = t.next()
                return (write, direction, next, t)
        return False
    
    # Draw each transition between states.
    def draw(self, canvas):
        canvas.add(self.color)
        canvas.add(Ellipse(size=self.size, pos=(self.center[0] - self.size[0]/2, self.center[1] - self.size[1]/2)))
        if self.final:
            canvas.add(Color(1,1,0))
            canvas.add(Ellipse(size=(6*self.size[0]/7, 6*self.size[1]/7), pos=(self.center[0] - 6*(self.size[0]/2)/7, self.center[1] - 6*(self.size[1]/2)/7)))
            canvas.add(self.color)
            canvas.add(Ellipse(size=(5*self.size[0]/7, 5*self.size[1]/7), pos=(self.center[0] - 5*(self.size[0]/2)/7, self.center[1] - 5*(self.size[1]/2)/7)))
    
    def draw_transitions(self, canvas):
        for trans in self.transition_list:
            trans.draw(canvas)

# Connect states with transition
class Transition(object):
    def __init__(self, start, end):
        start.transition_list.append(self)
        self.start = start
        self.end = end
        self.color = Color(1,1,1)
        if start is end:
            self.bend_point = [(self.start.get_center()[0]+self.end.get_center()[0])/2, (self.start.get_center()[1]+self.end.get_center()[1])/2+200]
        else:
            dist = sqrt(math.pow(-start.get_center()[1]+end.get_center()[1], 2)+math.pow(start.get_center()[0]-end.get_center()[0],2))
            normal = ((start.get_center()[1]-end.get_center()[1])/dist, (-start.get_center()[0]+end.get_center()[0])/dist)
            self.bend_point = [(start.get_center()[0]+end.get_center()[0])/2+100*normal[0], (start.get_center()[1]+end.get_center()[1])/2+100*normal[1]]
        self.read_char = '_'
        self.write_char = '_'
        self.direction = '_'
    
    def change_color(self, new_color):
        self.color = new_color
    
    def collision(self, touch):
        if(self.start is self.end):
            dist = sqrt(math.pow(self.bend_point[0]-self.start.get_center()[0],2)+math.pow(self.bend_point[1]-self.start.get_center()[1],2))
            if dist == 0:
                dist =1
            line = [self.bend_point[0]-self.start.get_center()[0], self.bend_point[1]-self.start.get_center()[1]]
            normal_x = (line[1])/dist
            normal_y = (-line[0])/dist
            start_x = self.start.get_center()[0]+20*(normal_x)
            end_x = self.start.get_center()[0]-20*(normal_x)
            start_y = self.start.get_center()[1]+20*(normal_y)
            end_y = self.start.get_center()[1]-20*(normal_y)
            t_x=0.3
            t_y=0.3
        else:
            start_x = self.start.get_center()[0]
            start_y = self.start.get_center()[1]
            end_x = self.end.get_center()[0]
            end_y = self.end.get_center()[1]
            t_x = 0.5
            t_y = 0.5
        B_x = pow(1-t_x, 2)*start_x+2*(1-t_x)*t_x*self.bend_point[0]+pow(t_x,2)*end_x#calculate point on bezier
        B_y = pow(1-t_y, 2)*start_y+2*(1-t_y)*t_y*self.bend_point[1]+pow(t_y,2)*end_y#calculate point on bezier
        
        
        if abs(touch.x-B_x)<=15 and  abs(touch.y-B_y)<=15:
            return True
        return False
     
    def set_bend(self, touch):
        if self.start is self.end:
            t_x = 0.3
            t_y = 0.3
            dist = sqrt(math.pow(self.bend_point[0]-self.start.get_center()[0],2)+math.pow(self.bend_point[1]-self.start.get_center()[1],2))
            if dist == 0:
                dist =1
            line = [self.bend_point[0]-self.start.get_center()[0], self.bend_point[1]-self.start.get_center()[1]]
            normal_x = (line[1])/dist
            normal_y = (-line[0])/dist
            start_x = self.start.get_center()[0]+20*(normal_x)
            end_x = self.start.get_center()[0]-20*(normal_x)
            start_y = self.start.get_center()[1]+20*(normal_y)
            end_y = self.start.get_center()[1]-20*(normal_y)
        else:
            t_x = 0.5
            t_y = 0.5
            start_x = self.start.get_center()[0]
            start_y = self.start.get_center()[1]
            end_x = self.end.get_center()[0]
            end_y = self.end.get_center()[1]
        B_x = touch.x
        B_y = touch.y
        self.bend_point[0] = (B_x/(2*(1-t_x)*t_x)) - ((pow(1-t_x, 2)*start_x+pow(t_x,2)*end_x)/(2*(1-t_x)*t_x))
        self.bend_point[1] = (B_y/(2*(1-t_y)*t_y)) - ((pow(1-t_y, 2)*start_y+pow(t_y,2)*end_y)/(2*(1-t_y)*t_y))
    
    def read(self):
        return self.read_char
    
    def write(self):
        return self.write_char
    
    def move(self):
        return self.direction
    
    def next(self):
        return self.end
    
    def draw(self, canvas):
        canvas.add(self.color)
        if(self.start is self.end):
            dist = sqrt(math.pow(self.bend_point[0]-self.start.get_center()[0],2)+math.pow(self.bend_point[1]-self.start.get_center()[1],2))
            if dist == 0:
                dist =1
            line = [self.bend_point[0]-self.start.get_center()[0], self.bend_point[1]-self.start.get_center()[1]]
            normal_x = (line[1])/dist
            normal_y = (-line[0])/dist
            start_x = self.start.get_center()[0]+20*(normal_x)
            end_x = self.start.get_center()[0]-20*(normal_x)
            start_y = self.start.get_center()[1]+20*(normal_y)
            end_y = self.start.get_center()[1]-20*(normal_y)
            t_x=0.3
            t_y=0.3
            B_x = pow(1-t_x, 2)*start_x+2*(1-t_x)*t_x*self.bend_point[0]+pow(t_x,2)*end_x#calculate point on bezier
            B_y = pow(1-t_y, 2)*start_y+2*(1-t_y)*t_y*self.bend_point[1]+pow(t_y,2)*end_y#calculate point on bezier
            triangle = Triangle()
            triangle_base_x = B_x-10*(line[0]/dist)#Ten Pixels below the center of the states
            triangle_base_y = B_y-10*(line[1]/dist)#Ten Pixels below the center of the states
            triangle.points = [B_x, B_y, triangle_base_x+10*(normal_x), triangle_base_y+10*normal_y, triangle_base_x-10*normal_x, triangle_base_y-10*normal_y]
        else:
            start_x = self.start.get_center()[0]
            start_y = self.start.get_center()[1]
            end_x = self.end.get_center()[0]
            end_y = self.end.get_center()[1]
            t_x = 0.5
            t_y = 0.5
            halfway_x = (self.start.get_center()[0]+self.end.get_center()[0])/2
            halfway_y = (self.start.get_center()[1]+self.end.get_center()[1])/2
        
        
            triangle = Triangle()
            dist = sqrt(math.pow(end_x-start_x,2)+math.pow(end_y-start_y,2))
            if dist == 0:
                dist = 1
        
            B_x = pow(1-t_x, 2)*start_x+2*(1-t_x)*t_x*self.bend_point[0]+pow(t_x,2)*end_x#calculate point on bezier
            B_y = pow(1-t_y, 2)*start_y+2*(1-t_y)*t_y*self.bend_point[1]+pow(t_y,2)*end_y#calculate point on bezier
        
            triangle_base_x = B_x-10*((end_x-start_x)/dist)#Ten Pixels below the center of the states
            triangle_base_y = B_y-10*((end_y-start_y)/dist)#Ten Pixels below the center of the states
        
            normal_x = -((end_y-start_y)/dist)
            normal_y = ((end_x - start_x)/dist)
            triangle.points=[B_x, B_y, triangle_base_x+10*normal_x, triangle_base_y+10*normal_y,triangle_base_x-10*normal_x, triangle_base_y-10*normal_y]
        
        canvas.add(Line(bezier=(start_x, start_y, self.bend_point[0], self.bend_point[1], end_x, end_y)))
        canvas.add(triangle)
        self.add_buttons(self, B_x, B_y)

    #Adds buttons to the transition between states
    def add_buttons(self, transition, B_x, B_y):
        btn1 = Button(pos=(B_x, B_y+10), size=(30,30), text=self.read_char)
        btn2 = Button(pos=(B_x+35, B_y+10), size=(30,30), text =self.write_char)
        btn3 = Button(pos=(B_x+70, B_y+10), size=(30,30), text=self.direction)
        
        def edit_read(self):
            p=ReadPopup(pos=(B_x, B_y))
            p.initialize(self, transition)
            p.open()
        def edit_write(self):
            p=WritePopup(pos=(B_x, B_y))
            p.initialize(self, transition)
            p.open()
        def edit_direction(self):
            p=DirectionPopup(pos=(B_x, B_y))
            p.initialize(self, transition)
            p.open()
            
        btn1.bind(on_press = edit_read)
        btn2.bind(on_press = edit_write)
        btn3.bind(on_press = edit_direction)
        buttons.extend([btn1, btn2, btn3])
        root.add_widget(btn1)
        root.add_widget(btn2)
        root.add_widget(btn3)

#This class contains all the actions performed by the top bar
class TopBar(Widget):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    
    def dismiss_popup(self):
        self._popup.dismiss()
    
    def email(self):
        tree = self.getXML()
        tree.write('temp.xml')
        f=open('temp.xml', 'r')
        t = 'Copy the text below into a file and save it. Then open the saved file with Turing Machine Simulator.\n\n'
        email.send(recipient='',
                   subject='Check out this Turing machine I made',
                   text = t+f.read(),
                   create_chooser=True)
    
    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        savedTree = ET.parse(os.path.join(path, filename[0]))
        root = savedTree.getroot()
        global turing_machine
        turing_machine.state_list=[]#Clear previous open Turing Machine
        global tape
        tape_el=root.find('tape')
        tape=Tape()
        tape.tapelist=list(tape_el.text)
        tape.head = int(tape_el.get('head'))
        TuringMachineApp.build_tape(app)
        global alphabet
        alphabet = list(root.find('alphabet').text)
        
        for s in root.find('states'):
            newState = State(center = (float(s.get('center_x')), float(s.get('center_y'))), color=Color(0,1,0), size =(50,50))
            newState.name = s.get('name')
            if s.get('name') == '0':
                newState.changeColor(Color(1,0,0))
                newState.deselect()
            newState.final = s.get('final')=='True'
            turing_machine.state_list.append(newState)
            
        #add transitions now this can only be done once all the states are added
        i=0
        for state in root.find('states'):
            for trans in state.find('transitions'):
                end = trans.get('end')
                for s in turing_machine.state_list:
                    if(s.name == end):
                        end_state = s
                        break
                newTrans = Transition(turing_machine.state_list[i], end_state)
                newTrans.read_char = trans.get('read')
                newTrans.write_char = trans.get('write')
                newTrans.direction = trans.get('direction')
                newTrans.bend_point = [float(trans.get('bend_x')), float(trans.get('bend_y'))]
            i=i+1
        turing_machine.redraw()
        self.dismiss_popup()

    def save(self, path, filename):
        #with open(os.path.join(path, filename), 'w') as stream:
        #    stream.write(self.text_input.text)
        file_path = path+'/'+filename+'.xml'
        tree = self.getXML()
        tree.write(file_path)
        self.dismiss_popup()
    
    def getXML(self):
        global turing_machine
        global tape
        root = ET.Element('TuringMachine')
        ET.SubElement(root, "tape", head = str(tape.head)).text = ''.join(tape)
        ET.SubElement(root, "alphabet").text = ''.join(alphabet)
        s = ET.SubElement(root, "states")
        for state in turing_machine.state_list:
            current = ET.SubElement(s, "state", center_x=str(state.center[0]), name=str(state.name), center_y=str(state.center[1]), final=str(state.final))
            t = ET.SubElement(current, "transitions")
            for trans in state.transition_list:
                ET.SubElement(t, "transition", bend_x=str(trans.bend_point[0]), bend_y=str(trans.bend_point[1]), read=trans.read_char,
                              write=trans.write_char, direction=trans.direction, end=trans.end.name)
        return ET.ElementTree(root)
    
    def undo(self):
        if(turing_machine.selected_state is not None):
            turing_machine.selected_state.deselect()
            turing_machine.selected_state = None
        if len(action_list)!=0:
            prev_action = action_list.pop()
            inst = prev_action.instruction
            widg = prev_action.widget
            if inst == 'add':
                if type(widg) == State:
                    turing_machine.state_list.remove(widg)
                else: #Assumes transition
                    widg.start.transition_list.remove(widg)
            elif inst == 'del':
                if type(widg) == State:
                    turing_machine.state_list.append(widg)
                    for trans in prev_action.cascaded_effects:
                        trans.start.transition_list.append(trans)
                else:
                    widg.start.transition_list.append(widg)
            elif inst == 'final':
                if widg.is_final():
                    widg.set_not_final()
                else:
                    widg.set_final()
            turing_machine.redraw()
            
    def enter_alphabet(self):
        global alphabet
        p = AlphabetPopup()
        layout = GridLayout(rows=1, padding=5, spacing=10, size_hint=(1, 1))
        textbox = TextInput(text=''.join(alphabet))
        layout.add_widget(textbox)
        btn = Button(text = 'OK')
        def OK(self):
            global alphabet
            alphabet = list(textbox.text)
            p.dismiss()
            
        btn.bind(on_press = OK)
        layout.add_widget(btn)
        p.content = layout
        p.open()
    
    def step_back(self):
        if len(turing_machine.step_list)>0:
            trans = turing_machine.step_list.pop()
            if trans.direction == 'R':
                tape.sethead(tape.head - 1)
            elif trans.direction == 'L':
                tape.sethead(tape.head + 1)
            tape.write(trans.read())#reset character on tape
            if turing_machine.selected_state is not None:
                turing_machine.selected_state.deselect()
            turing_machine.selected_state = turing_machine.visited_states.pop()
            turing_machine.selected_state.select()
            turing_machine.redraw()
    
    def edit_run_speed(self):
        p = RunSpeedPopup()
        speeds = ['step', '1x', '2x']
        global run_speed
        def on_checkbox_active(checkbox, value):
            global run_speed
            run_speed = checkbox.id
        layout = GridLayout(rows=1, padding=5, spacing=10, size_hint=(1, 1))
        
        for s in speeds:
            checkbox = CheckBox(label = s, group='speed', id=s)
            if s == run_speed:
                checkbox.active=True
            checkbox.bind(active=on_checkbox_active)
            layout.add_widget(checkbox)
            layout.add_widget(Label(text=s))
        p.content = layout
        p.open()
    
    def stop(self):
        Clock.unschedule(turing_machine.top_bar.run_turing)
       
    def run_turing(self, *positional):
        global tape
        global run_speed
        Halt = False
        global turing_machine
       
        popup = Popup(title = "Simulation Incomplete", title_color=(1,1,1,1), size_hint = (0.3, 0.3))
        if len(turing_machine.state_list) == 0:
            popup.content = Label(text = "[color=#ffffff]The Turing machine\nhas no states[/color]", markup = True)
            popup.open()
        else:
            if turing_machine.selected_state is None:
                turing_machine.selected_state = turing_machine.state_list[0]#initialize to start state if required
            turing_machine.selected_state.select()
            turing_machine.redraw()
            if not Halt:
                step = self.single_step(tape, turing_machine.selected_state)
                if step is not False:
                    turing_machine.visited_states.append(turing_machine.selected_state)
                    if len(turing_machine.visited_states)>5:
                        turing_machine.visited_states = turing_machine.visited_states[1:]
                    turing_machine.selected_state.deselect()
                    (tape, turing_machine.selected_state, trans) = step
                    turing_machine.selected_state.select()
                    if turing_machine.selected_transition is not None:
                        turing_machine.selected_transition.change_color(Color(1,1,1))
                    turing_machine.selected_transition = trans
                    turing_machine.step_list.append(trans)
                    if len(turing_machine.step_list)>5:
                        turing_machine.step_list = turing_machine.step_list[1:]
                    print turing_machine.step_list
                    trans.change_color(Color(1,1,0))
                    app.build_tape()
                    turing_machine.redraw()
                    if run_speed == '1x':
                        Clock.schedule_once(turing_machine.top_bar.run_turing, 1)
                    elif run_speed == '2x':
                        Clock.schedule_once(turing_machine.top_bar.run_turing, 0.5)
                    #else speed is set to step and no recall needs to be set
                        
                else:
                    Halt = True
            if Halt:
                if turing_machine.selected_transition is not None:
                    turing_machine.selected_transition.change_color(Color(1,1,1))
                    turing_machine.redraw()
                popup = Popup(title = "Simulation Complete", title_color=(1, 1, 1, 1), size_hint = (0.3, 0.3))
                if turing_machine.selected_state.is_final():
                    popup.content = Label(text = "[color=#ffffff]Simulation Complete\nwith answer Yes[/color]", markup = True)
                else:
                    popup.content = Label(text = "[color=#ffffff]Simulation Complete\nwith answer No[/color]", markup = True)
                popup.open()
          
            
    def single_step(self, tape, current):
        trans = current.get_transition(tape.read())
        if trans is not False:
            (write, direction, next, t) = trans
            tape.write(write)
            tape.move(direction)
            return (tape, next, t)
        else:
            return False

class ReadPopup(Popup):
    def initialize(self, trigger, transition):
        root = self
        layout = ScrollView(size_hint=(None, None), height = 50, width=215, do_scroll_y=False, effect_x= ScrollEffect())
        grid = GridLayout(rows=1, size_hint=(None, None), height=50, width=len(alphabet)*60, padding =(5,5), spacing =10)
        def make_selection(self):
            trigger.text = self.text
            transition.read_char = self.text
            root.dismiss()
        
        for letter in alphabet:
            btn = Button(text=letter, width=40)
            btn.bind(on_press = make_selection)
            grid.add_widget(btn)
        layout.add_widget(grid)
        self.content = layout

class WritePopup(Popup):
    def initialize(self, trigger, transition):
        root = self
        layout = ScrollView(size_hint=(None, None), height = 50, width=215, do_scroll_y=False, effect_x= ScrollEffect())
        grid = GridLayout(rows=1, size_hint=(None, None), height=50, width=len(alphabet)*60, padding =(5,5), spacing =10)
        def make_selection(self):
            trigger.text = self.text
            transition.write_char = self.text
            root.dismiss()
        
        for letter in alphabet:
            btn = Button(text=letter, width=40)
            btn.bind(on_press = make_selection)
            grid.add_widget(btn)
        layout.add_widget(grid)
        self.content = layout

class DirectionPopup(Popup):
    def initialize(self, trigger, transition):
        root = self
        layout = GridLayout(rows=1, size_hint=(None, None), height=50, width=180, padding =(5,5), spacing =10)
      
        def make_selection(self):
            trigger.text = self.text
            transition.direction = self.text
            root.dismiss()
        
        directions = ['L', 'R', '_']
        for d in directions:
            btn = Button(text=d, width=40)
            btn.bind(on_press = make_selection)
            layout.add_widget(btn)
        
        self.content = layout


# Basic start state.
class StartState(State):
    def __init__(self, **kwargs):
        super(StartState, self).__init__(center=(25, 25), size=(50,50), color=Color(1,0,0))


class Canvas(Widget):
    pass

#The following code was taken from the kivy website at http://kivy.org/docs/api-kivy.uix.filechooser.html
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class AlphabetPopup(Popup):
    pass

class RunSpeedPopup(Popup):
    pass

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
if __name__ == '__main__':
    TuringMachineApp().run();
