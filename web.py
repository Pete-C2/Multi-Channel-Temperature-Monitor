from flask import Flask, render_template
import datetime
import RPi.GPIO as GPIO
from max31855 import MAX31855, MAX31855Error

app = Flask(__name__)

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

   cs_pins = [3, 5]
   clock_pin = 11
   data_pin = 7
   units = "c"
   thermocouples = []
   # Create a dictionary called temps to store the temperatures and names:
   temps = {
      1 : {'name' : 'Channel 1', 'temp' : ''},
      2 : {'name' : 'Channel 2', 'temp' : ''}
      }
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
      'temps' : temps
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
