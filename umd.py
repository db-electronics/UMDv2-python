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
# sudo apt install python-pip3
# pip3 install pyserial

import sys
import os
import glob
import serial
import threading
from io import TextIOWrapper
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import configparser
import subprocess

from core.cartridge import Cartridge
from core.configfile import ConfigFile
from core.hardware import UMDv2
from core.genesis import Genesis
from core.sms import sms
from core.snes import snes


class AppUmd(Tk):

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

        console_menu_width = len(max(self.cart_types, key=len))
        button_width = 9

        # declare main window
        Tk.__init__(self, *args, **kwargs)
        self.title("UMDv2")
        self.ico_load = tk.PhotoImage(file="res/db.gif")
        self.tk.call("wm", "iconphoto", self._w, self.ico_load)

        # create menus
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.menu_file = tk.Menu(self.menu)
        self.menu_file.add_command(label="Select ROM", command=self.select_rom)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Preferences", command=self.open_preferences)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit",
                                   command=self.app_exit)
        self.menu.add_cascade(label="File", menu=self.menu_file)

        self.menu_help = tk.Menu(self.menu)
        self.menu_help.add_command(label="About",
                                   command=lambda: messagebox.showinfo("About",
                                                                       "UMDv2 software and hardware designed by René Richard"))
        self.menu.add_cascade(label="Help", menu=self.menu_help)

        # add elements to the window
        row = 0
        self.lbl_romtasks = tk.Label(self, text="ROM Tasks")
        self.lbl_romtasks.grid(row=row, column=0, columnspan=2, padx=8, pady=4, sticky="w")
        row += 1
        # buttons for local ROM tasks
        self.frm_romtasks = tk.Frame(self)
        self.var_romconsole = tk.StringVar(self)
        self.var_romconsole.set(self.configfile.read("CONSOLE", "last_selected"))
        self.opt_romconsole = tk.OptionMenu(self.frm_romtasks,
                                            self.var_romconsole,
                                            *self.cart_types,
                                            command=self.select_console)
        self.opt_romconsole.config(width=console_menu_width)
        self.opt_romconsole.pack(side=LEFT)
        self.btn_loadrom = tk.Button(self.frm_romtasks,
                                     text="Select ROM",
                                     width=button_width,
                                     command=self.select_rom).pack(side=LEFT)
        self.btn_md5 = Button(self.frm_romtasks,
                              text="MD5",
                              width=button_width,
                              command=self.calc_md5).pack(side=LEFT)
        self.btn_md5 = Button(self.frm_romtasks,
                              text="Header",
                              width=button_width,
                              command=self.read_header).pack(side=LEFT)
        self.frm_romtasks.grid_propagate(False)
        self.frm_romtasks.grid(row=row, column=0, padx=8, pady=4, sticky="nwe")
        row += 1
        self.var_selectedrom = StringVar()
        self.lbl_currentrom = tk.Label(self, textvariable=self.var_selectedrom)
        self.lbl_currentrom.grid(row=row, column=0, padx=8, pady=4, sticky="w")

        # check if there is a last_rom in the config gile
        check_last = self.configfile.read("FILES", "last_rom")
        if len(check_last) > 0:
            self.var_selectedrom.set(check_last)

        # buttons for remote UMD tasks
        row += 1
        self.sep_console = tk.Frame(self, height=2, bd=10, relief=RAISED)
        self.sep_console.grid(row=row, column=0, columnspan=2, sticky="we", padx=10)
        row += 1
        self.lbl_umdtasks = tk.Label(self, text="UMD Tasks")
        self.lbl_umdtasks.grid(row=row, column=0, padx=8, pady=4, sticky="w")
        row += 1
        self.frm_umdtasks = tk.Frame(self)

        self.btn_connect_umd = Button(self.frm_umdtasks,
                                      text="Connect",
                                      width=button_width,
                                      command=self.connect_umd).pack(side=LEFT)

        self.frm_umdtasks.grid(row=row, column=0, padx=8, pady=4, sticky="nwe")

        # entry box for sending commands to UMDv2
        row += 1
        self.sep_console = tk.Frame(self, height=2, bd=10, relief=RAISED)
        self.sep_console.grid(row=row, column=0, columnspan=2, sticky="we", padx=10)
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
        self.lbl_output.grid(row=row, padx=10, pady=8, sticky="w")
        row += 1
        # create a frame for console output and scrollbar
        self.frm_console = tk.Frame(self)
        self.txt_output = tk.Text(self.frm_console, height=20, width=120)
        self.txt_output.config(bg="black", fg="cyan", font=("Courier", 10), padx=4, pady=4)
        self.txt_output.grid(row=0, column=0, padx=4, pady=4, sticky="nwes")
        self.scroll_txt = Scrollbar(self.frm_console, command=self.txt_output.yview)
        self.scroll_txt.grid(row=0, column=1, sticky="nwes")
        self.txt_output['yscrollcommand'] = self.scroll_txt.set
        self.frm_console.grid_rowconfigure(0, weight=1)
        self.frm_console.grid_columnconfigure(0, weight=1)
        self.frm_console.grid(row=row, column=0, columnspan=2, padx=4, pady=4, sticky="nwes")

        # resize the frm_console on window resize
        self.columnconfigure(0, weight=1)
        self.rowconfigure(row, weight=1)

        # version number and info at the bottom
        row += 1
        self.lbl_listports = tk.Label(self, text="Available UMDv2 devices: ")
        self.lbl_listports.grid(row=row, column=0, padx=8, pady=4, sticky="w")
        self.btn_clroutput = tk.Button(self,
                                       text="Clear",
                                       width=button_width,
                                       command=self.clear_output)
        self.btn_clroutput.grid(row=row, column=1, padx=8, pady=4, sticky="e")
        row += 1
        self.frm_ports = tk.Frame(self)
        self.frm_ports.grid(row=row, padx=4, pady=4, sticky="nwes")

    # ------------------------------------------------------------------------------------------------------------------
    #  connect umd
    #
    #  start a background thread to connect to the UMD
    # ------------------------------------------------------------------------------------------------------------------
    def connect_umd(self):
        def callback():
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
            # for dummy in range(0, 3):
            #     var = tk.IntVar()
            #     port = "port" + str(dummy)
            #     self.chk_port = tk.Checkbutton(self.frm_ports,
            #                                    text=port,
            #                                    variable=var,
            #                                    command=self.select_port)
            #     self.selected_ports[port] = var
            #     self.chk_port.pack(side=LEFT)
        thread = threading.Thread(target=callback)
        thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    #  select console
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def read_header(self):
        file_path = self.var_selectedrom.get()
        console = self.var_romconsole.get()
        if len(file_path) > 0:
            if console == "genesis":
                rom = Genesis(file_path)

            try:
                rom.format_header()
            except UnboundLocalError:
                print("{} read_header unimplemented".format(console))

        else:
            messagebox.showwarning("Warning", "You must load a ROM before performing this operation")

    # ------------------------------------------------------------------------------------------------------------------
    #  select console
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def calc_md5(self):
        filepath = self.var_selectedrom.get()
        if len(filepath) > 0:
            rom = Cartridge(filepath)
            rom.md5()
            print("MD5 sum of {} is {}".format(os.path.basename(filepath), rom.md5_hex_str))
            del rom
        else:
            messagebox.showwarning("Warning", "You must load a ROM before performing this operation")

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
        selected = self.var_romconsole.get()
        self.configfile.modify("CONSOLE", "last_selected", selected)

    # ------------------------------------------------------------------------------------------------------------------
    #  select_rom
    #
    #  select a ROM file, default to this console's ROM directory
    # ------------------------------------------------------------------------------------------------------------------
    def select_rom(self):
        initial_directory = self.configfile.read("ROMDIRECTORIES", self.var_romconsole.get())
        selection = filedialog.askopenfilename(initialdir=initial_directory)
        if len(selection) > 0:
            self.var_selectedrom.set(selection)
            self.configfile.modify("FILES", "last_rom", selection)

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
    #  send_txt_command
    #  \param event
    #
    #  Send a plain text command to the UMDv2
    # ------------------------------------------------------------------------------------------------------------------
    def clear_output(self):
        self.txt_output.configure(state="normal")
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.configure(state="disabled")

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

    def __repr__(self):
        pass


# ------------------------------------------------------------------------------------------------------------------
#  main
#
#  main application
# ------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # execute only if run as a script

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

