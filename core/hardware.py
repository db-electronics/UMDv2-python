#! /usr/bin/env python3
# -*- coding: utf-8 -*-
########################################################################
# \file  hardware.py
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

import sys
import glob
import serial


## Universal Mega Dumper
#
#  All communications with the UMD are handled by the umd class
class umdv2:

    timeout = 0
    port = {}

    # ------------------------------------------------------------------------------------------------------------------
    #  __init__
    #
    #  select a local file
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, timeout):
        self.timeout = timeout
        pass

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
    def connect(self, app):
        app.print_output("autodecting UMDv2...\n")
        umd_ports = []
        self.port.clear()
        check_ports = self.list_serial_ports()
        if len(check_ports) == 0:
            app.print_output("no active serial ports detected, please connect a UMDv2 to the PC and press 'Connect'\n")
            pass
        else:
            for port in check_ports:
                app.print_output("attempting to connect to UMDv2 on " + port + " : ")
                try:
                    ser = serial.Serial(port=port,
                                        baudrate=460800,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        timeout=self.timeout)
                    ser.write(bytes("flash\n", "utf-8"))
                    response = ser.readline().decode("utf-8")
                    if response == "flash\n":
                        app.print_output("present!\n")
                        umd_ports.append(port)
                    else:
                        app.print_output("timed out\n")
                        pass
                    ser.close()
                    app.txt_output.update()
                except (OSError, serial.SerialException):
                    pass

            # add all discovered ports to the
            for port in umd_ports:
                self.port[port] = serial.Serial(port=port,
                                                baudrate=460800,
                                                bytesize=serial.EIGHTBITS,
                                                parity=serial.PARITY_NONE,
                                                stopbits=serial.STOPBITS_ONE,
                                                timeout=self.timeout)
