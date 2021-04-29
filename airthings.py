#!/usr/bin/env python3
import os
import sys
import json
import logging
import argparse
from datetime import datetime
from airthings.waveplusplus import WavePlusPlus

parser = argparse.ArgumentParser(description='Airthings WavePlusPlus')
parser.add_argument('--config', '-c', default='config.json', 
    help='The path to the configuration file.')
parser.add_argument('--device-serial', '-d',
    help='The serial number for the device. Can be a comma separated list.')

if __name__ == "__main__":
    # todo - clean all of this up because its horrible
    args = parser.parse_args()
    if args.device_serial:
        try:
            devices = [
                {"name": None, "serial": int(x)}
                for x in args.device_serial.split(',')
            ]
        except ValueError:
            raise ValueError(
                "Invalid serial number passed. Must be integers "
                f"separated by commas. Received: {args.device_serial}"
            )
            sys.exit(1)
        # Defaults
        config = {
            "logging": {
                "enabled": True
            }
        }
        dataPath = "data"
    else:
        if os.path.exists(args.config):
            with open(args.config, 'r') as fh:
                config = json.load(fh)
            devices = config['devices']
        else:
            raise FileNotFoundException(
                "No devices passed and no config.json found."
            )
        if 'output' in config:
            if 'path' in config['output']:
                dataPath = config['output']['path']
            else:
                dataPath = 'data'
        if config['logging']['enabled']:
            if 'logfile' in config['logging']:
                logfile = config['logging']['logfile']
                if logfile['enabled']:
                    logPath = logfile['path']
                    dt = datetime.now().strftime("%Y-%m-%d")
                    logFile = f"WavePlusPlus-{dt}.log"
                    logFilePath = os.path.join(
                        logPath, logFile
                    )
                    if not os.path.exists(logPath):
                        os.mkdir(logPath)
            # Logging Config
            if 'logformat' in config['logging']:
                logformat = config['logging']['logformat']
            else:
                logformat = "%(asctime)s [%(levelname)-5.5s] %(message)s"
            logFormatter = logging.Formatter(logformat)
            rootLogger = logging.getLogger()
            if logfile['enabled']:
                fileHandler = logging.FileHandler(logFilePath)
                fileHandler.setFormatter(logFormatter)
                rootLogger.addHandler(fileHandler)

            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            rootLogger.addHandler(consoleHandler)
            rootLogger.setLevel(logging.INFO)

            logging.info("Script Initialized")
    
    if not os.path.exists(dataPath):
        logging.info(f"Creating Output Path: {dataPath}")
        os.mkdir(dataPath)

    for device in devices:
        serial = int(device['serial'])
        logging.info(f"Querying Device {serial}")
        sensors = None
        for i in range(5):
            waveplus = WavePlusPlus(serial)
            waveplus.connect()
            sensors = waveplus.read()
            waveplus.disconnect()
            if sensors:
                logging.info("Successfully queried device.")
                break
            else:
                logging.warn(
                    "Failed to query device. Trying again in 5 seconds.")
                time.sleep(5)
        else:
            logger.warn("Failed to query after five tries. Giving up!")
        dts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        dataFile = f"WavePlusPlus-{serial}-{dts}.json"
        logging.info(f"Writing to file {dataFile}")
        dataFilePath = os.path.join(
            dataPath, dataFile
        )
        with open(dataFilePath, 'w') as fh:
            json.dump(sensors, fh, indent=4, sort_keys=False)