#
#           Philips LED Lamp python Plugin for Domoticz
#           Version 0.1.3

#           Powered by lib python miio https://github.com/rytilahti/python-miio
#
#           This is forked version by mazycz from Whilser
#           In this version are removed scenes and implemented multiple lamps using JSON configuration
#


"""
<plugin key="PhilipsLED" name="Xiaomi MiJia Philips LED Lamp" author="mazy.cz" originalauthor="Whilser" version="0.1.3" wikilink="https://www.domoticz.com/wiki/Xiaomi_MiJia_Philips_LED_Lamp" externallink="https://github.com/mazycz/Xiaomi-MiJia-Philips-LED-Lamp">
    <description>
        <h2>Xiaomi MiJia Philips LED Lamp</h2><br/>
        <h3>Configuration</h3>
        Enter Name, the IP Address and Token of your Philips Lamp. Enter data in JSON Format<br/>
        <br/><br/>
        JSON Data format example: [{'Name' : 'Lamp 1', 'IP Address' : '192.168.0.1', 'Token': 'aabbcc'},{'Name' : 'Lamp 2', 'IP Address' : '192.168.0.2', 'Token': 'aabbcc'}]
    </description>
    <params>
        <param field="Address" label="JSON Data" width="500px" required="true" default=""/>
        <param field="Mode2" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="True" />
            </options>
        </param>
    </params>
</plugin>
"""

import os
import sys
import time
import os.path
import json
import random
import binascii

import Domoticz

module_paths = [x[0] for x in os.walk( os.path.join(os.path.dirname(__file__), '.', '.env/lib/') ) if x[0].endswith('site-packages') ]
for mp in module_paths:
    sys.path.append(mp)

from miio import PhilipsBulb
from miio.philips_bulb import PhilipsBulbStatus, PhilipsBulbException

class BasePlugin:

    UNITS = []
    LAMPS = []

    pollTime = 1
    nextTimeSync = 0
    handshakeTime = 0

    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        jsObj = json.loads(Parameters["Address"])
        for i in range(len(jsObj)):
            self.UNITS.append(jsObj[i])
            if i+1 not in Devices:
                Domoticz.Log(f'Not in Philips - {self.UNITS[i]["Name"]}')
                Domoticz.Device(Name=self.UNITS[i]["Name"],  Unit=i+1, Type=241, Subtype=8, Switchtype=7, Used=1).Create()
            self.LAMPS.append(PhilipsBulb(self.UNITS[i]["IP Address"], self.UNITS[i]["Token"]))

        self.pollTime = random.randrange(5, 16)
        self.nextTimeSync = 0

        DumpConfigToLog()
        Domoticz.Heartbeat(20)

        Domoticz.Debug('Plugin started.')
        Domoticz.Log('Poll time is every {0} minute'.format(self.pollTime))

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Color):
        #Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level)+ ", Color: "+str(Color))
        Level = max(min(Level, 100), 1)

        try:
            if Command == 'On':
                Domoticz.Log(f"On {Unit -1}")
                self.LAMPS[Unit - 1].on()
                Devices[Unit].Update(nValue=1, sValue='On', TimedOut = False)

            elif Command == 'Off':
                Domoticz.Log(f"Off {Unit -1}")
                self.LAMPS[Unit - 1].off()
                Devices[Unit].Update(nValue=0, sValue='Off', TimedOut = False)

            elif Command == 'Set Level':
                Domoticz.Log(f"SetLevel {Unit -1} level: {Level}")
                self.LAMPS[Unit - 1].set_brightness(Level)
                Devices[Unit].Update(nValue=1, sValue=str(Level), TimedOut = False)

            elif Command == 'Set Color':
                Domoticz.Log(f"SetColor {Unit -1} level: {Color}")
                Hue = json.loads(Color)
                if Hue['m'] == 2:
                    Temp = 100-((100*Hue['t'])/255)
                    Temp = max(min(Temp, 100), 1)

                    self.LAMPS[Unit - 1].set_brightness_and_color_temperature(Level, Temp)
                    Devices[Unit].Update(nValue=1, sValue=str(Level), Color = Color, TimedOut = False)
        except Exception as e:
            Domoticz.Error('Error send command to {0} with IP {1}. Lamp is not responding, check power/network connection. Errror: {2}'.format(Unit, self.UNITS[Unit - 1], e.__class__))
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=Devices[Unit].sValue, TimedOut = True)
            self.handshakeTime = 0
            self.nextTimeSync = 0

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        self.nextTimeSync -= 1
        self.handshakeTime -= 1

        try:
            for i in range(len(self.UNITS)):
                if self.handshakeTime <= 0:
                    self.LAMPS[i].do_discover()
                    self.handshakeTime = 3

                if (self.nextTimeSync <= 0) and (i+1 in Devices):
                    Domoticz.Debug('Sync on time: every {0} minute called'.format(self.pollTime))
                    self.nextTimeSync = int((self.pollTime*60)/20)

                    status = self.LAMPS[i].status()

                    if status.is_on:
                        hue = int((100 - int(status.color_temperature)) * 255 / 100)
                        if hue == 0: hue = 1

                        color = {}
                        color['m']  = 2
                        color['t']  = hue
                        color['r']  = 0
                        color['g']  = 0
                        color['b']  = 0
                        color['cw'] = 0
                        color['ww'] = 0
                        sColor = json.dumps(color)

                        # if ((Devices[self.UNITS[i]].sValue != str(status.brightness)) or (Devices[self.UNITS[i]].nValue != 1) or (Devices[self.UNITS[i]].TimedOut == True)):
                        #     Devices[self.UNITS[i]].Update(nValue=1, sValue=str(status.brightness), Color = sColor, TimedOut = False)

                    if not status.is_on:
                        if ((Devices[i+1].nValue != 0) or (Devices[i+1].TimedOut == True)):
                            Devices[i+1].Update(nValue=0, sValue='Off', TimedOut = False)

        except Exception as e:
            #Devices[self.UNITS].Update(nValue=Devices[self.UNITS].nValue, sValue=Devices[self.UNITS].sValue, TimedOut = True)
            self.handshakeTime = 0
            self.nextTimeSync = 0

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device TimedOut: " + str(Devices[x].TimedOut))
    return
