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

    checksumRom = 0
    checksumCalc = 0
    
    header_address = 0x100
    headerChecksum = 0x18E
    headerSize = 0x100
    header_dict = {}
    romStartAddress = 0x200
    
    readChunkSize = 2048

########################################################################    
## byteSwap(self, ifile, ofile):
#  \param self self
#  \param ifile
#  \param ofile
#
########################################################################
    def byteSwap(self, ifile, ofile):
        
        fileSize = os.path.getsize(ifile)
        pos = 0
        
        try:
            os.remove(ofile)
        except OSError:
            pass
            
        with open(ofile, "wb+") as fwrite:
            with open(ifile, "rb") as fread:
                while(pos < fileSize):  
                    badEndian = fread.read(2)
                    revEndian = struct.pack('<h', *struct.unpack('>h', badEndian))
                    fwrite.write(revEndian)
                    pos += 2

########################################################################    
## checksum(self, file):
#  \param self self
#  \param file the rom to verify
#
########################################################################
    def checksum(self):
        
        # Genesis checksums start after the header
        pos = self.romStartAddress
        self.checksumCalc = 0
        fileSize = os.path.getsize(self.filepath)
        
        with open(self.filepath, "rb") as f:
            
            # read the ROM header's checksum value

            f.seek(self.headerChecksum, 0)
            data = f.read(2)
            thisWord = data[0],data[1]
            self.checksumRom = int.from_bytes(thisWord, byteorder="big")
            
            # jump ahead of ROM header
            f.seek(self.romStartAddress, 0)
            
            while( pos < fileSize ):
                if( ( fileSize - pos ) >= self.readChunkSize):
                    sizeOfRead = self.readChunkSize
                else:
                    sizeOfRead = ( fileSize - pos )
                    
                data = f.read(sizeOfRead)
                
                i = 0
                while i < sizeOfRead and i+1 < sizeOfRead:
                    thisWord = data[i],data[i + 1]
                    intVal = int.from_bytes(thisWord, byteorder="big")
                    self.checksumCalc = (self.checksumCalc + intVal) & 0xFFFF
                    i += 2 
                
                pos += sizeOfRead

########################################################################    
## readGenesisROMHeader
#  \param self self
#  
#  Read and format the ROM header for Sega Genesis cartridge
########################################################################
    def read_header(self):
        
        # clear current rom info dictionnary
        self.header_dict.clear()
        with open(self.filepath, "rb") as f:

            f.seek(self.header_address, 0)
            # get console name
            self.header_dict.update({"Console Name": f.read(16).decode("utf-8", "replace")})
            # get copyright information
            self.header_dict.update({"Copyright": f.read(16).decode("utf-8", "replace")})
            # get domestic name
            self.header_dict.update({"Domestic Name": f.read(48).decode("utf-8", "replace")})
            # get overseas name
            self.header_dict.update({"Overseas Name": f.read(48).decode("utf-8", "replace")})
            # get serial number
            self.header_dict.update({"Serial Number": f.read(14).decode("utf-8", "replace")})
            # get checksum
            data = int.from_bytes(f.read(2), byteorder="big" )
            self.header_dict.update({"Checksum": [data, hex(data)]})
            # get io support
            self.header_dict.update({"IO Support": f.read(16).decode("utf-8", "replace")})
            # get ROM Start Address
            data = int.from_bytes(f.read(4), byteorder="big" )
            self.header_dict.update({"ROM Begin": [data, hex(data)]})
            # get ROM End Address
            data = int.from_bytes(f.read(4), byteorder="big" )
            self.header_dict.update({"ROM End": [data, hex(data)]})
            # get Start of RAM
            data = int.from_bytes(f.read(4), byteorder="big" )
            self.header_dict.update({"RAM Begin": [data, hex(data)]})
            # get End of RAM
            data = int.from_bytes(f.read(4), byteorder="big" )
            self.header_dict.update({"RAM End": [data, hex(data)]})
            # get sram support
            self.header_dict.update({"SRAM Support": f.read(4)})
            # get start of sram
            data = int.from_bytes(f.read(4), byteorder="big" )
            self.header_dict.update({"SRAM Begin": [data, hex(data)]})
            # get end of sram
            data = int.from_bytes(f.read(4), byteorder="big" )
            self.header_dict.update({"SRAM End": [data, hex(data)]})
            # get modem support
            self.header_dict.update({"Modem Support": f.read(12).decode("utf-8", "replace")})
            # get memo
            self.header_dict.update({"Memo": f.read(40).decode("utf-8", "replace")})
            # get country support
            self.header_dict.update({"Country Support": f.read(16).decode("utf-8", "replace")})

            return self.header_dict

