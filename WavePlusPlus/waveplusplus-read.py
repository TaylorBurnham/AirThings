#!/usr/bin/env python3
# Code has been heavily lifted from the original source published
# by Airthings, but adapted for use with Python3.
#
# https://github.com/Airthings/waveplus-reader
#
# All source is released under the MIT license.
# Requires bluepy==1.3.0

import os
import sys
import json
import time
import struct
import logging
from datetime import datetime
from bluepy.btle import UUID, Peripheral, Scanner, DefaultDelegate

class WavePlusPlus():
    def __init__(self, SerialNumber):
        logging.info("Initialized")
        self.periph = None
        self.curr_val_char = None
        self.MacAddr = None
        self.SN = SerialNumber
        self.uuid = UUID("b42e2a68-ade7-11e4-89d3-123b93f75cba")

    def connect(self):
        logging.info("Attempting connection to device with Serial Number {}".format(self.SN))
        if self.MacAddr is None:
            scanner = Scanner().withDelegate(DefaultDelegate())
            searchCount = 0
            # Loop for 50 scans or until we find it.
            while self.MacAddr is None:
                devices = scanner.scan(0.1)
                searchCount += 1
                for dev in devices:
                    ManuData = dev.getValueText(255)
                    logging.info("Checking if Device {} / {} is WavePlus".format(dev.addr, ManuData))
                    if ManuData:
                        SN = self.parseSerialNumber(ManuData)
                        if SN == self.SN:
                            logging.info("Found Device {} with Serial Number {}".format(dev.addr, SN))
                            self.MacAddr = dev.addr
                if searchCount >= 50:
                    # Set to false if we hit 50.
                    # No breaks.
                    self.MacAddr = False
            if self.MacAddr is None or not self.MacAddr:
                logging.ERROR("Could not find device.")
                sys.exit(1)

        # Initialize Device
        if self.periph is None:
            logging.info("Connecting to Device {}".format(self.MacAddr))
            self.periph = Peripheral(self.MacAddr)
        if self.curr_val_char is None:
            self.curr_val_char = self.periph.getCharacteristics(
                uuid=self.uuid
            )[0]

    def disconnect(self):
        if self.periph:
            logging.info("Disconnecting from Device")
            self.periph.disconnect()
            self.periph = None
            self.curr_val_char = None
        else:
            logging.info("No device to disconnect from.")

    def read(self):
        if (self.curr_val_char is None):
            logging.info("ERROR: Devices are not connected.")
            sys.exit(1)
        raw_data = self.curr_val_char.read()
        sensor_data = self.parseSensors(raw_data)
        return sensor_data

    @staticmethod
    def parseSerialNumber(ManuDataHexStr):
        ManuData = bytearray.fromhex(ManuDataHexStr)
        if (((ManuData[1] << 8) | ManuData[0]) == 0x0334):
            SN  =  ManuData[2]
            SN |= (ManuData[3] << 8)
            SN |= (ManuData[4] << 16)
            SN |= (ManuData[5] << 24)
        else:
            SN = "Unknown"
        return SN

    def parseSensors(self, raw_data):
        raw_data = struct.unpack('BBBBHHHHHHHH', raw_data)
        sensor_version = raw_data[0]
        if sensor_version == 1:
            # build sensors
            sensor_data = {
                "config": {
                    "version": sensor_version,
                    "tbd1": raw_data[2],
                    "tbd2": raw_data[3]
                },
                "atmospheric": {
                    "humidity": {
                        "value": raw_data[1] / 2.0,
                        "unit": "%rH"
                    },
                    "temperature": {
                        "value": raw_data[6] / 100.0,
                        "unit": "C"
                    },
                    "pressure": {
                        "value": raw_data[7] / 50.0,
                        "unit": "hPa"
                    }
                },
                "particle": {
                    "radon_lt": {
                        "value": self.conv2radon(raw_data[5]),
                        "unit": "Bq/m3"
                    },
                    "radon_st": {
                        "value": self.conv2radon(raw_data[4]),
                        "unit": "Bq/m3"
                    },
                    "co2": {
                        "value": raw_data[8] * 1.0,
                        "unit": "ppm"
                    },
                    "voc": {
                        "value": raw_data[9] * 1.0,
                        "unit": "ppb"
                    }
                }
            }
        else:
            logging.info("Unknown Sensor Version {}".format(sensor_version))
            logging.info("Raw Output: {}".format(raw_data))
            sys.exit(1)
        return sensor_data

    @staticmethod
    def conv2radon(radon_raw):
        if 0 <= radon_raw <= 16383:
            radon = radon_raw
        else:
            radon = "N/A" # bad read
        return radon


# Logging Settings
logPath = "logs"
logFile = "WavePlusPlus-{}.log".format((datetime.now().strftime("%Y-%m-%d")))
if not os.path.exists(logPath):
    os.mkdir(logPath)

# Logging Config
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, logFile))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.INFO)

logging.info("Script Initialized")
if sys.argv[1].isdigit() is not True or len(sys.argv[1]) != 10:
    logging.error("Incorrect or no value passed for serial number.")
    logging.error("Value Passed: {}".format(sys.argv[1]))
    sys.exit(1)

SerialNumber = int(sys.argv[1])
dataPath = "data"
dataFile = os.path.join(dataPath, ("WavePlus-{}-{}.json".format(SerialNumber, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))))
if not os.path.exists(dataPath):
    os.mkdir(dataPath)

logging.info("Getting Data from WavePlus {}".format(SerialNumber))
sensors = None
waveplus = WavePlusPlus(SerialNumber)
waveplus.connect()
sensors = waveplus.read()
waveplus.disconnect()
logging.info("Got Data!")

if sensors:
    logging.info("Writing to File {}".format(dataFile))
    with open(dataFile, 'w') as fh:
        json.dump(sensors, fh, indent=4, sort_keys=False)
else:
    logging.info("Failed to get data!")
    logging.info("Data: {}".format(sensors))

logging.info("Done!")