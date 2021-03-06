"""Multi-channel temperature logger
Reads the configuration from an associated xml file.
Presents a set of webpages to display the temperature from an arbitrary number of temperature sensors as defined by the configuration.
"""

from flask import Flask, render_template, request
from flask_restful import Api, Resource, reqparse, fields, marshal
import datetime
import xml.etree.ElementTree as ET
import os
import threading
import time
import csv
import RPi.GPIO as GPIO
from max31855 import MAX31855, MAX31855Error

sensor_fields = {
    'name': fields.String,
    'uri': fields.Url('temperature_sensor')
}

class SystemConfig(Resource):
     def __init__(self):
          super(SystemConfig, self).__init__()
     def get(self):
          return {"name": title, "units": units}

class TemperatureSensorList(Resource):

    def __init__(self):
        super(TemperatureSensorList, self).__init__()

    def get(self):
        return [marshal(temperatureSensor, sensor_fields) for temperatureSensor in sensors]

class TemperatureSensor(Resource):

    def __init__(self):
        super(TemperatureSensor, self).__init__()

    def get(self, id):
          sensor = [sensor for sensor in sensors if sensor['id'] == id] 
          if len(sensor) == 0:
               abort(404)
               
          return {'temperature': sensor[0]['temperature'], 'age': sensor[0]['age']}


# Sensor measurements
class MeasurementThread ( threading.Thread ):

     def run ( self ):
          global sensors
          global temps
          global air_temp
          global cs_pins
          global clock_pin
          global data_pin
          global units

          thermocouples = []
         
          for cs_pin in cs_pins:
               thermocouples.append(MAX31855(cs_pin, clock_pin, data_pin, units, GPIO.BOARD))

          while True: # TODO: Ideally want to detect when closing to exit the loop
               channel = 1
               now = datetime.datetime.now()
               #print(now)
               timeString = now.strftime("%H:%M on %d-%m-%Y")
               
               
               for thermocouple in thermocouples:
                    if (channel == 1):
                         air_temp = int(thermocouple.get_rj())
                         sensors[0]['temperature'] = air_temp
                    try:
                         
                         tc = str(int(thermocouple.get()))
                         temps[channel]['time'] = now
                         temps[channel]['age'] = ''
                         temps[channel]['temperature'] = tc+u'\N{DEGREE SIGN}'+units.upper()
                         temps[channel]['last'] = tc # Record the last valid measurement
                         sensors[channel]['temperature'] = tc
                         sensors[channel]['age'] = ''
                    except MAX31855Error as e:
                         tc = "Error: "+ e.value
                         if (temps[channel]['time'] == 'Never'):
                               age_string = "(Never measured)"
                               temps[channel]['temperature'] = tc
                         else:
                               temps[channel]['temperature'] = temps[channel]['last']
                               age = now - temps[channel]['time']
                               if (age.days == 0):
                                    if (age.seconds < 60):
                                        age_string = "(" + str(age.seconds) + "s)"
                                    else:
                                        if ((int(age.seconds/60)) == 1):
                                             age_string = "(" + str(int(age.seconds/60)) + " min)"
                                        else:
                                             if (age.seconds > (60 * 60)): # > 1 hour
                                                  if ((int(age.seconds/60/60)) == 1):
                                                       age_string = "(" + str(int(age.seconds/60/60)) + " hour)"
                                                  else:
                                                       age_string = "(" + str(int(age.seconds/60/60)) + " hours)"
                                             else:
                                                  age_string = "(" + str(int(age.seconds/60)) + " mins)"
                                    if (age.seconds > (5 * 60)): # 5 mins
                                        temps[channel]['temperature'] = tc + ". Last: " + str(temps[channel]['last'])
                               else:
                                    if (age.days == 1):
                                        age_string = "(" + str(age.days) + " day)"
                                    else:
                                         age_string = "(" + str(age.days) + " days)"
                                    temps[channel]['temperature'] = tc

                         temps[channel]['age'] = age_string
                         sensors[channel]['temperature'] = temps[channel]['temperature']
                         sensors[channel]['age'] = age_string

                    channel = channel + 1
               #end = datetime.datetime.now()
               #print(end-now)

               time.sleep(measurement_interval)

          for thermocouple in thermocouples:
               thermocouple.cleanup()

# Initialisation

# Read config from xml file

# Find directory of the program
dir = os.path.dirname(os.path.abspath(__file__))

# Get the configuration
tree = ET.parse(dir+'/config.xml')
root_cfg = tree.getroot()
HW_cfg = root_cfg.find('HARDWARE')
sensors_cfg = root_cfg.find('SENSORS')
display_cfg = root_cfg.find('DISPLAY')
logging_cfg = root_cfg.find('LOGGING')

# Read hardware configuration
# Clock
CLK = HW_cfg.find('CLOCK')
clock_pin = int(CLK.find('PIN').text)
# Data
DATA = HW_cfg.find('DATA')
data_pin = int(DATA.find('PIN').text)
# Measurement interval
measurement_interval = int(HW_cfg.find('INTERVAL').text) # Interval in seconds between measurements
# Chip Selects
cs_pins = []
for child in sensors_cfg:
     cs_pins.append(int(child.find('CSPIN').text))


# Read display settings configuration
units = display_cfg.find('UNITS').text.lower()
title = display_cfg.find('TITLE').text

sensors = [
    {
        'id': 0,
        'name': u'Air',
        'temperature': u'-',
        'time' : 'Never',
        'age' : ''
    
    }]
air_temp = '-'
temps = {}
channel = 1
for child in sensors_cfg:
     # sensors used to store measurements for REST API
     sensors.append({'id': channel, 'name':  child.find('NAME').text, 'temperature': u'-', 'age' : ''})
     # temps used to store measurements for Flask HTML API
     temps[channel] = {'name' : child.find('NAME').text, 'temperature' : '', 'time' : 'Never', 'age' : ''}
     channel = channel + 1

# Read logging
logging_cfg = root_cfg.find('LOGGING')
log_interval = int(logging_cfg.find('INTERVAL').text)*60  # Interval in minutes from config file
log_status = "Off"  # Values: Off -> On -> Stop -> Off
pending_note = ""

MeasurementThread().start()

app = Flask(__name__)

# Setup Flask REST interface

appREST = Flask(__name__, static_url_path="")
apiREST = Api(appREST)
apiREST.add_resource(SystemConfig, '/temperaturemonitor/api/v1.0/config/systemconfig', endpoint = 'SystemConfig')
apiREST.add_resource(TemperatureSensorList, '/temperaturemonitor/api/v1.0/config/sensors', endpoint = 'temperature_sensors')
apiREST.add_resource(TemperatureSensor, '/temperaturemonitor/api/v1.0/measure/sensors/<int:id>', endpoint = 'temperature_sensor')


# Flask web page code

@app.route('/')
def index():
     global title
     global log_status
     global pending_note
     now = datetime.datetime.now()
     timeString = now.strftime("%H:%M on %d-%m-%Y")
     if log_status == "On":
          logging = "Active"
     else:
          logging = "Inactive"
     if pending_note != "":
          note = "Pending note: " + pending_note
     else:
          note = ""
     templateData = {
                     'title' : title,
                     'time': timeString,
                     'logging' : logging,
                     'note' : note
                    }
     return render_template('main.html', **templateData)

@app.route("/", methods=['POST'])   # Seems to be run regardless of which page the post comes from
def log_button():
     global log_status
     global pending_note
     if request.method == 'POST':
          # Get the value from the submitted form  
          submitted_value = request.form['logging']
          if submitted_value == "Log_Start":
               if (log_status == "Off"):
                    log_status = "On"
                    LogThread().start()
                    
          if submitted_value =="Log_Stop":   
               if (log_status == "On"):
                    log_status = "Stop"
          if submitted_value =="Add_Note":
               pending_note = request.form['note']
     return index()
@app.route('/note')
def note():
     if pending_note != "":
          note = "Pending note: " + pending_note
     else:
          note = ""
     templateData = {
                     'title' : title,
                     'note' : note
                    }
     return render_template('note.html', **templateData)
  
@app.route('/temp')
def temp():
     now = datetime.datetime.now()
     timeString = now.strftime("%H:%M on %d-%m-%Y")

     # TODO: Consider what happens if the thread is updating the data at the same time as display
     # Can a safe copy be made?
       
     templateData = {
                'title' : title,
                'time': timeString,
                'air' : air_temp,
                'temps' : temps,
                'units' : units.upper()
                }

     return render_template('oven.html', **templateData)

@app.route('/confirm')
def confirm():
     templateData = {
                'title' : title
                }
     return render_template('confirm.html', **templateData)

@app.route('/shutdown')
def shutdown():
     command = "/usr/bin/sudo /sbin/shutdown +1"
     import subprocess
     process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
     output = process.communicate()[0]
     print (output)
     templateData = {
                'title' : title
                }
     return render_template('shutdown.html', **templateData)

@app.route('/cancel')
def cancel():
     command = "/usr/bin/sudo /sbin/shutdown -c"
     import subprocess
     process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
     output = process.communicate()[0]
     print (output)

     return index()


          
# Logging code: write a CSV file with header and then one set of sensor measurements per interval
class LogThread ( threading.Thread ):

     def run ( self ):
          global log_status
          global dir
          global log_interval
          global cs_pins
          global clock_pin
          global data_pin
          global units
          global pending_note
          
          now = datetime.datetime.now()
          filetime = now.strftime("%Y-%m-%d-%H-%M")
          filename=dir+'/logging/'+filetime+'_temperature_log.csv'
          with open(filename, 'a') as csvfile:
               logfile = csv.writer(csvfile, delimiter=',', quotechar='"')
               row = ["Date-Time"]
               for channels in temps:
                    row.append( temps[channels]['name'])
                    row.append("Age")
               row.append("Notes")
               logfile.writerow(row)

          while log_status == "On":
               with open(filename, 'a') as csvfile:
                    logfile = csv.writer(csvfile, delimiter=',', quotechar='"')
                    now = datetime.datetime.now()
                    row = [now.strftime("%d/%m/%Y %H:%M")]

                    for channel in temps:
                         row.append(temps[channel]['temperature'])
                         row.append(temps[channel]['age'])

                    if pending_note != "":
                         row.append(pending_note)
                         pending_note = ""
                    logfile.writerow(row)
               time.sleep(log_interval)
          log_status = "Off"

def flaskThread():
     # Start webserver
     app.run(debug=False, host='0.0.0.0', port=5000)
     
if __name__ == '__main__':
     threading.Thread(target=flaskThread).start()
     appREST.run(debug=False, host='0.0.0.0', port=5001)
     
     
