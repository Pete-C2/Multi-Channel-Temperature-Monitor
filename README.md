# Multi-Channel-Temperature-Monitor
Multi-channel temperature monitor, e.g. for wood fired oven. The intention is for the Raspberry Pi to be headless and all operation undertaken through a web browser. Text sizes have been optimised for viewing on mobile phone screens.

Requires:
- The [GPIO Library](https://code.google.com/p/raspberry-gpio-python/) (Already on most Raspberry Pi OS builds).
- The [Flask web server](https://www.raspberrypi.org/learning/python-web-server-with-flask/worksheet/). Install command:
  - sudo apt-get install python3-flask
- A [Raspberry Pi](http://www.raspberrypi.org/).
- Hardware with [MAX31855 temperature monitors](https://www.maximintegrated.com/en/products/analog/sensors-and-sensor-interface/MAX31855.html):
  - Design updated for flexible number of sensors

Installation:
- Copy files to a folder on the Raspberry Pi
- Edit /etc/rc.local to autorun application:
   - sudo nano /etc/rc.local
   - Add: python /home/pi/.../web.py where ... is the location of your file
- Edit config.xml to define system
    
Recommendations (to make life easier):
- Set a [static IP address](https://www.modmypi.com/blog/tutorial-how-to-give-your-raspberry-pi-a-static-ip-address)
- Define a [hostname](http://www.simonthepiman.com/how_to_rename_my_raspberry_pi.php)
- Create a [fileshare](http://raspberrypihq.com/how-to-share-a-folder-with-a-windows-computer-from-a-raspberry-pi/)

## Use

Load webpage Your.IP:5000 where Your.IP is the IP address of your Raspberry Pi (hence the recommendation to set a static IP address) or //hostname:5000.
Click on:
- Temperatures to begin monitoring. The webpage updates every two seconds.
- Shutdown to turn the Raspberry Pi off from the web browser.

## Changelog

### V0.2
Added config.xml to define the configuration.
Supports arbitrary number of channels.

### V0.1
Initial trial code.

Supports two fixed temperature monitoring channels.

MAX31855 driver modified from https://github.com/Tuckie/max31855.
