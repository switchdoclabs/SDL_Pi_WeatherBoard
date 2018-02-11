Weather Board Libraries and Example for Raspberry Pi

Supports SwitchDoc Labs WeatherRack / Argent Data / Sparkfun

Version 1.8 

August 22, 2016: Added support for WXLink - Wireless connection to WeatherRack and AM2315

August 4, 2016:   Fix for OLED Present under Lightning Conditions

SwitchDocLabs Documentation for the Weather Board under products on:

http://www.switchdoc.com/

Support for all 7 I2C devices supported by the Weather Board

New Support for the SwitchDoc Labs Grove OLED Board <BR>
New Support for the ThunderBoard Lighting Detector <BR>
New Support for SwitchDoc SunAirPlus Solar Power Controller Board<BR>


-------------------
Other installations required for AM2315 support:

sudo apt-get install python-pip <BR>
sudo apt-get install libi2c-dev <BR>
sudo pip install tentacle_pi<BR>

-------------------
Other installations required for SD1306 OLED support:
sudo apt-get update<BR>

sudo apt-get install python-imaging python-smbus<BR>

sudo apt-get install build-essential python-dev python-pip<BR>
sudo pip install RPi.GPIO<BR>


Finally, on the Raspberry Pi install the Python Imaging Library and smbus library by executing:

sudo apt-get install python-imaging python-smbus<BR>

Now to download and install the SSD1306 python library code and examples, execute the following commands:

sudo apt-get install git <BR>
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git<BR>
cd Adafruit_Python_SSD1306<BR>
sudo python setup.py install<BR>



--------------------
Setup for the WeatherBoard.py file
--------------------

Modify this section of code to support your configuration:
<pre>
# set to true if you are building the Weather Board project with Lightning Sensor
config.Lightning_Mode = False
# set to true if you are building the Solar Powered Weather Board
config.SolarPower_Mode = False
</pre>

All other devices are detected automatically.

----------------
Example Execution
----------------

sudo python WeatherBoard.py


----------------
Programming Note
----------------

If you attach an AM2315 to the WXLink Transmitter, then the program will assume that is the AM2315 you want for outside temperature and humidity.   These values will overwrite the AM2315 connected to the local Raspberry Pi or Weather Board.
