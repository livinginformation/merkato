
#from exchange import Exchange
#from merkato import Merkato

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.lines import Line2D

import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import tkinter
import tkinter.ttk
import tkinter as tk
from tkinter import ttk

from operator import itemgetter
import random
import time

LARGE_FONT= ("Liberation Mono", 12)
print(style.available)
style.use("dark_background")

"""
expected bot data format from merkato

{
"open_orders" : { "buy" : [(0.022, 0.5), 
                           (0.018, 1.5) ],
                  "sell"  : [(0.027, 0.5), 
                             (0.033,1.5) ]},
"filled_orders" :  {"buy" : [(0.022, 0.5, 2016-08-26 18:53:38), 
                             (0.018, 1.5, 2016-08-26 18:53:38) ],
                    "sell"  : [(0.027, 0.5 ,2016-08-26 18:53:38), 
                              (0.033,1.5, YYYY-MM-DD HH:MM:SS) ]},                          
"balances" : {"BTC" : 0.5121,
              "XMR": 15.2039},
"market" : (00.24,0.026),
"price"  : 0.025
                    
}
"""

class Graph(tk.Frame):

    def __init__(self, app, parent, delay = 5000, stub=False, price_x=[], price_y=[], bought_x=[], bought_y=[], sold_x=[], sold_y=[],
                 x_lowest_sell_order=[], y_lowest_sell_order=[], x_highest_buy_order=[], y_highest_buy_order=[]):
        tk.Frame.__init__(self, parent, bg="black")
        self.app = app
        self.parent = parent
        self.stub = stub
        self.delay = delay
        self.x_axis_window_size = 31  # todo: button for changing this

        #self.label = tk.Label(self, text=self.parent.pair, font=LARGE_FONT)
        self.label = ttk.Label(self, text=self.parent.title, style="app.TLabel")



        self.fig, self.ax = plt.subplots()

        self.x_price = price_x
        self.y_price = price_y
        self.line_price = Line2D(self.x_price, self.y_price, color="blue")
        self.ax.add_line(self.line_price)

        self.x_bought = bought_x
        self.y_bought = bought_y
        self.boughtScatter = self.ax.scatter(self.x_bought, self.y_bought, color="lime", marker="P", s=100)

        self.x_sold = sold_x
        self.y_sold = sold_y
        self.scatter_sold = self.ax.scatter(self.x_sold, self.y_sold, color="salmon", marker="D", s=100)

        self.x_lowest_sell_order = x_lowest_sell_order
        self.y_lowest_sell_order = y_lowest_sell_order
        self.line_lowest_sell_order = Line2D(self.x_lowest_sell_order, self.y_lowest_sell_order, color="red")
        self.ax.add_line(self.line_lowest_sell_order)

        self.x_highest_buy_order = x_highest_buy_order
        self.y_highest_buy_order = y_highest_buy_order
        self.line_highest_buy_order = Line2D(self.x_highest_buy_order, self.y_highest_buy_order, color="green")
        self.ax.add_line(self.line_highest_buy_order)

        plt.tight_layout()
        #self.fig = Figure(figsize=(5, 5), dpi=100)
        #self.graph = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.ax.grid(color='gray', linestyle='--', linewidth=.5)
        self.ax.set_title(self.parent.title)
        self.canvas.draw()


        self.toolbar_frame = tk.Frame(self)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar_frame,)
        self.toolbar.update()

        # --------------------------------------
        self.options_frame = tk.Frame(self,bg = "black")
        self.x_axis_auto_scroll = MyWidget(self.app, self.options_frame, optional=True, handle="auto scroll")
        self.x_axis_auto_scroll.grid(row=0, column=0, sticky=tk.NE)
        # --------------------------------------

        self.toolbar_frame.pack(side=tk.TOP, anchor=tk.W, pady=(4,10))
        #self.label.pack(pady=(20,0), padx=10, side=tk.TOP)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.options_frame.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=True)

        # --------------------------------------
        self.x_low, self.x_hi = self.ax.get_xlim()
        self.y_low, self.y_hi = self.ax.get_ylim()

        #self.loop = animation.FuncAnimation(f, self.refresh,fargs = , interval=1000)

        if self.stub:
            self._root().after(5000, self.refresh, self.fake_data())


    def fake_data(self):
        x_this = self.x_price[-1] + 1
        old_price = self.y_price[-1]

        price = old_price + random.randint(-5, 5)
        data = {
            "price": (x_this, price),
            "open_orders": {"buy": [(241, 0.5, x_this)],
                            "sell": [(258, 0.5, x_this)]},

        }

        trigger_buy = old_price > 241 and price < 241
        trigger_sell = old_price < 258 and price > 258
        print(old_price, price,trigger_buy,trigger_sell)
        if trigger_buy or trigger_sell:
            print("#------------\nORDER ALERT:")
            closed = {"filled_orders":{"buy":[],
                                       "sell":[]}}
            if trigger_sell:
                self.fake_prev_order = "sell"
                closed["filled_orders"]["sell"].append((258, 0.5, x_this-1))
            if trigger_buy:
                closed["filled_orders"]["buy"].append((241, 0.5, x_this-1))
            print(data)
            data.update(closed)


        print(repr(data))
        return data

    def date_formatter(self, date):
        # TODO: do something with date
        return date

    def refresh(self, data):
        """
        :param data: a dictionary that comes from bot update method.  todo: agree on format for data
        :return:
        """
        self.x_low, self.x_hi = self.ax.get_xlim()
        self.y_low, self.y_hi = self.ax.get_ylim()
        start = time.time()
        self.ax.clear()
        print("cleared self.ax")
        try:
            if "price" in data:
                px, py = data["price"]
                self.x_price.append(self.date_formatter(px))
                self.y_price.append(py)
            if self.x_price and self.y_price:
                self.line_price.set_data(self.x_price, self.y_price)
                self.ax.add_line(self.line_price)

            # -----------------------------------------------------

            if "filled_orders" in data:
                if "buy" in data["filled_orders"]:
                    for filled in data["filled_orders"]["buy"]:
                        bx = self.date_formatter(filled[2]) # date
                        by = filled[0]
                        self.x_bought.append(bx)
                        self.y_bought.append(by)
            if self.x_bought and self.y_bought:
                print(self.x_bought, self.y_bought)
                #self.boughtScatter.set_offsets((self.x_bought, self.y_bought))
                self.boughtScatter = self.ax.scatter(self.x_bought, self.y_bought, color="lime", marker="P", s=100)

            # -----------------------------------------------------
            if "filled_orders" in data:
                if "sell" in data["filled_orders"]:
                    for filled in data["filled_orders"]["sell"]:
                        sx = self.date_formatter(filled[2]) # date
                        sy = filled[0]
                        self.x_sold.append(sx)
                        self.y_sold.append(sy)
            if self.x_sold and self.y_sold:
                #self.scatter_sold.set_offsets((self.x_sold, self.y_sold))
                self.scatter_sold = self.ax.scatter(self.x_sold, self.y_sold, color="salmon", marker="D", s=100)
            # -----------------------------------------------------
            order_price_index = 0  # sort on first element of tuple which should be price (for now)
            order_time_index = 2
            if "open_orders" in data:
                if "sell" in data["open_orders"]:
                    sell_data = data["open_orders"]["sell"]
                    if sell_data:
                        lowest_sell = sorted(sell_data, key=itemgetter(order_price_index))[0]
                        self.x_lowest_sell_order.append(self.date_formatter(lowest_sell[order_time_index]))
                        self.y_lowest_sell_order.append(lowest_sell[order_price_index])
                        if len(sell_data) > 1:   # then we have a meaningful "high" order
                            # todo: something with this data
                            highest_sell = sorted(sell_data, key=itemgetter(order_price_index))[-1]

                if "buy" in data["open_orders"]:
                    buy_data = data["open_orders"]["buy"]
                    if buy_data:
                        highest_buy = sorted(buy_data, key=itemgetter(order_price_index))[-1]
                        self.x_highest_buy_order.append(self.date_formatter(highest_buy[order_time_index]))
                        self.y_highest_buy_order.append(highest_buy[order_price_index])
                        if len(buy_data) > 1:   # then we have a meaningful "low" order
                            # todo: something with this data
                            lowest_buy = sorted(buy_data, key=itemgetter(order_price_index))[0]

            if self.x_lowest_sell_order and self.y_lowest_sell_order:
                self.line_lowest_sell_order.set_data(self.x_lowest_sell_order, self.y_lowest_sell_order)
                self.ax.add_line(self.line_lowest_sell_order)

            if self.x_highest_buy_order and self.y_highest_buy_order:
                self.line_highest_buy_order.set_data(self.x_highest_buy_order, self.y_highest_buy_order)
                self.ax.add_line(self.line_highest_buy_order)
            # -----------------------------------------------------

            print("------->",self.x_axis_auto_scroll.optState.get())
            if self.x_axis_auto_scroll.optState.get():
                if len(self.x_price) > self.x_axis_window_size:
                    self.ax.set_xlim(self.x_price[-1 * self.x_axis_window_size + 1], self.x_price[-1])
                    self.ax.autoscale(axis="y")
                else:
                    self.ax.autoscale(axis="y")

            else:
                print("trying:  ", self.x_low, self.x_hi, self.y_low, self.y_hi)
                self.ax.set_xlim(self.x_low, self.x_hi)
                self.ax.set_ylim(self.y_low, self.y_hi)

            self.ax.grid(color='gray', linestyle='--', linewidth=.5)
            self.ax.set_title(self.parent.title, fontsize=10)
            self.canvas.draw()



        except Exception as e:
            print(str(e))
            raise
        finally:
            if self.stub:
                duration = time.time() - start
                this_delay = int(max((self.delay - duration * 1000), 100))  # be at least 100 ms, assumes past behavior predicts future ;)
                print("duration of graph refresh: ", duration)
                self._root().after(this_delay, self.refresh, self.fake_data())




class Bot(ttk.Frame):
    def __init__(self,app, parent, exchange_config={}, stub = False, title = "merkato",pair="", auto_start = False, starting_stats = {"price_x": []}, *args, **kwargs):
        ttk.Frame.__init__(self, parent, style="app.TFrame", *args, **kwargs)
        self.app = app
        self.parent = parent
        self.stub = stub
        # if background and not self.app.light:
        #     self.bg = tk.PhotoImage(file = background)
        #     self.bglabel = tk.Label(self, image=self.bg)
        #     self.bglabel.place(x=0, y=0, relwidth=1, relheight=1)
        self.pair = pair # TODO: unused for now
        self.title = title
        self.heading = ttk.Label(self, text=self.title, style="heading.TLabel")

        # merkato args
        #self.auth_frame = ttk.Frame(self, style="app.TFrame")

        # --------------------
        self.exchange_frame = ttk.Frame(self, style="app.TFrame")
        self.exchange_name = MyWidget(self.app, self.exchange_frame, handle="exchange", choices= ["tux", "polo", "kraken", "gdax"])
        self.coin = MyWidget(self.app, self.exchange_frame, handle="coin", choices= ["XMR", "LTC", "PEPE"])
        self.base = MyWidget(self.app, self.exchange_frame, handle="base", choices= ["BTC","USDT"])
        self.public_key = MyWidget(self.app, self.exchange_frame, handle="pub. key", choices="entry")
        self.private_key = MyWidget(self.app, self.exchange_frame, handle="priv. key", is_password=True, choices="entry")

        self.ask_budget = MyWidget(self.app, self.exchange_frame, handle="sell budget", startVal=0.0, choices="entry")
        self.bid_budget = MyWidget(self.app, self.exchange_frame, handle="buy budget", startVal=0.0, choices="entry")
        self.execute = ttk.Button(self.exchange_frame, text = "Launch", cursor = "shuttle", command= self.start)

        self.exchange_name.grid(row=0, column=0,sticky=tk.NE, padx=(10,10), pady=(5,5))
        self.coin.grid(row=0, column=1, sticky=tk.NE, padx=(10, 10), pady=(5, 5))
        self.base.grid(row=1, column=1, sticky=tk.NE, padx=(10, 10), pady=(5, 5))
        self.public_key.grid(row=2, column=0, sticky=tk.NE, padx=(10, 10), pady=(5, 5))
        self.private_key.grid(row=2, column=1, sticky=tk.NE, padx=(10, 10), pady=(5, 5))
        self.ask_budget.grid(row=3, column=1,sticky=tk.NE, padx=(10,10), pady=(5,5))
        self.bid_budget.grid(row=3, column=0,sticky=tk.NE, padx=(10,10), pady=(5,5))
        self.execute.grid(row=4, column=1, sticky=tk.NE, padx=(10,10), pady=(15,5))
        # --------------------
        self.graph = Graph(self.app,self,stub=self.stub, **starting_stats)

        self.graph.grid(row = 0, column=0, rowspan=3, padx=(5,10))
        #self.auth_frame.grid(row = 0, column=1, sticky=tk.NE, padx=(10,10), pady=(20,5))
        self.exchange_frame.grid(row = 0, column=1, sticky=tk.NE, padx=(10,10), pady=(20,5))



    def start(self):
        for widget in [self.public_key, self.private_key, self.exchange_name,self.coin, self.base, self.ask_budget, self.bid_budget]:
            print("{}:\t\t{}".format(widget.handle,widget.get()[0]))

        # if not exchange_config:
        #     # get args via gui
        #     pass
        #self.bot = Merkato(exchange_config)

        """
        #self.body = VSFrame(self,fheight = 430,nobar = True)
        self.dest = Destination(self.app,self,name = "",cwidth = 40,select_handle = "Subaddress Book",background = "misc/genericspace.gif",mode = "receive")

        self.addresses = []

        #self.textAddress = MyWidget(self.app,self.body.interior,handle = "Address",choices = [self.app.initAddress],cwidth = 50,startVal =  self.app.initAddress )
        self.amountVar = tk.StringVar()
        self.dest.amount.value.config(textvariable = self.amountVar)
        self.new_label = MyWidget(self.app,self,handle = "New Subaddress",ewidth=23,choices = "entry",startVal = "<label goes here>")
        self.moon3 = tk.PhotoImage(file = "misc/moonbutton3.gif")
        if "monero" not in sys.argv[1]:
            self.new_button = tk.Button(self,text = "New Sub.",command =self.new_subaddress,highlightthickness=0,font=('Liberation Mono','12','normal'),foreground = "white",bd = 3,bg = "#2D89A0" )
        else:
            self.new_button = tk.Button(self,text = "New Sub.",command =self.new_subaddress,image = self.moon3,compound = tk.CENTER,height = 18,width = 60,highlightthickness=0,font=('Liberation Mono','12','normal'),foreground = "white",bd = 3,bg = "#900100" )
        #self.amount = MyWidget(self.app,self.body.interior,handle = "Amount",choices = "entry",optional = True,activeStart=False)
        #self.amount.value.configure(textvariable = self.amountVar)
        self.amountVar.trace("w", lambda name, index, mode, sv=self.amountVar: self.amountCallback(sv))
        #self.amount.optState.trace("w", lambda name, index, mode, sv=self.amountVar: self.amountCallback(sv))
        self.qr = ttk.Label(self,style = "app.TLabel")
        self.genQR()

        self.heading.grid(row=0,column=0,sticky = tk.W,pady= (10,15))
        #self.body.grid(row=1,column=0,sticky = tk.W+ tk.E,pady= (5,20))
        self.dest.grid(row=1,column=0,columnspan = 2,sticky = tk.W,padx = (15,15))
        self.new_label.grid(row=2,column=0,sticky = tk.W,padx = (109,0),pady=(15,0))
        self.new_button.grid(row=2,column=1,sticky = tk.W,padx = (0,10),pady=(25,0))
        #self.textAddress.grid(row=1,column=0,columnspan = 2,sticky = tk.W)
        #self.amount.grid(row=2,column=1,sticky = tk.E,pady= (10,0))
        self.qr.grid(row=3,column=0,sticky = tk.W+tk.E,padx=(140,0),pady= (15,80),columnspan = 3)
        """

class MyWidget(ttk.Frame):
    def __init__(self,app, parent,handle,choices=None,subs = {}, is_password = False,startVal = None,allowEntry = False,static = False,
                 cipadx = 0,optional = False,activeStart=1,ewidth = 8,cwidth = None, cmd = None, *args, **kwargs):
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
            self.optBut = ttk.Checkbutton(self,variable = self.optState,onvalue = 1,offvalue=0,command = self._grey,style = "app.TCheckbutton")
            self.optBut.pack(side="left")
        if isinstance(self.choices,__builtins__.list):
            if not allowEntry:
                state = "readonly"
            else:
                state = "enabled"
            if not cwidth: cwidth = len(max(self.choices,key=len))
            self.value = ttk.Combobox(self,values = self.choices,state = state,width=cwidth,postcommand = self.wideMenu,style = "app.TCombobox")
            self.value.bind('<<ComboboxSelected>>',self.findSubs)
            #self.value.bind('<Configure>', self.wideMenu)
        if self.choices == "entry":
            state = "enabled" if not static else "readonly"
            if not is_password:
                self.value = ttk.Entry(self,width=ewidth,style = "app.TEntry",state = state)
            else:
                self.value = ttk.Entry(self, width=ewidth, style="app.TEntry", state=state, show="*")
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

    def findSubs(self,event = None,not_init = True):
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




if __name__ == "__main__":
    root = tk.Tk()
    root.title("merkato (pre-release)")
    mystyle = ttk.Style()
    mystyle.theme_use('clam')  # ('clam', 'alt', 'default', 'classic')
    mystyle.configure("app.TLabel", foreground="white", background="black",
                      font=('Liberation Mono', '10', 'normal'))  # "#4C4C4C")
    mystyle.configure("unlocked.TLabel", foreground="light green", background="black",
                      font=('Liberation Mono', '12', 'normal'))  # "#4C4C4C")
    mystyle.configure("smaller.TLabel", foreground="white", background="black",
                      font=('Liberation Mono', '10', 'normal'))  # "#4C4C4C")
    mystyle.configure("heading.TLabel", foreground="white", background="black",
                      font=('Liberation Mono', '36', 'normal'))  # "#4C4C4C")
    mystyle.configure("app.TFrame", foreground="gray55", background="black")  # "#4C4C4C",)
    mystyle.configure("app.TButton", foreground="gray55", background="#D15101", activeforeground="#F2681C")  # F2681C
    mystyle.configure("app.TCheckbutton", foreground="gray55", background="black")  # "#4C4C4C")
    mystyle.configure("app.TCombobox", background="#F2681C", selectbackground="#D15101")  # postoffset = (0,0,500,0))
    mystyle.configure("app.TEntry", foreground="black", background="gray55")
    mystyle.configure("pass.TEntry", foreground="gray55", background="gray55", insertofftime=5000)
    root.option_add("*TCombobox*Listbox*selectBackground", "#D15101")


    targs = {
            "price_x" : [1,2,3,4,5,6,7,8,9,10, 11],
            "price_y" : [250,250,240,240,250,260,260,240,230,260,250],
            "bought_x" : [3,8,],
            "bought_y" : [241,241,],
            "sold_x" : [5.85,10],
            "sold_y" : [258,258],
            "x_lowest_sell_order" : [1,2,3,4,5,6,7,8,9,10],
            "y_lowest_sell_order" : [258, 258, 258, 258, 258, 258, 258, 258, 258, 258, ],
            "x_highest_buy_order" : [1,2,3,4,5,6,7,8,9,10],
            "y_highest_buy_order" : [241, 241, 241, 241, 241, 241, 241, 241, 241, 241, ],
            }
    test = Bot(root, root, stub = 1, title="Stub GUI (very raw)", starting_stats=targs)
    test.pack()

    root.mainloop()
