from   vsframe import VSFrame
import tkinter
import tkinter.ttk
import tkinter as tk
from collections import OrderedDict
from bot import Bot

class App:
    # adapted from notebook.py Copyright 2003, Iuri Wickert (iwickert yahoo.com)
    # initialization. receives the master widget
    # reference and the notebook orientation
    def __init__(self, master, side=tk.LEFT):

        self.active_fr = None
        self.count = 0
        self.choice = tk.IntVar(0)
        self.master = master  # Bot

        # allows the TOP and BOTTOM
        # radiobuttons' positioning.
        if side in (tk.TOP, tk.BOTTOM):
            self.side = tk.LEFT

        else:
            self.side = tk.TOP

        # creates notebook's frames structure
        #self.rb_fr = tk.Frame(master, borderwidth=2, relief=tk.RIDGE, bg="black")
        self.rb_fr = VSFrame(master, borderwidth=2, relief=tk.RIDGE, bg="black")
        self.rb_fr.pack(side=side, fill=tk.BOTH)
        #  ----------------------------------------------------------------------------
        self.new_frame = tk.Frame(self.rb_fr, borderwidth=2, relief=tk.RIDGE, bg="black")
        self.new_frame.pack(side=tk.BOTTOM, padx=(10,10))
        self.new_button = tk.Button(self.new_frame, text="New", command=self.make_new, )
        self.new_button.pack()
        #  ----------------------------------------------------------------------------
        self.screen_fr = tk.Frame(master, borderwidth=2, relief=tk.RIDGE, bg="black")
        self.screen_fr.pack(fill=tk.BOTH)
        self.roster = OrderedDict() # Bot

    # return a master frame reference for the external frames (screens)
    def __call__(self):
        return self.screen_fr

    def make_new(self):
        new_bot = Bot(self.master, self.screen_fr, self)
        self.add_screen(new_bot,
                   "null",
                   textvariable=new_bot.title_var,
                   bg="gray75",
                   fg="black",
                   selectcolor="lightblue"
                   )
    # add a new frame (screen) to the (bottom/left of the) notebook
    def add_screen(self, fr, title, **kwargs):

        b = tk.Radiobutton(self.rb_fr.interior, 
            text=title, 
            indicatoron=0,
            variable=self.choice, 
            value=self.count,
            command=lambda: self.display(fr), 
            borderwidth=4, 
            **kwargs)
           
        b.pack(fill=tk.BOTH, side=self.side, pady=(13,0), padx=(6,6))

        # ensures the first frame will be
        # the first selected/enabled
        if not self.active_fr:
            fr.is_active = True  # Bot
            fr.pack(fill=tk.BOTH, expand=1)
            self.active_fr = fr

        self.count += 1

        self.roster[fr] = b   # Bot

        # returns a reference to the newly created
        # radiobutton (allowing its configuration/destruction)
        return b


    def kill_screen(self, fr):   # Bot \/\/\/
        ''' TODO Function Description
        '''
        victim = self.roster.pop(fr)
        victim.destroy()
        for f, b in self.roster.items():
            self.display(f)
            break


    # hides the former active frame and shows
    # another one, keeping its reference
    def display(self, fr):
        ''' TODO Function Description
        '''
        try:
            self.roster[self.active_fr].config(fg="black")
        except:
            pass
        self.active_fr.is_active = False  # Bot
        self.active_fr.forget()
        fr.pack(fill=tk.BOTH, expand=1)
        fr.is_active = True  # Bot
        self.active_fr = fr
        try:
            self.active_fr.graph.draw_graph()
        except:
            pass
        self.roster[self.active_fr].config(fg="black")


    def update_frames(self):
        ''' TODO Function Description
        '''
        for bot, button in self.roster.items():
            try:
                bot.update()
                try:
                    if bot.graph.performance.get() == "inf":
                        button.config(fg="green")
                    elif float(bot.graph.performance.get()) > 0:
                        button.config(fg="green")
                    elif float(bot.graph.performance.get()) < 0:
                        button.config(fg="red")
                    else:
                        button.config(fg="black")
                except Exception as e:
                    print(str(e))
                    button.config(fg="orange")
            except Exception as e:
                button.config(bg="red")
                button.config(fg="black")
                print(str(e)) # TODO: email user
                raise # todo  delete me
        self.master.after(10000, self.update_frames)