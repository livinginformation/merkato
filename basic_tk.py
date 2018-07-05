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


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()


    def create_widgets(self):

        self.welcome_message = tk.Label(self, anchor='n', padx = 10, text=welcome_txt).pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red", command=root.destroy)
        self.quit.pack(side="bottom")

        self.create_new = tk.Button(self, command=self.start_create_frame)
        self.create_new["text"] = "Create New Merk/Exc"
        self.create_new.pack(side="bottom")
      
        self.run_merkatos = tk.Button(self, command=self.start_simple_app)
        self.run_merkatos["text"] = "Run Merkatos"
        self.run_merkatos.pack(side="bottom")


    def start_create_frame(self):
        self.remove_all_widgets()
        self.run_remove_tables_prompts()
    

    def start_simple_app(self):
        self.remove_all_widgets()


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
        self.drop_merkatos_message = tk.Label(self, anchor='n', padx = 10, text=drop_merkatos_txt).pack(side="top")
        
        self.drop_merkatos = tk.Button(self, command=self.drop_merkatos_table)
        self.drop_merkatos["text"] = "Yes"
        self.drop_merkatos.pack(side="bottom")
      
        self.dont_drop_merkatos = tk.Button(self, command=self.dont_drop_merkatos_table)
        self.dont_drop_merkatos["text"] = "No"
        self.dont_drop_merkatos.pack(side="bottom")


    def run_remove_exchanges_prompts(self):
        self.drop_merkatos_message = tk.Label(self, anchor='n', padx = 10, text=drop_exchanges_txt).pack(side="top")

        self.drop_exchanges = tk.Button(self, command=self.drop_exchanges_table)
        self.drop_exchanges["text"] = "Yes"
        self.drop_exchanges.pack(side="bottom")
      
        self.dont_drop_exchanges = tk.Button(self, command=self.dont_drop_exchanges_table)
        self.dont_drop_exchanges["text"] = "No"
        self.dont_drop_exchanges.pack(side="bottom")


    def run_enter_api_key_info(self):
        self.public_key_field = tk.Entry(self, width=40)
        self.private_key_field = tk.Entry(self, width=40)

        self.private_key_message = tk.Label(self, anchor='n', padx = 10, text=private_key_text)
        self.public_key_message = tk.Label(self, anchor='n', padx = 10, text=public_key_text)

        self.submit_keys = tk.Button(self, command=self.submit_api_keys)
        self.submit_keys["text"] = "Submit keys"

        self.public_key_field.pack(side="top")
        self.public_key_message.pack(side="top")

        self.private_key_field.pack(side="top")
        self.private_key_message.pack(side="top")

        self.submit_keys.pack(side="bottom")


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
        self.run_enter_api_key_info()


    def dont_drop_exchanges_table(self):
        self.remove_all_widgets()
        self.run_enter_api_key_info()


    def submit_api_keys(self):
        pass


root = tk.Tk()
app = Application(master=root)
app.mainloop()