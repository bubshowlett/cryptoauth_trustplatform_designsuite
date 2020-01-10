from .sys_helper import sys_helper
from .path_helper import path_helper
from pathlib import Path
import hid
import sys, os
import json

nEDBG_DEBBUGER_PID        = 8565   #0x2175
CRYPTO_TRUST_PLATFORM_PID = 8978   #0x2312
VENDOR_ID                 = 1003   #0x03EB

class program_flash():
    """
    Class with methods which help with wrappers and
    helpers for flash hex file into CryptoAuth Trust Platform board
    """
    def __init__(self):
        self.jar_loc = None

    def get_jar_loc(self):
        """
        Function which fetch the jar location and store it in self.jar_loc
        """
        homepath = path_helper.get_home_path()
        filename = str(Path(os.path.join(homepath, "trustplatform_config.json")))
        with open(filename, 'r') as file:
            data = json.load(file)
        self.jar_loc = data["MPLABX"]["ipe_path"]
    
    def check_mplab_path(self):
        """
        Function which checks the mplab ipe path is present or not
        
        Outputs:
               Returns True or False
               True            mplab ipe path set
               False           mplab ipe path not set
        """
        homepath = path_helper.get_home_path()
        filename = str(Path(os.path.join(homepath, "trustplatform_config.json")))
        with open(filename, 'r') as file:
            data = json.load(file)
        
        def_val = data["MPLABX"]["path_set"]
        if def_val.lower() == "true":
            return True
        else:
            return False

    @staticmethod
    def check_debugger_info():
        """
        Function which check the nEDBG CMSIS-DAP debugger connected or not

        Outputs:
               Returns a list of ["path", "vendor_id", "product_id", "serial_number", "manufacturer_string", product_string", "interafce_number"]

               vendor_id                vendor id
               product_id               product id
               serial_number            product serial number
               manufacturer_string      product manufacturer name
               product_string           product name
               interface_number         interface number 
        """
        debugger_info = hid.enumerate(VENDOR_ID, nEDBG_DEBBUGER_PID)
        return debugger_info

    @staticmethod
    def check_firmware_info():
        """
        Function which check the firmware info whether Factory reset program flashed or not

        Outputs:
               Returns a list of ["path", "vendor_id", "product_id", "serial_number", "manufacturer_string", product_string", "interafce_number"]

               vendor_id                vendor id
               product_id               product id
               serial_number            product serial number
               manufacturer_string      product manufacturer name
               product_string           product name
               interface_number         interface number 
        """
        firmware_info = hid.enumerate(VENDOR_ID, CRYPTO_TRUST_PLATFORM_PID)
        return firmware_info

    def flash_micro(self, hexfile_path):
        """
        Function which flash the hex file into crypto trust platform board by executing command
        
        Examples:
            To flash hex file "java -jar "C:\\Program Files (x86)\\Microchip\\MPLABX\\v5.30\\mplab_platform\\mplab_ipe\\ipecmd.jar"
                                          -PATSADM21E18A -TPPKOB -ORISWD -OL -M -F"cryptoauth_trust_platform.hex"
        Inputs:
              hexfile_path             Hex file which will be flashed into CryptoAuth Trust Platform

        Outputs:
               Returns a namedtuple of ['returncode', 'stdout', 'stderr']

               returncode              Returns error code from terminal
               stdout                  All standard outputs are accumulated here. 
               srderr                  All error and warning outputs 
        """
        self.get_jar_loc()
        subprocessout = sys_helper.run_subprocess_cmd(cmd=["java", "-jar", self.jar_loc, "-PATSAMD21E18A", "-TPPKOB", "-OL", "-M", ("-F"+str(Path(hexfile_path)))])
        return subprocessout

    def check_for_factory_program(self, firm_valid=False):
        """
        Function which check whether the proper device connected or not, if connected which flash default factory reset image 

        Outputs: 
              Returns true or error message
              True               when default factory reset program present or successfully factory image programmed      
        """
        firm_info = self.check_firmware_info()
        if firm_info == [] or firm_info[0]['product_string'] != "CryptoAuth Trust Platform":    
            debug_info = self.check_debugger_info()
            if debug_info != []:
                if "MCHP3311" in debug_info[0]['serial_number']:
                    print("Default factory program image not found")
                    if self.check_mplab_path() == True: 
                        print("Programming factory reset image")
                        homepath = path_helper.get_home_path()
                        hexfile = str(Path(os.path.join(homepath, "assets", "Factory_Program.X", "CryptoAuth_Trust_Platform.hex"))) 
                        subprocessout = self.flash_micro(hexfile)
                        print(subprocessout.stdout)
                        if subprocessout.returncode != 0:
                            return subprocessout.stderr
                        else:
                            return True
                    else:
                        return "Reprogram the CryptoAuth Trust Platform board with Trust platform factory program"
                else:
                    return "Cannot connect to CryptoAuth Trust Platform, check USB connection"
            else:
                return "Cannot connect to CryptoAuth Trust Platform, check USB connection"
                 
        else:
            return True


