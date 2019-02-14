#! /usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# \file  configfile.py
# \author René Richard
# \brief This program allows to read and write to various game cartridges
#        including: Genesis, Coleco, SMS, PCE - with possibility for
#        future expansion.
########################################################################
# \copyright This file is part of Universal Mega Dumper.
#
#   Universal Mega Dumper is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Universal Mega Dumper is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Universal Mega Dumper.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

# https://docs.python.org/3/library/configparser.html
import sys
import configparser

#  configfile
#
#  All Genesis specific functions
class configfile:

    path = ""

    # ------------------------------------------------------------------------------------------------------------------
    #  __init__
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, path):
        try:
            with open(path) as f:
                # read in the settings
                pass
        except IOError:
            self.create_default(path)

        self.path = path

    # ------------------------------------------------------------------------------------------------------------------
    #  create_default
    #
    #  create a default configuration file
    # ------------------------------------------------------------------------------------------------------------------
    def create_default(self, path):

        # create a generic conf file if none is found
        config = configparser.ConfigParser()
        config["UMD"] = {"auto_connect_on_start": "yes",
                         "last_port": "",
                         "timeout": "0.5"}
        config["COMMAND"] = {"clear_entry_on_send": "yes",
                             "auto_append_lf": "yes"}
        config["CONSOLE"] = {"last_selected": "genesis"}

        if sys.platform.startswith("win"):
            pass
        elif sys.platform.startswith("linux"):
            config["ROMDIRECTORIES"] = {"genesis": "~/ROMs/genesis",
                                        "sms": "~/ROMs/sms",
                                        "snes": "~/ROMs/snes",
                                        "tg16": "~/ROMs/tg16"}
        elif sys.platform.startswith("darwin"):
            pass
        else:
            pass

        with open(path, "w") as f:
            config.write(f)

    # ------------------------------------------------------------------------------------------------------------------
    #  modify
    #
    #  modify an option in the config file
    # ------------------------------------------------------------------------------------------------------------------
    def modify(self, section, option, value):
        try:
            with open(self.path) as f:
                pass
        except IOError:
            self.create_default(self.path)

        config = configparser.ConfigParser()
        config.read(self.path)
        config[section][option] = value

        with open(self.path, "w") as f:
            config.write(f)

    # ------------------------------------------------------------------------------------------------------------------
    #  read
    #
    #  return the config file, create a default if there is no file found
    # ------------------------------------------------------------------------------------------------------------------
    def read(self, section, option):
        try:
            with open(self.path) as f:
                pass
        except IOError:
            self.create_default(self.path)

        config = configparser.ConfigParser()
        config.read(self.path)
        return config[section][option]

