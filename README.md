Weather Board Libraries and Example for Raspberry Pi

Supports SwitchDoc Labs WeatherRack / Argent Data / Sparkfun

Version 1.5 
July 19, 2016

SwitchDocLabs Documentation for the Weather Board under products on:

http://www.switchdoc.com/

Support for all 7 I2C devices supported by the Weather Board

New Support for the SwitchDoc Labs Grove OLED Board
New Support for the MOD-1016G Grove Lightning Detection Board - www.embeddedadventures.com 


-------------------
Other installations required for AM2315 support:

sudo apt-get install python-pip 
sudo apt-get install libi2c-dev 
sudo pip install tentacle_pi

-------------------
Other installations required for SD1306 OLED support:
sudo apt-get update

sudo apt-get install python-imaging python-smbus

sudo apt-get install build-essential python-dev python-pip
sudo pip install RPi.GPIO


Finally, on the Raspberry Pi install the Python Imaging Library and smbus library by executing:

sudo apt-get install python-imaging python-smbus

Now to download and install the SSD1306 python library code and examples, execute the following commands:

sudo apt-get install git 
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
sudo python setup.py install



--------------------
Setup for the WeatherBoard.py file
--------------------

Modify this section of code to support your configuration:

# set to true if you are building the Weather Board project with Lightning Sensor
config.Lightning_Mode = False

All other devices are detected automatically.

----------------
Example Execution
----------------

sudo python WeatherBoard.py


