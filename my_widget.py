import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import tkinter
import tkinter.ttk
from tkinter import ttk
import tkinter as tk


class MyWidget(ttk.Frame):

    def __init__(self,
        app, 
        parent,
        handle,
        choices = None,
        subs = {}, 
        is_password = False,
        startVal = None,
        allowEntry = False,
        static = False,
        cipadx = 0,
        optional = False,
        activeStart = 1,
        ewidth = 8,
        cwidth = None,
        cmd = None,
        *args,
        **kwargs
    ):
        ttk.Frame.__init__(self, parent,style = "app.TFrame", *args, **kwargs)
        self.app = app
        self.parent = parent
        self.handle = handle
        self.choices = choices
        self.optional = optional
        self.allowEntry = allowEntry
        self.startVal = startVal
        self.cmd = cmd
        self.subs = subs
        self.sub = None

        # if background and not self.app.light:
        #     self.bg = tk.PhotoImage(file = background)
        #     self.bglabel = tk.Label(self, image=self.bg)
        #     self.bglabel.place(x=0, y=0, relwidth=1, relheight=1)

        if self.optional:
            self.optState = tk.IntVar()
            self.optBut = ttk.Checkbutton(self,
                variable = self.optState,
                onvalue = 1,
                offvalue = 0,
                command = self._grey,
                style = "app.TCheckbutton"
            )
            self.optBut.pack(side="left")

        if isinstance(self.choices, list):
            if not allowEntry:
                state = "readonly"

            else:
                state = "enabled"

            if not cwidth: cwidth = len(max(self.choices,key=len))

            self.value = ttk.Combobox(self,
                values = self.choices,
                state = state,
                width = cwidth,postcommand = self.wideMenu,
                style = "app.TCombobox"
            )
            self.value.bind('<<ComboboxSelected>>',self.findSubs)
            #self.value.bind('<Configure>', self.wideMenu)

        if self.choices == "entry":
            state = "enabled" if not static else "readonly"

            if not is_password:
                self.value = ttk.Entry(self,width=ewidth,style = "app.TEntry",state = state)

            else:
                self.value = ttk.Entry(self, 
                    width = ewidth, 
                    style = "app.TEntry", 
                    state = state, 
                    show = "*"
                )
            self._root().after(0,self.findSubs,None,False)

        self.title = ttk.Label(self, text = self.handle,style = "app.TLabel")
        self.title.pack(anchor = tk.W)

        if self.choices:
            self.value.pack(anchor = tk.E,ipadx = cipadx)

            if not self.startVal is None:

                if not self.choices == "entry":
                    self.value.set(self.startVal)
                    self._root().after(0,self.findSubs,None,False)

                else:
                    self.value.insert(0,startVal)
                    self._root().after(0,self.findSubs,None,False)

        if self.optional:
            if activeStart:
                self.optState.set(1)


    def wideMenu(self,event = None):
        ''' TODO Function Description
        '''
        try:
            global mystyle
            
            if self.handle in ["Account"]:
                #print("got Account wideMenu")
                mystyle.configure("TCombobox",postoffset = (0,0,150,0))
                self.value.config(style = "TCombobox")

            elif self.handle in ["Subaddress Book"]:
                mystyle.configure("TCombobox",postoffset = (0,0,100,0))
                self.value.config(style = "TCombobox")

            else:
                mystyle.configure("TCombobox",postoffset = (0,0,0,0))

        except Exception as e:
            print(str(e))


    def get(self):
        ''' TODO Function Description
        '''
        #print(self.handle,self.sub,bool(self.sub))
        if self.choices:
            if self.sub:
                val = [self.value.get()]

                try:
                    val.extend(self.sub.get())

                except TypeError:
                    print(self.handle,self.sub,bool(self.sub))

                return val
            return [self.value.get()]

        elif self.optional:
            if self.optState.get():
                if self.sub:
                    val = [self.value.get()]

                    try:
                        val.extend(self.sub.get())

                    except TypeError:
                        print(self.handle,self.sub,bool(self.sub))

                    return val
                    
                return [self.handle]

            else:
                return None

        else:
            print("tried to get:%s" %self.handle)
            return #[self.value.get()]


    def findSubs(self, event = None, not_init = True):
        ''' TODO Function Description
        '''
        if self.sub:
            self.sub.destroy()
            self.sub = None

        if self.subs:
            if self.value.get() in self.subs and not self.choices == "entry":
                self.sub = MyWidget(self.app,self,**self.subs[self.value.get()])
                self.sub.pack(anchor = tk.E,pady=3)

            elif self.choices == "entry":
                self.sub = MyWidget(self.app,self,**self.subs["entry"])
                self.sub.pack(anchor = tk.E,pady=3)

            else:
                pass

        if self.cmd and not_init:
            self.cmd()


    def _grey(self,override = False):
        ''' TODO Function Description
        '''
        if self.optional and self.choices:
            if not self.optState.get():
                self.value.config(state="disabled")

            else:
                if isinstance(self.value,tkinter.ttk.Combobox):
                    if self.allowEntry:
                        self.value.config(state="enabled")

                    else:
                        self.value.config(state="readonly")

                else:
                    self.value.config(state="enabled")

        if self.sub:
            self.sub._grey()