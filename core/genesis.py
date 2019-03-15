#! /usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# \file  genesis.py
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

import os
import struct
from core.cartridge import Cartridge


# Genesis
#
#  All Genesis specific functions
class Genesis(Cartridge):

    # ------------------------------------------------------------------------------------------------------------------
    #  __init__
    #
    #  initialize - create a default cartridge
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, path=None):
        super().__init__(path)

        # override header attributes for Genesis
        self._header_address = 0x100
        self._header_size = 0x100
        self._header_dict = {}
        self.header = self.Header()

    # ------------------------------------------------------------------------------------------------------------------
    #  read_header
    #
    #  Read and format the ROM header for Sega Genesis cartridge
    # ------------------------------------------------------------------------------------------------------------------
    def read_header(self):

        # check if dealing with local ROM or remote ROM
        if self.file_path is not None:
            self.get_header_from_file()

        # clear current rom info dictionary
        self._header_dict.clear()
        # get console name
        self._header_dict.update({"Console Name": self._header_bytes[0:15].decode("utf-8", "replace")})
        # get copyright information
        self._header_dict.update({"Copyright": f.read(16).decode("utf-8", "replace")})

        with open(self.file_path, "rb") as f:
            f.seek(self._header_address, 0)
            # get console name
            self._header_dict.update({"Console Name": f.read(16).decode("utf-8", "replace")})
            # get copyright information
            self._header_dict.update({"Copyright": f.read(16).decode("utf-8", "replace")})
            # get domestic name
            self._header_dict.update({"Domestic Name": f.read(48).decode("utf-8", "replace")})
            # get overseas name
            self._header_dict.update({"Overseas Name": f.read(48).decode("utf-8", "replace")})
            # get serial number
            self._header_dict.update({"Serial Number": f.read(14).decode("utf-8", "replace")})
            # get checksum
            data = int.from_bytes(f.read(2), byteorder="big")
            self._header_dict.update({"Checksum": [data, hex(data)]})
            # get io support
            self._header_dict.update({"IO Support": f.read(16).decode("utf-8", "replace")})
            # get ROM Start Address
            data = int.from_bytes(f.read(4), byteorder="big")
            self._header_dict.update({"ROM Begin": [data, hex(data)]})
            # get ROM End Address
            data = int.from_bytes(f.read(4), byteorder="big")
            self._header_dict.update({"ROM End": [data, hex(data)]})
            # get Start of RAM
            data = int.from_bytes(f.read(4), byteorder="big")
            self._header_dict.update({"RAM Begin": [data, hex(data)]})
            # get End of RAM
            data = int.from_bytes(f.read(4), byteorder="big")
            self._header_dict.update({"RAM End": [data, hex(data)]})
            # get sram support
            self._header_dict.update({"SRAM Support": f.read(4)})
            # get start of sram
            data = int.from_bytes(f.read(4), byteorder="big")
            self._header_dict.update({"SRAM Begin": [data, hex(data)]})
            # get end of sram
            data = int.from_bytes(f.read(4), byteorder="big")
            self._header_dict.update({"SRAM End": [data, hex(data)]})
            # get modem support
            self._header_dict.update({"Modem Support": f.read(12).decode("utf-8", "replace")})
            # get memo
            self._header_dict.update({"Memo": f.read(40).decode("utf-8", "replace")})
            # get country support
            self._header_dict.update({"Country Support": f.read(16).decode("utf-8", "replace")})

            return self._header_dict

    #  Header class for proper formatting and addresses
    class Header:

        # ------------------------------------------------------------------------------------------------------------------
        #  __init__
        #
        #  initialize - data offsets and conversion types for Header
        # ------------------------------------------------------------------------------------------------------------------
        def __init__(self):
            self._indexes = {
                "Console Name ": [0x100, 16, "str"],  # name, {address, size, type}
                "Copyright    ": [0x110, 16, "str"],
                "Domestic Name": [0x120, 48, "str"],
                "Overseas Name": [0x150, 48, "str"],
                "Serial Number": [0x180, 14, "str"],
                "Checksum     ": [0x18E, 2, "bintx"],
                "IO Support   ": [0x190, 16, "str"],
                "ROM Begin    ": [0x1A0, 4, "bintx"],
                "ROM End      ": [0x1A4, 4, "bintx"],
                "RAM Begin    ": [0x1A8, 4, "bintx"],
                "RAM End      ": [0x1AC, 4, "bintx"],
                "SRAM Support ": [0x1B0, 4, "bytes"],
                "SRAM Begin   ": [0x1B4, 4, "bintx"],
                "SRAM End     ": [0x1B8, 4, "bintx"],
                "Modem Support": [0x1BC, 12, "str"],
                "Memo         ": [0x1C8, 40, "str"],
                "Region       ": [0x1F0, 16, "str"],
            }

        @property
        def indexes(self):
            return self._indexes





