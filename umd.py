#! /usr/bin/env python3
# -*- coding: utf-8 -*-
########################################################################
# \file umd.py
# \author René Richard
# \brief This program allows to read and write to various game cartridges
#        including: Genesis, Coleco, SMS, PCE - with possibility for
#        future expansion.
########################################################################

# sudo apt install python3-tk
# sudo apt install python3-pil python3-pil.imagetk
# sudo apt install python-pip3
# pip3 install pyserial

import sys
import os
import glob
import serial
from io import TextIOWrapper
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import configparser
import subprocess

from PIL import Image, ImageTk
from core.configfile import ConfigFile
from core.hardware import UMDv2
from core.genesis import genesis
from core.sms import sms
from core.snes import snes


class AppUmd(Tk):

    hex_test = "0x000000 00 01 02 03 04 05 06 06 07 08 09 0A 0B 0C 0D 0E 0F\n"

    load_filename = ""

    configfile = ""
    umdv2 = ""

    # selected ports holds the IntVar() type, active_ports is boolean
    selected_ports = {}
    active_ports = {}

    cart_types = ["genesis", "sms", "snes", "tg16"]

    # ------------------------------------------------------------------------------------------------------------------
    #  __init__
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, conf, device, *args, **kwargs):

        # store config in this class
        self.configfile = conf
        self.umdv2 = device

        # declare main window
        Tk.__init__(self, *args, **kwargs)
        self.title("UMDv2")
        self.ico_load = tk.PhotoImage(file="res/db.gif")
        self.tk.call("wm", "iconphoto", self._w, self.ico_load)

        # create menus
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.menu_file = tk.Menu(self.menu)
        self.menu_file.add_command(label="Load ROM", command=self.load_rom)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Preferences", command=self.open_preferences)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.app_exit)
        self.menu.add_cascade(label="File", menu=self.menu_file)

        self.menu_help = tk.Menu(self.menu)
        self.menu_help.add_command(label="About", command=self.about_popup)
        self.menu.add_cascade(label="Help", menu=self.menu_help)

        # add elements to the window
        row = 0
        # two buttons inside the same drive element
        self.frm_buttons = tk.Frame(self)
        self.btn_loadrom = tk.Button(self.frm_buttons, text="Load ROM", command=self.load_rom).pack(side=LEFT)
        self.btn_connect_umd = Button(self.frm_buttons, text="Connect", command=self.connect_umd).pack(side=LEFT)
        self.frm_buttons.grid_propagate(False)
        self.frm_buttons.grid(row=row, column=0, padx=8, pady=4, sticky="nwe")

        # option menu for console selection
        row += 1
        self.frm_options = tk.Frame(self)
        menu_width = len(max(self.cart_types, key=len))
        self.lbl_consoles = tk.Label(self.frm_options, text="Cart Type")
        self.lbl_consoles.grid(row=0, column=0)
        self.var_consoles = tk.StringVar(self)
        self.var_consoles.set(self.configfile.read("CONSOLE", "last_selected"))
        self.opt_consoles = tk.OptionMenu(self.frm_options, self.var_consoles,
                                          *self.cart_types, command=self.select_console)
        self.opt_consoles.config(width=menu_width)
        self.opt_consoles.grid(row=1, column=0, sticky="w")

        self.frm_options.grid(row=row, column=0, padx=8, pady=4, sticky="nwe")

        # load an image for shits and giggles
        # self.img_load = Image.open("res/db-favicon.png")
        # self.render_dblogo = ImageTk.PhotoImage(self.img_load)
        # self.img_dblogo = Label(self, image=self.render_dblogo)
        # self.img_dblogo.image = self.render_dblogo
        # self.img_dblogo.grid(row=row, column=1, padx=4, pady=4, sticky=N+E)

        # entry box for sending commands to UMDv2
        row += 1
        self.lbl_output = tk.Label(self, text="Send Command")
        self.lbl_output.grid(row=row, padx=8, sticky="nw")
        row += 1
        self.entry_cmd = tk.Entry(self)
        self.entry_cmd.grid(row=row, padx=8, pady=4, sticky="wes")
        self.entry_cmd.bind("<Return>", self.send_txt_command)

        # message box + label for console output
        row += 1
        self.sep_console = tk.Frame(self, height=2, bd=10, relief=RAISED)
        self.sep_console.grid(row=row, sticky="we", padx=10)
        row += 1
        self.lbl_output = tk.Label(self, text="UMDv2 output")
        self.lbl_output.grid(row=row, padx=10, sticky="w")
        row += 1
        # create a frame for console output and scrollbar
        self.frm_console = tk.Frame(self)
        self.txt_output = tk.Text(self.frm_console, height=20, width=120)
        self.txt_output.config(bg="black", fg="green", font=("Courier", 10), padx=4, pady=4)
        self.txt_output.grid(row=0, column=0, padx=4, pady=4, sticky="nwes")
        self.scroll_txt = Scrollbar(self.frm_console, command=self.txt_output.yview)
        self.scroll_txt.grid(row=0, column=1, sticky="nwes")
        self.txt_output['yscrollcommand'] = self.scroll_txt.set
        self.frm_console.grid_rowconfigure(0, weight=1)
        self.frm_console.grid_columnconfigure(0, weight=1)
        self.frm_console.grid(row=row, padx=4, pady=4, sticky="nwes")

        # resize the frm_console on window resize
        self.columnconfigure(0, weight=1)
        self.rowconfigure(row, weight=1)

        # version number and info at the bottom
        row += 1
        self.lbl_listports = tk.Label(self, text="Available UMDv2 devices: ")
        self.lbl_listports.grid(row=row, column=0, padx=4, pady=4, sticky="w")
        row += 1
        self.frm_ports = tk.Frame(self)
        self.frm_ports.grid(row=row, padx=4, pady=4, sticky="nwes")

    # ------------------------------------------------------------------------------------------------------------------
    #  connect umd
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def connect_umd(self):
        self.umdv2.connect(self)
        self.selected_ports.clear()
        for widget in self.frm_ports.pack_slaves():
            widget.destroy()
        i = 0
        for port in self.umdv2.port:
            var = tk.IntVar()
            self.chk_port = tk.Checkbutton(self.frm_ports,
                                           text=port,
                                           variable=var,
                                           command=self.select_port)
            self.selected_ports[port] = var
            if i == 0:
                self.chk_port.select()
            self.chk_port.pack(side=LEFT)
            i += 1

        # add a few dummy ports
        for dummy in range(0, 3):
            var = tk.IntVar()
            port = "port" + str(dummy)
            self.chk_port = tk.Checkbutton(self.frm_ports,
                                           text=port,
                                           variable=var,
                                           command=self.select_port)
            self.selected_ports[port] = var
            self.chk_port.pack(side=LEFT)

    # ------------------------------------------------------------------------------------------------------------------
    #  select console
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def select_port(self):
        self.active_ports.clear()
        for key, value in self.selected_ports.items():
            print(key + " ", end='')
            state = self.selected_ports[key].get()
            print(str(state))
            self.active_ports[key] = bool(value.get())

    # ------------------------------------------------------------------------------------------------------------------
    #  select console
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def select_console(self, event):
        selected = self.var_consoles.get()
        self.configfile.modify("CONSOLE", "last_selected", selected)
        print(selected)

    # ------------------------------------------------------------------------------------------------------------------
    #  load_rom
    #
    #  load a ROM file, default to this console's ROM directory
    # ------------------------------------------------------------------------------------------------------------------
    def load_rom(self):
        initial_directory = self.configfile.read("ROMDIRECTORIES", self.var_consoles.get())
        self.load_filename = filedialog.askopenfilename(initialdir=initial_directory)
        if(len(self.load_filename)) > 0:
            print(self.load_filename)

    # ------------------------------------------------------------------------------------------------------------------
    #  write
    #  \param string
    #
    #  print to the console output and autoscroll
    # ------------------------------------------------------------------------------------------------------------------
    # def print_output(self, string):
    #    self.txt_output.configure(state="normal")
    #    self.txt_output.insert(END, string)
    #    self.txt_output.see(END)
    #    self.txt_output.configure(state="disabled")

    # ------------------------------------------------------------------------------------------------------------------
    #  send_txt_command
    #  \param event
    #
    #  Send a plain text command to the UMDv2
    # ------------------------------------------------------------------------------------------------------------------
    def send_txt_command(self, event):
        command = self.entry_cmd.get()
        if self.configfile.read("COMMAND", "clear_entry_on_send") == "yes":
            self.entry_cmd.delete(0, END)
        if self.configfile.read("COMMAND", "auto_append_lf") == "yes":
            print("sending : " + command)
        else:
            print("sending : " + command)

    # ------------------------------------------------------------------------------------------------------------------
    #  open preferences
    #
    #  open the preferences file in the platform's default app
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def open_preferences():
        try:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, "umd.conf"])
        except IOError:
            pass

    # ------------------------------------------------------------------------------------------------------------------
    #  app_exit
    #
    #  Retrieve the ROM's manufacturer flash ID
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def about_popup():
        messagebox.showinfo("About", "UMDv2 software and hardware designed by René Richard")

    # ------------------------------------------------------------------------------------------------------------------
    #  app_exit
    #
    #  Retrieve the ROM's manufacturer flash ID
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def app_exit():
        exit()


class RedirectOutput(TextIOWrapper):

    def __init__(self, txt_object):
        self.txt_output = txt_object

    def write(self, string):
        self.txt_output.configure(state="normal")
        self.txt_output.insert(END, string)
        self.txt_output.see(END)
        self.txt_output.configure(state="disabled")


# check for config file
configfile = ConfigFile("umd.conf")

# create umd
timeout = float(configfile.read("UMD", "timeout"))
umdv2 = UMDv2(timeout)
app = AppUmd(configfile, umdv2)

# redirect stdout to the console window in the GUI
redirector = RedirectOutput(app.txt_output)
sys.stdout = redirector

if configfile.read("UMD", "auto_connect_on_start") == "yes":
    app.connect_umd()

app.mainloop()

