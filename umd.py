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
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import configparser
import subprocess

from PIL import Image, ImageTk
from core.configfile import configfile
from core.hardware import umddb
from core.genesis import genesis
from core.sms import sms
from core.snes import snes


class appUmd(Tk):

    hex_test = "0x000000 00 01 02 03 04 05 06 06 07 08 09 0A 0B 0C 0D 0E 0F\n"

    umd_ports = []
    load_filename = ""

    configfile = ""

    cart_types = ["genesis", "sms", "snes", "tg16"]

    # ------------------------------------------------------------------------------------------------------------------
    #  __init__
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, conf, *args, **kwargs):

        # store config in this class
        self.configfile = conf

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

        #self.about_menu

        # add elements to the window
        row = 0
        # two buttons inside the same drive element
        self.frm_buttons = tk.Frame(self)
        self.btn_loadrom = tk.Button(self.frm_buttons, text="Load ROM", command=self.load_rom).pack(side=LEFT)
        self.btn_connect_umd = Button(self.frm_buttons, text="Connect", command=self.connect_umd).pack(side=LEFT)
        self.frm_buttons.grid_propagate(False)
        self.frm_buttons.grid(row=row, column=0, padx=8, pady=4, sticky="nwe")

        # option menu for console selection
        row = row + 1
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
        row = row + 1
        self.lbl_output = tk.Label(self, text="Send Command")
        self.lbl_output.grid(row=row, padx=8, sticky="nw")
        row = row + 1
        self.entry_cmd = tk.Entry(self)
        self.entry_cmd.grid(row=row, padx=8, pady=4, sticky="wes")
        self.entry_cmd.bind("<Return>", self.send_txt_command)

        # message box + label for console output
        row = row + 1
        self.sep_console = tk.Frame(self, height=2, bd=10, relief=RAISED)
        self.sep_console.grid(row=row, sticky="we", padx=10)
        row = row + 1
        self.lbl_output = tk.Label(self, text="UMDv2 output")
        self.lbl_output.grid(row=row, padx=10, sticky="w")
        row = row + 1
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
        row = row + 1
        self.frm_status = tk.Frame(self)
        self.lbl_cart = tk.Label(self.frm_status, text="File: ")
        self.lbl_cart.grid(row=0, column=0, padx=4, pady=4, sticky="we")
        self.lbl_output = tk.Label(self.frm_status, text="UMDv2 version 2.0.0.0")
        self.lbl_output.grid(row=0, column=1, padx=4, pady=4, sticky="we")
        self.frm_status.grid(row=row, padx=4, pady=4, sticky="nwes")

    # ------------------------------------------------------------------------------------------------------------------
    #  select console
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def select_console(self, event):
        selected = self.var_consoles.get()
        self.configfile.modify("CONSOLE", "last_selected", selected)
        self.print_output(selected + "\n")
        pass

    # ------------------------------------------------------------------------------------------------------------------
    #  open preferences
    #
    #  open the preferences file in the platform's default app
    # ------------------------------------------------------------------------------------------------------------------
    def open_preferences(self):
        try:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, "umd.conf"])
        except IOError:
            pass

    # ------------------------------------------------------------------------------------------------------------------
    #  load_rom
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def load_rom(self):
        initial_directory = self.configfile.read("ROMDIRECTORIES", self.var_consoles.get())
        self.load_filename = filedialog.askopenfilename(initialdir=initial_directory)
        if(len(self.load_filename)) > 0:
            self.print_output(self.load_filename + "\n")

    # ------------------------------------------------------------------------------------------------------------------
    #  app_exit
    #
    #  Retrieve the ROM's manufacturer flash ID
    # ------------------------------------------------------------------------------------------------------------------
    def app_exit(self):
        exit()

    # ------------------------------------------------------------------------------------------------------------------
    #  app_exit
    #  \param string
    #
    #  print to the console output and autoscroll
    # ------------------------------------------------------------------------------------------------------------------
    def print_output(self, string):
        self.txt_output.configure(state="normal")
        self.txt_output.insert(END, string)
        self.txt_output.see(END)
        self.txt_output.configure(state="disabled")

    # ------------------------------------------------------------------------------------------------------------------
    #  list_serial_ports
    #
    #  List the platform's available serial ports on which the UMDv2 may be connected
    # ------------------------------------------------------------------------------------------------------------------
    def list_serial_ports(self):
        # enumerate ports
        if sys.platform.startswith("win"):
            ports = ["COM%s" % (i + 1) for i in range(256)]
        elif sys.platform.startswith("linux"):
            ports = glob.glob("/dev/ttyA[A-Za-z]*")
        elif sys.platform.startswith("darwin"):
            ports = glob.glob("/dev/cu*")
        else:
            raise EnvironmentError("Unsupported platform")

        return ports

    # ------------------------------------------------------------------------------------------------------------------
    #  connect_umd
    #
    #  Attempt to connect to all UMDv2 connected to the computer
    # ------------------------------------------------------------------------------------------------------------------
    def connect_umd(self):
        self.print_output("autodecting UMDv2...\n")
        check_ports = self.list_serial_ports()
        if len(check_ports) == 0:
            self.print_output("no active serial ports detected, please connect a UMDv2 to the PC and press 'Connect'\n")
            pass
        else:
            for port in check_ports:
                self.print_output("attempting to connect to UMDv2 on " + port + " : ")
                try:
                    ser = serial.Serial(port=port,
                                        baudrate=460800,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        timeout=0.5)
                    ser.write(bytes("flash\n", "utf-8"))
                    response = ser.readline().decode("utf-8")
                    if response == "flash\n":
                        self.print_output("present!\n")
                        self.umd_ports.append(port)
                    else:
                        self.print_output("timed out\n")
                        pass
                    ser.close()
                    self.txt_output.update()
                except (OSError, serial.SerialException):
                    pass

    # ------------------------------------------------------------------------------------------------------------------
    #  send_txt_command
    #  \param event
    #
    #  Send a plain text command to the UMDv2
    # ------------------------------------------------------------------------------------------------------------------
    def send_txt_command(self, event):
        command = self.entry_cmd.get()
        self.print_output("sending : " + command + "\n")
        pass


# check for config file
configfile = configfile("umd.conf")

app = appUmd(configfile)

if configfile.read("UMD", "auto_connect_on_start") == "yes":
    app.connect_umd()

app.mainloop()

