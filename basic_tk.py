from merkato.merkato_config import load_config, get_config, create_config
from merkato.merkato import Merkato
from merkato.parser import parse
from merkato.utils.database_utils import no_merkatos_table_exists, create_merkatos_table, insert_merkato, get_all_merkatos, get_exchange, no_exchanges_table_exists, create_exchanges_table, drop_merkatos_table, drop_exchanges_table
from merkato.utils import generate_complete_merkato_configs
import sqlite3
import time
import pprint
import tkinter as tk


welcome_txt = """Welcome to Merkato Would you like to run current merkatos, or create a new exchange or merkato?."""
drop_merkatos_txt = "Do you want to drop merkatos?"
drop_exchanges_txt = "Do you want to drop exchanges?"
public_key_text = """Please enter your api public key"""
private_key_text = """Please enter your api secret key"""
exchange_select_txt = """Please select an exchange"""


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.base = "BTC"
        self.coin = "XMR"
        self.spread = .02
        self.coin_reserve = 17
        self.base_reserve = .4
        self.pack()
        self.create_widgets()


    def create_widgets(self):

        welcome_message = tk.Label(self, anchor='n', padx = 10, text=welcome_txt)
        welcome_message.pack(side="top")
      
        run_merkatos = tk.Button(self, command=self.start_simple_app)
        run_merkatos["text"] = "Run Merkatos"
        run_merkatos.pack(side="top")

        create_new = tk.Button(self, command=self.start_create_frame)
        create_new["text"] = "Create New Merk/Exc"
        create_new.pack(side="top")

        quit = tk.Button(self, text="QUIT", fg="red", command=root.destroy)
        quit.pack(side="top")


    def start_simple_app(self):
        self.remove_all_widgets()


    def start_create_frame(self):
        self.remove_all_widgets()
        self.run_remove_tables_prompts()


    def remove_all_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()


    def run_remove_tables_prompts(self):
        if no_merkatos_table_exists():
            create_merkatos_table()
            self.run_remove_exchanges_prompts()
        else:
            self.run_remove_merkatos_prompt()


    def run_remove_merkatos_prompt(self):
        drop_merkatos_message = tk.Label(self, anchor='n', padx = 10, text=drop_merkatos_txt).pack(side="top")
        
        drop_merkatos = tk.Button(self, command=self.drop_merkatos_table)
        drop_merkatos["text"] = "Yes"
        drop_merkatos.pack(side="bottom")
      
        dont_drop_merkatos = tk.Button(self, command=self.dont_drop_merkatos_table)
        dont_drop_merkatos["text"] = "No"
        dont_drop_merkatos.pack(side="bottom")


    def run_remove_exchanges_prompts(self):
        drop_merkatos_message = tk.Label(self, anchor='n', padx = 10, text=drop_exchanges_txt).pack(side="top")

        drop_exchanges = tk.Button(self, command=self.drop_exchanges_table)
        rop_exchanges["text"] = "Yes"
        drop_exchanges.pack(side="bottom")
      
        dont_drop_exchanges = tk.Button(self, command=self.dont_drop_exchanges_table)
        dont_drop_exchanges["text"] = "No"
        dont_drop_exchanges.pack(side="bottom")


    def run_enter_api_key_info(self):
        public_key_field = tk.Entry(self, width=40)
        private_key_field = tk.Entry(self, width=40)

        private_key_message = tk.Label(self, anchor='n', padx = 10, text=private_key_text)
        public_key_message = tk.Label(self, anchor='n', padx = 10, text=public_key_text)

        submit_keys = tk.Button(self, command=self.submit_api_keys)
        submit_keys["text"] = "Submit keys"

        public_key_field.pack(side="top")
        public_key_message.pack(side="top")

        private_key_field.pack(side="top")
        private_key_message.pack(side="top")

        submit_keys.pack(side="bottom")


    def drop_merkatos_table(self):
        drop_merkatos_table()
        self.remove_all_widgets()
        self.run_remove_exchanges_prompts()


    def dont_drop_merkatos_table(self):
        self.remove_all_widgets()
        self.run_remove_exchanges_prompts()


    def drop_exchanges_table(self):
        drop_exchanges_table()
        self.remove_all_widgets()
        self.run_select_exchange_prompt()


    def dont_drop_exchanges_table(self):
        self.remove_all_widgets()
        self.run_select_exchange_prompt()


    def submit_api_keys(self):
        pass


    def run_select_exchange_prompt(self):
        select_exchange_message = tk.Label(self, anchor='n', padx = 10, text=exchange_select_txt).pack(side="top")
        
        select_exchange_binance = tk.Button(self, command= lambda: self.choose_exchange('bina'))
        select_exchange_binance["text"] = "Binance"
        select_exchange_binance.pack(side="bottom")

        select_exchange_tux = tk.Button(self, command= lambda: self.choose_exchange('tux'))
        select_exchange_tux["text"] = "Tux"
        select_exchange_tux.pack(side="bottom")


    def choose_exchange(self, exchange):
        self.remove_all_widgets()
        self.exchange = exchange
        self.run_enter_api_key_info()


root = tk.Tk()
app = Application(master=root)
app.mainloop()