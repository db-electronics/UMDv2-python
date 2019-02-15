#! /usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# \file  cartridge.py
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
import hashlib


#  Cartridge
#
#  A generic cartridge class to handle common operations for all ROM/cartridge types
class Cartridge:

    md5_hex_str = None
    md5_bytes = None

    # ------------------------------------------------------------------------------------------------------------------
    #  __init__
    #
    #  initialize - create a default cartridge
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, path=None):
        self.filepath = path
        pass

    # ------------------------------------------------------------------------------------------------------------------
    #  md5
    #
    #  calculate the md5 sum of the ROM
    # ------------------------------------------------------------------------------------------------------------------
    def md5(self):
        if self.filepath is not None:
            hash_md5 = hashlib.md5()
            with open(self.filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            # packed bytes
            self.md5_bytes = hash_md5.digest()
            # hex string
            self.md5_hex_str = hash_md5.hexdigest()
            return hash_md5.digest()
        else:
            print("No file path specified for source file")

    # ------------------------------------------------------------------------------------------------------------------
    #  apply_ips
    #
    #  apply an ips patch to the ROM
    # ------------------------------------------------------------------------------------------------------------------
    def apply_ips(self, ips_file):
        # https://ipsy.readthedocs.io/en/latest/#ips-file-format
        pass
