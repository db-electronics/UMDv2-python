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
#  all console types inherit from this class
#  all rom function from child classes should operate on bytes and not files
class Cartridge:

    # ------------------------------------------------------------------------------------------------------------------
    #  __init__
    #
    #  initialize - create a default cartridge
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, path=None):
        self.file_path = path
        self._header_address = None
        self._header_size = None
        self._md5_hex_str = None
        self._md5_bytes = None
        self._header_bytes = None

    @property
    def header_address(self):
        return self._header_address

    @property
    def header_size(self):
        return self._header_size

    @property
    def md5_bytes(self):
        return self._md5_bytes

    @property
    def md5_hex_str(self):
        return self._md5_hex_str

    # ------------------------------------------------------------------------------------------------------------------
    #  get_header_from_file
    #
    #  extract the header portion of a ROM file
    # ------------------------------------------------------------------------------------------------------------------
    def get_header_from_file(self):
        with open(self.file_path, "rb") as f:
            f.seek(self.header_address, 0)
            self._header_bytes = f.read(self.header_size)

    # ------------------------------------------------------------------------------------------------------------------
    #  get_header_from_file
    #
    #  extract the header portion of a ROM file
    # ------------------------------------------------------------------------------------------------------------------
    def format_header(self):

        formatted = {}
        # check if dealing with local ROM or remote ROM
        if self.file_path is not None:
            self.get_header_from_file()

        for key, value in self.header.indexes.items():
            #print("{} {}".format(key, value))
            start = value[0] - self._header_address
            finish = start + (value[1])
            chunk = self._header_bytes[start:finish]
            if value[2] == "str":
                out = chunk.decode("utf-8", "replace")
            elif value[2] == "int":
                out = int.from_bytes(chunk, byteorder="small")
            elif value[2] == "intx":
                out = hex(int.from_bytes(chunk, byteorder="small"))
            elif value[2] == "bint":
                out = int.from_bytes(chunk, byteorder="big")
            elif value[2] == "bintx":
                out = hex(int.from_bytes(chunk, byteorder="big"))
            elif value[2] == "bytes":
                out = ""
                for b in chunk:
                    # "{value:#0{padding}x}"
                    out += "{0:#0{1}x} ".format(b,4)
            elif value[2] == "bits":
                out = ""
                for b in chunk:
                    out += "{:#010b} ".format(b)
            else:
                out = chunk
            print("{} : {}".format(key, out))

    # ------------------------------------------------------------------------------------------------------------------
    #  md5
    #
    #  calculate the md5 sum of the ROM
    # ------------------------------------------------------------------------------------------------------------------
    def md5(self):
        if self.file_path is not None:
            hash_md5 = hashlib.md5()
            with open(self.file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            # packed bytes
            self._md5_bytes = hash_md5.digest()
            # hex string
            self._md5_hex_str = hash_md5.hexdigest()
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
