# Airthings Thingies

This will be a general purpose repository for storing code and other thingies related to Airthings devices.

## Current Solutions

* WavePlusPlus - A partial rewrite of the existing [WavePlus Reader](https://github.com/Airthings/waveplus-reader) published by [Airthings](https://github.com/Airthings).

## WavePlusPlus

A Python 3 script that will read the serial number as the first parameter and spit out a JSON file with the results. There's two values I am not sure what they do and are ignored in the source code. I've filed these as `tbd1` and `tbd2` and may disappear without notice if I confirm they have no purpose.

Usage

This must be run as root (until I figure out how to not have to run it as root):

    ./waveplusplus-read.py <serial>

To test it for a bit (before running as a daemon):

    while true; do ./waveplusplus-read.py <serial>; sleep 60; done

Example output to file:

    {
        "config": {
            "version": 1,
            "tbd1": 10,
            "tbd2": 0
        },
        "atmospheric": {
            "humidity": {
                "value": 49.5,
                "unit": "%rH"
            },
            "temperature": {
                "value": 24.2,
                "unit": "C"
            },
            "pressure": {
                "value": 1011.3,
                "unit": "hPa"
            }
        },
        "particle": {
            "radon_lt": {
                "value": 18,
                "unit": "Bq/m3"
            },
            "radon_st": {
                "value": 9,
                "unit": "Bq/m3"
            },
            "co2": {
                "value": 956.0,
                "unit": "ppm"
            },
            "voc": {
                "value": 462.0,
                "unit": "ppb"
            }
        }
    }