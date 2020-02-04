#!/usr/bin/python3
# On system start, call gpio_controls.py start
# This powers up the LCD, starts LCDd, starts lcdproc, sets up the shutdown pin
#  and finally starts the fan control loop. 
# When the script gets a stop it shuts everything down but
#  does not issue a shutdown command.
# When it sees the shutdown pin pressed for more than 2 seconds, 
#  it does shut everything down and issue shutdown.

import os
import sys
import psutil
import subprocess
from time import sleep
from gpiozero import LED, Button, PWMLED

# Pin Definitions
sdButPIN = 17
lcdPower = 27
fanPWM = 22

# GPOI Object assignment
lcd = LED(lcdPower) # We're using LED as a power switch
fan = PWMLED(fanPWM)

# definitions
desiredTemp = 45 # The maximum temperature in Celsius after which we trigger the fan
fanSpeed = 99.00
minSpeed = 40.00

# Startup Processes
def lcdON():
    # Turn on the LCD, start LCDd daemon, start lcdproc
    # Restart lcdproc and LCDd if they are already running.
    print(" lcdON Called.")
    lcd.on()
    sleep(1)
    for proc in psutil.process_iter():
    # check whether the process name matches
        if proc.name() == 'lcdproc':
            proc.kill()
        if proc.name() == 'LCDd':
            proc.kill()
    # /usr/local/sbin/LCDd
    subprocess.Popen(["LCDd"])
    sleep(1)
    # /usr/local/bin/lcdproc
    subprocess.Popen(["lcdproc"])
    return()

def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    temp =(res.replace("temp=","").replace("'C\n",""))
    return temp

def handleFan():
    global fanSpeed
    actualTemp = float(getCPUtemperature())
    if (actualTemp > desiredTemp) and (fanSpeed <= 93):
        fanSpeed = fanSpeed + 6
    if (actualTemp < desiredTemp) and (fanSpeed >= minSpeed):
        fanSpeed = fanSpeed - 6
    pwmSpeed = fanSpeed / 100
    print("CPU Temp %4.2f F, Fan Speed %3d %% " % (actualTemp,fanSpeed))
    fan.value = pwmSpeed
    return()

# Shutdown Processes
def lcdOFF():
    print(" lcdOFF Called.")
    for proc in psutil.process_iter():
    # check whether the process name matches
        if proc.name() == 'lcdproc':
            proc.kill()
        if proc.name() == 'LCDd':
            proc.kill()
    lcd.off()
    return()

def shutdown():
    lcdOFF()
    subprocess.check_call(['sudo','poweroff'])
    sys.exit(0)

# Main
try:
    print("Starting Script.")
    if (len(sys.argv) > 1):
        if (sys.argv[1] == 'start'):
            lcdON()
            sdButton = Button(sdButPIN, hold_time=2)
            sdButton.when_held = shutdown
        if (sys.argv[1] == 'stop'):
            lcdOFF()
            sys.exit(0)
    else:
        print("Usage: gpio_controls.py {start|stop}")
        sys.exit(0)
    while True:
        handleFan()
        sleep(5) # Read the temperature every 5 sec, increase or decrease this limit if you want 
except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt 
    lcdOFF()
    sys.exit(0)
    
print("Script end.")