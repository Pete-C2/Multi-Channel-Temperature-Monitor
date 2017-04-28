from flask import Flask, render_template
import datetime
import RPi.GPIO as GPIO
from max31855 import MAX31855, MAX31855Error
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

# Read config from xml file

# Find directory of the program
dir = os.path.dirname(os.path.abspath(__file__))
tree = ET.parse(dir+'/config.xml')
root = tree.getroot()
HW = root.find('HARDWARE')
sensors = root.find('SENSORS')
display = root.find('DISPLAY')

# Read hardware
# Clock
CLK = HW.find('CLOCK')
clock_pin = int(CLK.find('PIN').text)
# Data
DATA = HW.find('DATA')
data_pin = int(DATA.find('PIN').text)
# Chip Selects
cs_pins = []
for child in sensors:
     cs_pins.append(int(child.find('CSPIN').text))

# Read display settings
units = display.find('UNITS').text.lower()
channel_names = []
for child in sensors:
     channel_names.append(child.find('NAME').text)
     
# Create a dictionary called temps to store the temperatures and names:
temps = {}
channel = 1
for child in sensors:
     temps[channel] = {'name' : child.find('NAME').text, 'temp' : ''}
     channel = channel + 1

@app.route('/')
def index():
   now = datetime.datetime.now()
   timeString = now.strftime("%H:%M on %d-%m-%Y")
   templateData = {
      'time': timeString
      }
   return render_template('main.html', **templateData)

@app.route('/temp')
def temp():
   now = datetime.datetime.now()
   timeString = now.strftime("%H:%M on %d-%m-%Y")

   thermocouples = []

   channel = 1
   for cs_pin in cs_pins:
       thermocouples.append(MAX31855(cs_pin, clock_pin, data_pin, units, GPIO.BOARD))

   for thermocouple in thermocouples:
       if (channel == 1):
          air_temp = int(thermocouple.get_rj())
       try:
           tc = int(thermocouple.get())
       except MAX31855Error as e:
           tc = "Error: "+ e.value
           running = False

       temps[channel]['temp'] = tc
       channel = channel + 1

   for thermocouple in thermocouples:
       thermocouple.cleanup()
       
   templateData = {
      'time': timeString,
      'air' : air_temp,
      'temps' : temps,
      'units' : units.upper()
      }

   return render_template('oven.html', **templateData)

@app.route('/confirm')
def confirm():
   return render_template('confirm.html')

@app.route('/shutdown')
def shutdown():
   command = "/usr/bin/sudo /sbin/shutdown +1"
   import subprocess
   process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
   output = process.communicate()[0]
   print output
   return render_template('shutdown.html')

@app.route('/cancel')
def cancel():
   command = "/usr/bin/sudo /sbin/shutdown -c"
   import subprocess
   process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
   output = process.communicate()[0]
   print output
   return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
