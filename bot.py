from merkato.merkato import Merkato
from merkato.utils import database_utils
from merkato.utils.database_utils import no_merkatos_table_exists, create_merkatos_table, insert_merkato, get_all_merkatos, get_exchange, no_exchanges_table_exists, create_exchanges_table
from merkato.utils import generate_complete_merkato_configs


from   graph import Graph
from   my_widget import MyWidget
import tkinter.messagebox as MessageBox

import tkinter
import tkinter.ttk
import tkinter as tk
from tkinter import ttk

class Bot(ttk.Frame):

    def __init__(self,
                 app,
                 parent,
                 owner,
                 persist = None,
                 stub = False,
                 auto_start = False,
                 starting_stats=None,
                 *args,
                 **kwargs
                 ):
        ttk.Frame.__init__(self, parent, style="app.TFrame", *args, **kwargs)
        self.app = app # root
        self.parent = parent # containing frame
        self.owner = owner
        self.stub = stub
        self.is_active = False
        self.title_var = tk.StringVar()
        self.coin_title = "coin"
        self.base_title = "base"
        self.exchange_title = "<exchange>"
        
        if self.stub:
            self.name = "XMR/BTC  Stub"

        else:
            self.name = "New Merkato"

        self.title_var.set(str(self.name))

        # merkato args
        #self.auth_frame = ttk.Frame(self, style="app.TFrame")
        self.bot = None

        if persist:
            self.name = persist["coin"] + "/" + persist["base"] + "    " + persist["configuration"]["exchange"]
            self.title_var.set(str(self.name))
            self.bot = Merkato(**persist) #presumably from db

        # --------------------
        self.exchange_frame = ttk.Frame(self, style="app.TFrame")
        self.exchange_menu, self.exchange_index = database_utils.get_all_exchanges()
        self.exchange_name = MyWidget(self.app, self.exchange_frame, handle="exchange", choices= self.exchange_menu)
        self.coin = MyWidget(self.app, self.exchange_frame, handle="coin", choices= ["XMR", "LTC", "PEPE"])
        self.base = MyWidget(self.app, self.exchange_frame, handle="base", choices= ["BTC","USDT"])
        #self.public_key = MyWidget(self.app, self.exchange_frame, handle="pub. key", choices="entry")
        #self.private_key = MyWidget(self.app, self.exchange_frame, handle="priv. key", is_password=True, choices="entry")

        self.ask_budget = MyWidget(self.app, self.exchange_frame, handle="coin reserve", startVal=0.0, choices="entry")
        self.bid_budget = MyWidget(self.app, self.exchange_frame, handle="base reserve", startVal=0.0, choices="entry")
        self.spread = MyWidget(self.app, self.exchange_frame, handle="spread [%]", startVal=5.0, choices="entry")
        self.execute = ttk.Button(self.exchange_frame, text = "Launch", cursor = "shuttle", command= self.start)

        self.exchange_name.grid(row=0, column=0,sticky=tk.NE, padx=(10,5), pady=(5,5))
        self.coin.grid(row=1, column=0, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        self.base.grid(row=2, column=0, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        #self.public_key.grid(row=3, column=0,  sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        #self.private_key.grid(row=4, column=0, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        self.ask_budget.grid(row=5, column=0,sticky=tk.NE, padx=(10,5), pady=(5,5))
        self.bid_budget.grid(row=6, column=0,sticky=tk.NE, padx=(10,5), pady=(5,5))
        self.spread.grid(row=7, column=0, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        self.execute.grid(row=8, column=0, sticky=tk.NE, padx=(10,5), pady=(15,5))
        # --------------------
        self.util_frame = ttk.Frame(self, style="app.TFrame")
        self.kill_button = ttk.Button(self.util_frame, text="Kill", cursor="shuttle", command=self.kill)
        self.kill_button.grid(row=0, column=0, sticky=tk.SE, padx=(10,5), pady=(15,5))
        # --------------------
        if not starting_stats:
            starting_stats= {"price_x": []}
        self.graph = Graph(self.app, self, stub=self.stub, **starting_stats)

        self.graph.grid(row = 0, column=0, rowspan=3, padx=(5,10))
        #self.auth_frame.grid(row = 0, column=1, sticky=tk.NE, padx=(10,10), pady=(20,5))
        if not self.bot:
            self.exchange_frame.grid(row = 0, column=1, sticky=tk.NE, padx=(10,10), pady=(20,5))
        self.util_frame.grid(row = 1, column=1, sticky=tk.SE, padx=(10,10), pady=(10,5))


    def update(self):

        if self.stub or self.bot: # then we have something to update
            print("---------------  updating %s ----------------------" % self.name)
            
            if not self.stub:
                context = self.bot.update()
                
            else:
                context = self.graph.fake_data()

            self.graph.refresh(data=context, active=self.is_active)
            
            try:
                self.title_var.set(str(self.name) + "   " + str(self.graph.performance.get()))
                
            except:
                self.title_var.set(str(self.name) + "   err")

    def start(self):
        for widget in [self.exchange_name,self.coin, self.base, self.ask_budget, self.bid_budget]:
            print("{}:\t\t{}".format(widget.handle,widget.get()[0]))

        #config = {}
        self.merk_args = {}

        #config['privatekey'] = self.private_key.get()[0]
        #config['publickey']  = self.public_key.get()[0]
        #config['limit_only'] = True

        self.merk_args["configuration"] = self.exchange_index[ self.exchange_name.get()[0]]
        #self.merk_args["exchange"] = self.exchange_name.get()[0]
        self.merk_args["coin"] = self.coin.get()[0]
        self.merk_args["base"] = self.base.get()[0]
        self.merk_args["coin_reserve"] = float(self.ask_budget.get()[0])
        self.merk_args["base_reserve"] = float(self.bid_budget.get()[0])
        self.merk_args["spread"] = float(self.spread.get()[0]) / 100.0

        self.coin_title = self.merk_args["coin"]
        self.base_title = self.merk_args["base"]
        self.graph.profit_base.config(text="%s \u0394bal:" % self.base_title[:4])
        self.graph.profit_alt.config(text="%s \u0394bal:" % self.coin_title[:4])
        self.exchange_title = self.merk_args["configuration"]["exchange"]
        self.name = str(self.merk_args["coin"]) + "/" + str(self.merk_args["base"]) + "    " + self.exchange_title
        self.title_var.set(str(self.name))

        if not self.stub:
            try:
              self.bot = Merkato(**self.merk_args)
            except Exception as e:
                MessageBox.showerror("Bot Start Fail", str(e) + repr(self.merk_args))

            else:
                self.exchange_frame.destroy()

    def kill(self):
        # TODO: tell self.bot to cancel all orders and delete merkato from DB
        self._root().after(10, self.owner.kill_screen, self)



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
