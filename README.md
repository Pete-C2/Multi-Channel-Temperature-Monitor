# Multi-Channel-Temperature-Monitor
Multi-channel temperature monitor, e.g. for wood fired oven. The intention is for the Raspberry Pi to be headless and all operation undertaken through a web browser. Text sizes have been optimised for viewing on mobile phone screens.

Requires:
- The [GPIO Library](https://code.google.com/p/raspberry-gpio-python/) (Already on most Raspberry Pi OS builds).
- The [Flask web server](https://www.raspberrypi.org/learning/python-web-server-with-flask/worksheet/). Install command:
  - sudo apt-get install python3-flask
- A [Raspberry Pi](http://www.raspberrypi.org/).
- Hardware with [MAX31855 temperature monitors](https://www.maximintegrated.com/en/products/analog/sensors-and-sensor-interface/MAX31855.html):
  - Design updated for flexible number of sensors.

Installation:
- Copy files to a folder on the Raspberry Pi.
- Edit /etc/rc.local to autorun application:
   - sudo nano /etc/rc.local
   - Add: python /home/pi/.../temperature-monitor.py where ... is the location of your file.
- Edit config.xml to define your system hardware. The defaults match my hardware.
    
Recommendations (to make life easier):
- Set a [static IP address](https://www.modmypi.com/blog/tutorial-how-to-give-your-raspberry-pi-a-static-ip-address).
- Define a [hostname](http://www.simonthepiman.com/how_to_rename_my_raspberry_pi.php).
- Create a [fileshare](http://raspberrypihq.com/how-to-share-a-folder-with-a-windows-computer-from-a-raspberry-pi/).
- Install [VNC](https://www.raspberrypi.org/documentation/remote-access/vnc/) for full headless access.

## Use

See wiki.

## Changelog

### V2.0.4
Simplified the REST sensor measurement

### V2.0.3
Simplified the REST sensors config

### V2.0.2
Simplified the REST systemconfig 

### V2.0.1
Corrected template to match changed variable name

### V2.0
Completed updated to REST interface
Logging uses measurements from measurement thread

### V1.2.6
Created thread to take measurements

### V1.2.5
Merged sensor definition

### V1.2.4
Reverted some changes as HTML and REST api's need two different data structures

### V1.2.3
Started to refactor code

### V1.2.2
Initial REST implementation


### V1.2.1
Updated to Python3

### V1.1
As a result of errors observered on the wood oven, typically short to ground error, code amended to record the last valid temperature and to indicate how old the measurement is.

### V1.0
Defined twelve temperature monitoring channels.

Considered suitable for use.

### V0.4
Added optional note to CSV output.

Added HTML page title to XML configuration.

### V0.3
Added CSV log output.

Tidied up code.

### V0.2
Added config.xml to define the configuration.

Supports arbitrary number of channels.

### V0.1
Initial trial code.

Supports two fixed temperature monitoring channels.

MAX31855 driver modified from https://github.com/Tuckie/max31855.
