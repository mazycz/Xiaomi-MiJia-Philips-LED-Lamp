# Xiaomi MiJia Philips LED Lamp Domoticz Plugin

This plugin is required to add the Xiaomi MiJia Philips LED Lamp to the list of supported devices Domoticz Home Automation System. **Note:** The plugin is under development. The plugin was tested with python 3.7.x and Domoticz 4.x installed on Raspberry Pi with Raspbian Buster.

This fork is updated to work with Python 3.7 and Raspbian Buster with multiple (Xiaomi MiJia Philips LED Lamp) lamps.
This fork is update to [Can't add any new Philips led issue](https://github.com/Whilser/Xiaomi-MiJia-Philips-LED-Lamp/issues/6) 

![Philis Bulb](https://github.com/mazycz/Xiaomi-MiJia-Philips-LED-Lamp/raw/master/images/PhilipsBulb.png)

## Currently supported:

- [x] Philips Bulb
- [x] Philips ZhiRui downlight
- [x] Philips ZhiYi ceiling lamp
- [x] etc. Xiaomi MiJia Philips LED lamp (basic support)

## How to Install:

    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install python3 python3-dev python3-pip
    sudo apt-get install libffi-dev libssl-dev
    sudo pip3 install -U pip setuptools
    sudo pip3 install -U virtualenv
    cd domoticz/plugins
    git clone https://github.com/mazycz/Xiaomi-MiJia-Philips-LED-Lamp.git PhilipsLED
    cd PhilipsLED
    virtualenv -p python3 .env
    source .env/bin/activate
    pip3 install python-miio==0.4.8
    deactivate

    sudo service domoticz restart

## How to update:

    cd domoticz/plugins/PhilipsLED
    git pull
    sudo service domoticz restart

To configure device, enter JSON formated configuration the Name, IP Address and Token of your Philips Lamp.
#### JSON Data format example: 

    [
        {"Name" : "Lamp 1", "IP Address" : "192.168.0.1", "Token": "aabbcc"},
        {"Name" : "Lamp 2", "IP Address" : "192.168.0.2", "Token": "ddeeff"}
    ]


![Domoticz plugin](https://github.com/mazycz/Xiaomi-MiJia-Philips-LED-Lamp/raw/master/images/DomoticzUnit.png)

If you liked it, buy me coffee! <br>
<a href="https://www.buymeacoffee.com/96izNco" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-yellow.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>


# Xiaomi MiJia Philips LED Lamp Plug for Domoticz

The plugin adds Xiaomi MiJia Philips LED Lamp support to the Domoticz home automation system. To configure the plugin, enter the IP address and token of the device. The `Scenes` parameter creates a selector switch for standard Philips LED Lamp scenes, set it to` show` if you plan to use scenes, otherwise set the flag to `hide`. The `Debug` flag is used to detect errors and debug the plugin. In order to prevent technical information from pouring into the console, it is recommended that the Debug flag be set to `False`.

#### Known bugs
- Adding and removing devices, currenty you have to manualy delete devices and then add then all in one time
- mobile application not changing state (on/off) immediately - you have to refresh it