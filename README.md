# Airthings Thingies

This is a general purpose repository for my Airthings devices. This is based off the [WavePlus Reader](https://github.com/Airthings/waveplus-reader) source code with support for Python 3.x. This has been developed on a Raspberry Pi 3b+ but it should work on any Linux system with `libglib2.0-dev` and `bluepy`.

## Usage

```
usage: airthings.py [-h] [--config CONFIG] [--device-serial DEVICE_SERIAL]

Airthings WavePlusPlus

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        The path to the configuration file.
  --device-serial DEVICE_SERIAL, -d DEVICE_SERIAL
                        The serial number for the device. Can be a comma
                        separated list.
```

## Details

This is still a work in progress but the gist of it is:

 * Update `config.json` with your device information. Each entry should have it's own JSON node.
 * Run the script as root unless you've figured out how to run it as a user (I haven't *yet*)

 The output will end up in the `data` folder by default unless you set it in the `config.json` file.
