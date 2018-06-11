import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.lines import Line2D
import datetime
from pprint import pprint
from   my_widget import MyWidget

import tkinter.messagebox as MessageBox

import tkinter
import tkinter.ttk
import tkinter as tk
from tkinter import ttk

from operator import itemgetter
import random
import time

class Graph(tk.Frame):

    def __init__(self, 
                app,
                parent,
                delay = 1000,
                stub=False,
                price_x=None,
                price_y=None,
                bought_x=None,
                bought_y=None,
                sold_x=None,
                sold_y=None,
                x_lowest_sell_order=None,
                y_lowest_sell_order=None,
                x_highest_buy_order=None,
                y_highest_buy_order=None
    ):
        tk.Frame.__init__(self, parent, bg="black")
        self.app = app
        self.parent = parent
        self.stub = stub
        self.delay = delay
        self.x_axis_window_size = 51  # todo: button for changing this
        self.coin_balance = tk.StringVar()
        self.base_balance = tk.StringVar()
        self.mean_price = tk.StringVar()
        self.performance = tk.StringVar()
        self.coin_balance.set("0")
        self.base_balance.set("0")
        self.mean_price.set("0")
        self.performance.set("0")
        self.orderbook = None

        #self.label = tk.Label(self, text=self.parent.pair, font=LARGE_FONT)
        self.label = ttk.Label(self, text=self.parent.name, style="app.TLabel")

        self.fig, self.ax = plt.subplots(1, 2, sharey=True, tight_layout=True,  gridspec_kw = {'width_ratios':[4, 1]})

        self.x_price = price_x if price_x else []
        self.y_price = price_y if price_y else []

        self.line_price = Line2D(self.x_price, self.y_price, color="blue")
        self.ax[0].add_line(self.line_price)

        self.x_bought = bought_x if bought_x else []
        self.y_bought = bought_y if bought_y else []
        self.boughtScatter = self.ax[0].scatter(self.x_bought, self.y_bought, color="lime", marker="P", s=100)

        self.x_sold = sold_x if sold_x else []
        self.y_sold = sold_y if sold_y else []
        self.scatter_sold = self.ax[0].scatter(self.x_sold, self.y_sold, color="salmon", marker="D", s=100)

        self.x_lowest_sell_order = x_lowest_sell_order if x_lowest_sell_order else []
        self.y_lowest_sell_order = y_lowest_sell_order if y_lowest_sell_order else []
        self.line_lowest_sell_order = Line2D(self.x_lowest_sell_order, self.y_lowest_sell_order, color="red")
        self.ax[0].add_line(self.line_lowest_sell_order)

        self.x_highest_buy_order = x_highest_buy_order if x_highest_buy_order else []
        self.y_highest_buy_order = y_highest_buy_order if y_highest_buy_order else []
        self.line_highest_buy_order = Line2D(self.x_highest_buy_order, self.y_highest_buy_order, color="green")
        self.ax[0].add_line(self.line_highest_buy_order)

        #plt.tight_layout()
        #self.fig = Figure(figsize=(5, 5), dpi=100)
        #self.graph = self.fig.add_subplot(111)
        # -----------------------------
        self.ax_depth = self.ax[1]
        self.ax_depth.grid(color='gray', linestyle='--', linewidth=.5)
        # ---------------------------

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.ax[0].grid(color='gray', linestyle='--', linewidth=.5)
        self.ax[0].set_title(self.parent.name, fontsize=10)
        self.canvas.draw()
        self.fig.canvas.mpl_connect('scroll_event', self.process_scroll)
        #self.draw_graph()

        self.toolbar_frame = tk.Frame(self)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar_frame,)
        self.toolbar.update()

        # --------------------------------------
        self.options_frame = tk.Frame(self,bg = "black")
        self.x_axis_auto_scroll = MyWidget(self.app, self.options_frame, optional=True, handle="auto_scroll")
        self.x_axis_window_size_input =  MyWidget(self.app, self.options_frame, choices="entry",ewidth=4, handle="width", startVal="100")

        self.x_axis_auto_scroll.grid(row=0, column=0, sticky=tk.NW, padx=(5.0), pady=(5,0))
        self.x_axis_window_size_input.grid(row=1, column=0, sticky=tk.NW, padx=(28.0), pady=(2,10))
        # --------------------------------------
        self.stats_frame = ttk.Frame(self.options_frame, style="app.TFrame")
        self.profit_base = ttk.Label(self.stats_frame, text="%s \u0394bal:" % self.parent.base_title[:4], style="app.TLabel")
        self.profit_base2 = ttk.Label(self.stats_frame, textvariable=self.base_balance, style="app.TLabel")
        self.profit_alt = ttk.Label(self.stats_frame, text="%s \u0394bal:" % self.parent.coin_title[:4], style="app.TLabel")
        self.profit_alt2 = ttk.Label(self.stats_frame, textvariable=self.coin_balance, style="app.TLabel")
        self.mean_price_lab = ttk.Label(self.stats_frame, text="\u03BC price:", style="app.TLabel")
        self.mean_price_lab2 = ttk.Label(self.stats_frame, textvariable=self.mean_price, style="app.TLabel")
        self.performance_lab = ttk.Label(self.stats_frame, text="\u0394 %:", style="app.TLabel")
        self.performance_lab2 = ttk.Label(self.stats_frame, textvariable=self.performance, style="app.TLabel")

        self.profit_base.grid(row=1, column=0, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        self.profit_base2.grid(row=1, column=1, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        self.profit_alt.grid(row=0, column=0, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        self.profit_alt2.grid(row=0, column=1, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        self.mean_price_lab.grid(row=0, column=2, sticky=tk.NE, padx=(40, 5), pady=(5, 5))
        self.mean_price_lab2.grid(row=0, column=3, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        self.performance_lab.grid(row=1, column=2, sticky=tk.NE, padx=(10, 5), pady=(5, 5))
        self.performance_lab2.grid(row=1, column=3, sticky=tk.NE, padx=(10, 5), pady=(5, 5))

        self.stats_frame.grid(row=0, column=2, rowspan=2, sticky=tk.NW, padx=(28.0), pady=(2,10))
        # --------------------------------------

        self.toolbar_frame.pack(side=tk.TOP, anchor=tk.W, pady=(4,10))
        #self.label.pack(pady=(20,0), padx=10, side=tk.TOP)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.options_frame.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=False)


        # --------------------------------------
        self.x_low, self.x_hi = self.ax[0].get_xlim()
        self.y_low, self.y_hi = self.ax[0].get_ylim()

        #self.loop = animation.FuncAnimation(f, self.refresh,fargs = , interval=1000)

        self.fake_prev_order = "sell"
        if self.stub:
            self.fake_spread = 4
            x_this = datetime.datetime.now()
            #self.fake_orders = {"buy": [(244, 0.5, x_this), (241, 0.5, x_this),(236, 0.5, x_this),(231, 0.5, x_this),(226, 0.5, x_this),(221, 0.5, x_this),(216, 0.5, x_this)],
            #                   "sell": [(253, 0.5, x_this),(258, 0.5, x_this), (263, 0.5, x_this), (263, 0.5, x_this), (268, 0.5, x_this), (273, 0.5, x_this), (278, 0.5, x_this)]}
            self.fake_orders = [dict(price=this_price, date=x_this, type="buy", amount=0.5) for this_price in range(244,100,-10)]
            self.fake_orders.extend([dict(price=this_price, date=x_this, type="sell", amount=0.5) for this_price in range(253,400,10)])
            #self._root().after(5000, self.refresh, self.fake_data())

    def process_scroll(self, event):
        pass

    def draw_orderbook(self, orderbook=None):
        if orderbook:
            bid_prices =  [float(order[0]) for order in orderbook["bids"]]
            bid_amounts = [float(order[1]) for order in orderbook["bids"]]
            ask_prices = [float(order[0]) for order in orderbook["asks"]]
            ask_amounts = [float(order[1]) for order in orderbook["asks"]]
            num_bins_bids = 100 # max(100, len(set(orderbook["bids"])))
            num_bins_asks = 100 # max(100, len(set(orderbook["asks"])))
            self.ax_depth.clear()
            #self.ax_depth.autoscale(False)
            self.ax_depth.grid(color='gray', linestyle='--', linewidth=.5)
            self.ax_depth.hist(bid_prices, weights=bid_amounts, bins=num_bins_bids, orientation="horizontal", color="g")
            self.ax_depth.hist(ask_prices, weights=ask_amounts, bins=num_bins_asks, orientation="horizontal", color="r")
            #self.ax_depth.autoscale(axis="x")
            #self.ax_depth.autoscale(False)

    def draw_depth(self, bps=.35):
        if self.orderbook:
            bidasks = self.orderbook.copy()
            best_bid = max([float(price) for price, amount in bidasks["bids"]])
            best_ask = min([float(price) for price, amount in bidasks["asks"]])
            worst_bid = best_bid * (1 - bps)
            worst_ask = best_ask * (1 + bps)
            filtered_bids = sorted(
                [(float(bid[0]), float(bid[1])) for bid in bidasks["bids"] if float(bid[0]) >= worst_bid],
                key=lambda x: -x[0])
            filtered_asks = sorted(
                [(float(ask[0]), float(ask[1])) for ask in bidasks["asks"] if float(ask[0]) <= worst_ask],
                key=lambda x: +x[0])

            bsizeacc = 0
            bhys = []  # bid - horizontal - ys
            bhxmins = []  # bid - horizontal - xmins
            bhxmaxs = []  # ...
            bvxs = []
            bvymins = []
            bvymaxs = []
            asizeacc = 0
            ahys = []
            ahxmins = []
            ahxmaxs = []
            avxs = []
            avymins = []
            avymaxs = []

            for (p1, s1), (p2, s2) in zip(filtered_bids, filtered_bids[1:]):
                bvymins.append(bsizeacc)
                if bsizeacc == 0:
                    bsizeacc += s1
                bhys.append(bsizeacc)
                bhxmins.append(p2)
                bhxmaxs.append(p1)
                bvxs.append(p2)
                bsizeacc += s2
                bvymaxs.append(bsizeacc)

            for (p1, s1), (p2, s2) in zip(filtered_asks, filtered_asks[1:]):
                avymins.append(asizeacc)
                if asizeacc == 0:
                    asizeacc += s1
                ahys.append(asizeacc)
                ahxmins.append(p1)
                ahxmaxs.append(p2)
                avxs.append(p2)
                asizeacc += s2
                avymaxs.append(asizeacc)

            self.ax_depth.clear()
            self.ax_depth.grid(color='gray', linestyle='--', linewidth=.5)
            self.ax_depth.vlines(bhys[:], bhxmins[:], bhxmaxs[:], color="green")
            self.ax_depth.hlines(bvxs, bvymins, bvymaxs, color="green")
            self.ax_depth.vlines(ahys[:], ahxmins[:], ahxmaxs[:], color="red")
            self.ax_depth.hlines(avxs, avymins, avymaxs, color="red")


    def calc_stats(self):
        ''' TODO Function Description
        '''
        # self.coin_balance.set(str(float(self.coin_balance.get()) + order[1]))
        base_cumulative = float(self.base_balance.get())
        coin_cumulative = float(self.coin_balance.get())

        selling_scenario = coin_cumulative < 0 and base_cumulative > 0
        buying_scenario = coin_cumulative > 0 and base_cumulative < 0
        zero_scenario = coin_cumulative == 0 and base_cumulative == 0
        free_money_scenario = (coin_cumulative >= 0 and base_cumulative > 0) or (coin_cumulative > 0 and base_cumulative >= 0)
        
        try:
            mean_price = abs(base_cumulative / coin_cumulative)
            
        except ZeroDivisionError as e:
            mean_price = "N/A"
            
        except Exception as e:
            MessageBox.showerror("calc_stats error", str(e))
            return
        
        else:
            price_actual = float(self.y_price[-1])
            diff = (abs(mean_price - price_actual) / price_actual) * 100

        if free_money_scenario:
            performance = "inf"
            performance_string = "inf"

        elif buying_scenario:
            if price_actual >= mean_price:
                performance = diff
                
            else:
                performance = -1 * diff
                
        elif selling_scenario:
            if price_actual <= mean_price:
                performance = diff
                
            else:
                performance = -1 * diff
                
        elif zero_scenario:
            performance = 0.0

        if type(performance) == float:
            performance_string = "{0:.3f}".format(performance)

        if type(mean_price) == float:
            mean_price_string = "{0:.5g}".format(mean_price)
            
        else:
            mean_price_string = mean_price

        self.mean_price.set(mean_price_string)
        self.performance.set(performance_string)


    def fake_data(self):
        print("------------- faking data ------------")

        x_this = datetime.datetime.now()
        old_price = self.y_price[-1]

        price = abs(old_price + random.randint(-5, 5))
        print(x_this, price)
        print("fake orders", repr(self.fake_orders))
        data = {
            "price": (x_this, price),
            "open_orders": list(self.fake_orders)

        }

        
        # ----------
        print("------------- fake: filling orders ------------")

        closed = {"filled_orders": []}

        this_fake_orders = list(self.fake_orders)
        fdt = datetime.timedelta(seconds=3)
        for order in this_fake_orders:
            if order["type"] == "buy":
                if price <= float(order["price"]):
                    closed["filled_orders"].append(dict(amount=float(order["amount"]), price=float(order["price"]), date=x_this - fdt, type="buy"))    # was (order[0], order[1], x_this - .5))
                    self.fake_orders.append(dict(amount=float(order["amount"]), price=float(order["price"]) + self.fake_spread, date=x_this - fdt, type="sell"))  # was ((order[0] + self.fake_spread, order[1], x_this - .5))
                    self.fake_orders.remove(order)

            if order["type"] == "sell":
                if price >= float(order["price"]):
                    closed["filled_orders"].append(dict(amount=float(order["amount"]), price=float(order["price"]), date=x_this - fdt, type="sell"))    # was (order[0], order[1], x_this - .5))
                    self.fake_orders.append(dict(amount=float(order["amount"]), price=float(order["price"]) - self.fake_spread, date=x_this - fdt, type="buy"))  # was ((order[0] + self.fake_spread, order[1], x_this - .5))
                    self.fake_orders.remove(order)





        # -----------

        # print(old_price, price,trigger_buy,trigger_sell)
        # if trigger_buy or trigger_sell:
        #     print("#------------\nORDER ALERT:")
        #     closed = {"filled_orders":{"buy":[],
        #                                "sell":[]}}
        #     if trigger_sell:
        #         self.fake_prev_order = "sell"
        #         closed["filled_orders"]["sell"].append((258, 0.5, x_this-1))
        #     if trigger_buy:
        #         self.fake_prev_order = "buy"
        #         closed["filled_orders"]["buy"].append((241, 0.5, x_this-1))
        #     print(data)
        #     data.update(closed)

        if closed["filled_orders"]:
            print("#------------\nORDER ALERT:")
            data.update(closed)
        order_book = {"asks": [], "bids": []}
        for step in range(2,50):
            ask_price = price * (1 + float(step) / 300.0)
            ask_amount = max(0, random.randint(-3, 5))
            bid_price = price * (1 - float(step) / 300.0)
            bid_amount = max(0, random.randint(-3, 5))

            order_book["asks"].append([str(ask_price), str(ask_amount)])
            order_book["bids"].append([str(bid_price), str(bid_amount)])
        data["orderbook"] = order_book

        print(repr(data))
        
        return data


    def date_as_object(self, date):
        ''' TODO Function Description
        '''
        # TODO: do something with date
        if isinstance(date,datetime.date):
            print("already a datetime object")
            return date
        date_object = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return date_object

    def ingest_data(self, data):
        print("------------- ingesting data ------------")
        for k,v in data.items():
            if not k =="filled_orders":
                pprint(k)
                pprint(v)
            else:
                pprint(k)
                if v:
                    pprint(v[0])
        if "price" in data:
            px, py = float(data["price"])
            self.x_price.append(self.date_as_object(px))
            self.y_price.append(py)
        # -----------------------------------------------------

        if "filled_orders" in data:
            ''' Format:
            [
            {'id': '430236', 'date': '2018-05-30 17:03:41', 'type': 'buy', 'price': '0.00000290', 'amount': '78275.86206896', 'total': '0.22700000', 'fee': '0.00000000', 'feepercent': '0.000', 'orderId': '86963799', 'market': 'BTC', 'coin': 'PEPECASH', 'market_pair': 'BTC_PEPECASH'},
            {'id': '423240', 'date': '2018-04-22 06:19:19', 'type': 'sell', 'price': '0.00000500', 'amount': '6711.95200000', 'total': '0.03355976', 'fee': '0.00000000', 'feepercent': '0.000', 'orderId': '90404882', 'market': 'BTC', 'coin': 'PEPECASH', 'market_pair': 'BTC_PEPECASH'},
            ...
            ]
            '''

            for filled in data["filled_orders"]:
                if "buy" == filled["type"]:
                    self.coin_balance.set(str(float(self.coin_balance.get()) + float(filled["amount"])))
                    self.base_balance.set(str(float(self.base_balance.get()) - (float(filled["amount"]) * float(filled["price"]))))
                    bx = self.date_as_object(filled["date"])  # date
                    by = float(filled["price"])
                    self.x_bought.append(bx)
                    self.y_bought.append(by)

                elif "sell" == filled["type"]:
                    self.coin_balance.set(str(float(self.coin_balance.get()) - float(filled["amount"])))
                    self.base_balance.set(str(float(self.base_balance.get()) + (float(filled["amount"]) * float(filled["price"]))))
                    sx = self.date_as_object(filled["date"])  # date
                    sy = float(filled["price"])
                    self.x_sold.append(sx)
                    self.y_sold.append(sy)

        # -----------------------------------------------------
        order_price_index = 0  # sort on first element of tuple which should be price (for now)
        order_time_index = 2

        if "open_orders" in data:
            if isinstance(data["open_orders"], dict):
                data["open_orders"] = [v for k,v in data["open_orders"].items()]
            '''
            {'coin': 'PEPECASH', 'market': 'BTC', 'date': '2017-10-14 09:05:27', 'type': 'sell', 'price': '0.00000835',
             'amount': '5988.02395209', 'total': '0.04999999', 'id': '85911467', 'filledamount': '0.00000000',
             'initamount': '5988.02395209', 'market_pair': 'BTC_PEPECASH'}, '85902008': {'coin': 'PEPECASH',
                                                                                         'market': 'BTC',
                                                                                         'date': '2017-10-13 18:42:02',
                                                                                         'type': 'buy',
                                                                                         'price': '0.00000227',
                                                                                         'amount': '70484.58149780',
                                                                                         'total': '0.16000000',
                                                                                         'id': '85902008',
                                                                                         'filledamount': '0.00000000',
                                                                                         'initamount': '70484.58149780',
                                                                                         'market_pair': 'BTC_PEPECASH'}
                                                                                         '''
            sell_amounts = [float(order["price"]) for order in data["open_orders"] if order["type"] == "sell"]
            buy_amounts = [float(order["price"]) for order in data["open_orders"] if order["type"] == "buy"]


            if sell_amounts:
                lowest_sell = min(sell_amounts)
                self.x_lowest_sell_order.append(datetime.datetime.now())
                self.y_lowest_sell_order.append(lowest_sell)
                #if len(sell_amounts) > 1:  # then we have a meaningful "high" order
                    ## todo: something with this data
                    #highest_sell = max(sell_amounts)

            if buy_amounts:
                highest_buy = max(buy_amounts)
                self.x_highest_buy_order.append(datetime.datetime.now())
                self.y_highest_buy_order.append(highest_buy)
                #if len(buy_amounts) > 1:  # then we have a meaningful "high" order
                    ## todo: something with this data
                    #lowest_buy = min(buy_amounts)

        # -----------------------------------------------------
        if "orderbook" in data:
            self.orderbook = data["orderbook"]

    def draw_graph(self):
        print("------------- drawing graph ------------")

        self.x_low, self.x_hi = self.ax[0].get_xlim()
        self.y_low, self.y_hi = self.ax[0].get_ylim()
        self.ax[0].clear()
        print("cleared self.ax[0]")

        if self.x_price and self.y_price:
            self.line_price.set_data(self.x_price, self.y_price)
            self.ax[0].add_line(self.line_price)

        if self.x_bought and self.y_bought:
            # self.boughtScatter.set_offsets((self.x_bought, self.y_bought))
            self.boughtScatter = self.ax[0].scatter(self.x_bought, self.y_bought, color="lime", marker="P", s=100)

        if self.x_sold and self.y_sold:
            # self.scatter_sold.set_offsets((self.x_sold, self.y_sold))
            self.scatter_sold = self.ax[0].scatter(self.x_sold, self.y_sold, color="salmon", marker="D", s=100)

        if self.x_lowest_sell_order and self.y_lowest_sell_order:
            self.line_lowest_sell_order.set_data(self.x_lowest_sell_order, self.y_lowest_sell_order)
            self.ax[0].add_line(self.line_lowest_sell_order)

        if self.x_highest_buy_order and self.y_highest_buy_order:
            self.line_highest_buy_order.set_data(self.x_highest_buy_order, self.y_highest_buy_order)
            self.ax[0].add_line(self.line_highest_buy_order)



        try:
            self.draw_depth()
        except:
            pass

        self.format_graph()

        self.canvas.draw()

    def format_graph(self):
        try:
            this_window_size = max(int(self.x_axis_window_size_input.get()[0]), 5)

        except:
            this_window_size = 50

        if True:
            if self.x_axis_auto_scroll.optState.get():

                if len(self.x_price) > this_window_size:
                    self.ax[0].set_xlim(self.x_price[-1 * this_window_size + 1], self.x_price[-1])
                    # self.ax[0].autoscale(axis="y")
                    self.ax[0].set_ylim(self.y_price[-1] * .85, self.y_price[-1] * 1.15)

                else:
                    # self.ax[0].autoscale(axis="y")
                    self.ax[0].set_ylim(self.y_price[-1] * .85, self.y_price[-1] * 1.15)
                    self.ax[0].set_xlim(self.x_price[0], self.x_price[-1])

            else:
                print("trying:  ", self.x_low, self.x_hi, self.y_low, self.y_hi)
                self.ax[0].set_xlim(self.x_low, self.x_hi)
                self.ax[0].set_ylim(self.y_low, self.y_hi)

        self.ax[0].grid(color='gray', linestyle='--', linewidth=.5)

        #self.ax[0].set_xticklabels([str(d) for d in self.x_price])
        self.ax[0].set_title(self.parent.name, fontsize=10)

        hfmt = matplotlib.dates.DateFormatter('%H:%M:%S')
        self.ax[0].xaxis.set_major_formatter(hfmt)
        self.ax[0].tick_params(axis='x', labelsize=8)
        #self.ax[0].set_xlim(self.x_price[0], self.x_price[-1])
        self.fig.autofmt_xdate()

    def check_dates(self,dates):
        for d in dates:
            print(d.isoformat(),datetime.datetime.toordinal(d))
            if not isinstance(d,datetime.date):
                raise Exception("Found bad date: %s %s " % (type(d),d))

    def refresh(self, data, active=True):
        '''
        :param data: a dictionary that comes from bot update method.  todo: agree on format for data
        :return:
        '''

        try:
            self.ingest_data(data)
            self.calc_stats()
            if active:
                self.draw_graph()
        except Exception as e:
            print(str(e))
            raise

        finally:
            
            if False:
                duration = time.time() - start
                this_delay = int(max((self.delay - duration * 1000), 100))  # be at least 100 ms, assumes past behavior predicts future ;)
                print("duration of graph refresh: ", duration)
                self._root().after(this_delay, self.refresh, self.fake_data())
