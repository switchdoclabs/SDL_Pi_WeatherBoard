#!/usr/bin/env python
#
# Weather Board Test File
# Version 1.5 July 19, 2016
#
# SwitchDoc Labs
# www.switchdoc.com
#
#

# imports

import sys
import time
from datetime import datetime
import random 


import config

import subprocess
import RPi.GPIO as GPIO


sys.path.append('./RTC_SDL_DS3231')
sys.path.append('./Adafruit_Python_BMP')
sys.path.append('./Adafruit_Python_GPIO')
sys.path.append('./SDL_Pi_WeatherRack')
sys.path.append('./SDL_Pi_FRAM')
sys.path.append('./SDL_Pi_TCA9545')
sys.path.append('./RaspberryPi-AS3935/RPi_AS3935')


import SDL_DS3231
import Adafruit_BMP.BMP280 as BMP280
import SDL_Pi_WeatherRack as SDL_Pi_WeatherRack

import SDL_Pi_FRAM
from RPi_AS3935 import RPi_AS3935


import SDL_Pi_TCA9545
#/*=========================================================================
#    I2C ADDRESS/BITS
#    -----------------------------------------------------------------------*/
TCA9545_ADDRESS =                         (0x73)    # 1110011 (A0+A1=VDD)
#/*=========================================================================*/

#/*=========================================================================
#    CONFIG REGISTER (R/W)
#    -----------------------------------------------------------------------*/
TCA9545_REG_CONFIG            =          (0x00)
#    /*---------------------------------------------------------------------*/

TCA9545_CONFIG_BUS0  =                (0x01)  # 1 = enable, 0 = disable 
TCA9545_CONFIG_BUS1  =                (0x02)  # 1 = enable, 0 = disable 
TCA9545_CONFIG_BUS2  =                (0x04)  # 1 = enable, 0 = disable 
TCA9545_CONFIG_BUS3  =                (0x08)  # 1 = enable, 0 = disable 

#/*=========================================================================*/

import Adafruit_SSD1306

import Scroll_SSD1306

################
# Device Present State Variables
###############

#indicate interrupt has happened from as3936

as3935_Interrupt_Happened = False;
# set to true if you are building the Weather Board project with Lightning Sensor
config.Lightning_Mode = False

config.AS3935_Present = False
config.DS3231_Present = False
config.BMP280_Present = False
config.FRAM_Present = False
config.HTU21DF_Present = False
config.AM2315_Present = False
config.ADS1015_Present = False
config.ADS1115_Present = False
config.OLED_Present = False


###############
# setup lightning i2c mux
##############

# points to BUS0 initially - That is where the Weather Board is located
if (config.Lightning_Mode == True):
	tca9545 = SDL_Pi_TCA9545.SDL_Pi_TCA9545(addr=TCA9545_ADDRESS, bus_enable = TCA9545_CONFIG_BUS0)


def returnStatusLine(device, state):

	returnString = device
	if (state == True):
		returnString = returnString + ":   \t\tPresent" 
	else:
		returnString = returnString + ":   \t\tNot Present"
	return returnString


###############   

#WeatherRack Weather Sensors
#
# GPIO Numbering Mode GPIO.BCM
#

anemometerPin = 26
rainPin = 21

# constants

SDL_MODE_INTERNAL_AD = 0
SDL_MODE_I2C_ADS1015 = 1    # internally, the library checks for ADS1115 or ADS1015 if found

#sample mode means return immediately.  THe wind speed is averaged at sampleTime or when you ask, whichever is longer
SDL_MODE_SAMPLE = 0
#Delay mode means to wait for sampleTime and the average after that time.
SDL_MODE_DELAY = 1

weatherStation = SDL_Pi_WeatherRack.SDL_Pi_WeatherRack(anemometerPin, rainPin, 0,0, SDL_MODE_I2C_ADS1015)

weatherStation.setWindMode(SDL_MODE_SAMPLE, 5.0)
#weatherStation.setWindMode(SDL_MODE_DELAY, 5.0)


################

# DS3231/AT24C32 Setup
filename = time.strftime("%Y-%m-%d%H:%M:%SRTCTest") + ".txt"
starttime = datetime.utcnow()

ds3231 = SDL_DS3231.SDL_DS3231(1, 0x68)


try:

	#comment out the next line after the clock has been initialized
	ds3231.write_now()
	print "DS3231=\t\t%s" % ds3231.read_datetime()
	config.DS3231_Present = True
	print "----------------- "
	print "----------------- "
	print " AT24C32 EEPROM"
	print "----------------- "
	print "writing first 4 addresses with random data"
	for x in range(0,4):
		value = random.randint(0,255)
		print "address = %i writing value=%i" % (x, value) 	
		ds3231.write_AT24C32_byte(x, value)
	print "----------------- "
	
	print "reading first 4 addresses"
	for x in range(0,4):
		print "address = %i value = %i" %(x, ds3231.read_AT24C32_byte(x)) 
	print "----------------- "

except IOError as e:
	#    print "I/O error({0}): {1}".format(e.errno, e.strerror)
	config.DS3231_Present = False
	# do the AT24C32 eeprom

	
################

# BMP280 Setup

try:
	bmp280 = BMP280.BMP280()
	config.BMP280_Present = True

except IOError as e:

	#    print "I/O error({0}): {1}".format(e.errno, e.strerror)
	config.BMP280_Present = False

################

# HTU21DF Detection 
try:
	HTU21DFOut = subprocess.check_output(["htu21dflib/htu21dflib","-l"])
	config.HTU21DF_Present = True
except:
	config.HTU21DF_Present = False

################

# OLED SSD_1306 Detection

try:
	RST =27
	display = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
	# Initialize library.
	display.begin()
	display.clear()
	display.display()
	config.OLED_Present = True
except:
	config.OLED_Present = False

################

# ad3935 Set up Lightning Detector
if (config.Lightning_Mode == True):
	# switch to BUS1 - lightning detector is on Bus1
	tca9545.write_control_register(TCA9545_CONFIG_BUS1)

	as3935 = RPi_AS3935(address=0x03, bus=1)

	try:

		as3935.set_indoors(True)
		config.AS3935_Present = True
		print "as3935 present"

	except IOError as e:

    		#    print "I/O error({0}): {1}".format(e.errno, e.strerror)
    		config.AS3935_Present = False
		# back to BUS0
		tca9545.write_control_register(TCA9545_CONFIG_BUS0)


	if (config.AS3935_Present == True):
		i2ccommand = "sudo i2cdetect -y 1"	
		output = subprocess.check_output (i2ccommand,shell=True, stderr=subprocess.STDOUT )
		print output
		as3935.set_noise_floor(0)
		as3935.calibrate(tun_cap=0x0F)

	as3935LastInterrupt = 0
	as3935LightningCount = 0
	as3935LastDistance = 0
	as3935LastStatus = ""
	# back to BUS0
	tca9545.write_control_register(TCA9545_CONFIG_BUS0)

	

def respond_to_as3935_interrupt():
    # switch to BUS1 - lightning detector is on Bus1
    print "in respond to as3935 interrupt"
    tca9545.write_control_register(TCA9545_CONFIG_BUS1)
    time.sleep(0.003)
    global as3935, as3935LastInterrupt, as3935LastDistance, as3935LastStatus
    reason = as3935.get_interrupt()
    as3935LastInterrupt = reason
    if reason == 0x01:
	as3935LastStatus = "Noise Floor too low. Adjusting"
        as3935.raise_noise_floor()
    elif reason == 0x04:
	as3935LastStatus = "Disturber detected - masking"
        as3935.set_mask_disturber(True)
    elif reason == 0x08:
        now = datetime.now().strftime('%H:%M:%S - %Y/%m/%d')
        distance = as3935.get_distance()
	as3935LastDistance = distance
	as3935LastStatus = "Lightning Detected "  + str(distance) + "km away. (%s)" % now
    # switch back to BUS0 
    tca9545.write_control_register(TCA9545_CONFIG_BUS0)
    #GPIO.add_event_detect(as3935pin, GPIO.RISING, callback=handle_as3935_interrupt)



if (config.Lightning_Mode == True):
	as3935pin = 13

	if (config.AS3935_Present == True):
		GPIO.setup(as3935pin, GPIO.IN)
		GPIO.add_event_detect(as3935pin, GPIO.RISING)
		#GPIO.add_event_detect(as3935pin, GPIO.RISING, callback=handle_as3935_interrupt)

###############
	
# Set up FRAM 

fram = SDL_Pi_FRAM.SDL_Pi_FRAM(addr = 0x50)
# FRAM Detection 
try:
	fram.read8(0)
	config.FRAM_Present = True
except:
	config.FRAM_Present = False

###############

# Detect AM2315 
try:
	from tentacle_pi.AM2315 import AM2315
	try:
		am2315 = AM2315(0x5c,"/dev/i2c-1")
		temperature, humidity, crc_check = am2315.sense()
		print "AM2315 =", temperature
		config.AM2315_Present = True
	except:
		config.AM2315_Present = False
except:
	config.AM2315_Present = False
	print "------> See Readme to install tentacle_pi"





# Main Loop - sleeps 10 seconds
# Tests all I2C devices on Weather Board 


# Main Program

print ""
print "Weather Board Demo / Test Version 1.5 - SwitchDoc Labs"
print ""
print ""
print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
print ""

totalRain = 0


print "----------------------"
print returnStatusLine("DS3231",config.DS3231_Present)
print returnStatusLine("BMP280",config.BMP280_Present)
print returnStatusLine("FRAM",config.FRAM_Present)
print returnStatusLine("HTU21DF",config.HTU21DF_Present)
print returnStatusLine("AM2315",config.AM2315_Present)
print returnStatusLine("ADS1015",config.ADS1015_Present)
print returnStatusLine("ADS1115",config.ADS1115_Present)
print returnStatusLine("AS3935",config.AS3935_Present)
print returnStatusLine("OLED",config.OLED_Present)
print "----------------------"







while True:


	if (config.Lightning_Mode == True):
    		# switch to BUS0
		print "switch to Bus0"
    		tca9545.write_control_register(TCA9545_CONFIG_BUS0)

	print "---------------------------------------- "
	print "----------------- "
	if (config.DS3231_Present == True):
		print " DS3231 Real Time Clock"
	else:
		print " DS3231 Real Time Clock Not Present"
	
	print "----------------- "
	#

	if (config.DS3231_Present == True):
		currenttime = datetime.utcnow()

		deltatime = currenttime - starttime
	 
		print "Raspberry Pi=\t" + time.strftime("%Y-%m-%d %H:%M:%S")

		if (config.OLED_Present):
			Scroll_SSD1306.addLineOLED(display,"%s" % ds3231.read_datetime())

		print "DS3231=\t\t%s" % ds3231.read_datetime()
	
		print "DS3231 Temperature= \t%0.2f C" % ds3231.getTemp()
		print "----------------- "



	print "----------------- "
	print " WeatherRack Weather Sensors" 
	print "----------------- "
	#

 	currentWindSpeed = weatherStation.current_wind_speed()/1.6
  	currentWindGust = weatherStation.get_wind_gust()/1.6
  	totalRain = totalRain + weatherStation.get_current_rain_total()/25.4
  	print("Rain Total=\t%0.2f in")%(totalRain)
  	print("Wind Speed=\t%0.2f MPH")%(currentWindSpeed)
	if (config.OLED_Present):
		Scroll_SSD1306.addLineOLED(display,  ("Wind Speed=\t%0.2f MPH")%(currentWindSpeed))
		Scroll_SSD1306.addLineOLED(display,  ("Rain Total=\t%0.2f in")%(totalRain))
  		if (config.ADS1015_Present or config.ADS1115_Present):	
			Scroll_SSD1306.addLineOLED(display,  "Wind Dir=%0.2f Degrees" % weatherStation.current_wind_direction())

    	print("MPH wind_gust=\t%0.2f MPH")%(currentWindGust)
  	if (config.ADS1015_Present or config.ADS1115_Present):	
		print "Wind Direction=\t\t\t %0.2f Degrees" % weatherStation.current_wind_direction()
		print "Wind Direction Voltage=\t\t %0.3f V" % weatherStation.current_wind_direction_voltage()

	print "----------------- "
	print "----------------- "
	if (config.BMP280_Present == True):
		print " BMP280 Barometer"
	else:
		print " BMP280 Barometer Not Present"
	print "----------------- "

	if (config.BMP280_Present):
		print 'Temperature = \t{0:0.2f} C'.format(bmp280.read_temperature())
		print 'Pressure = \t{0:0.2f} KPa'.format(bmp280.read_pressure()/1000)
		print 'Altitude = \t{0:0.2f} m'.format(bmp280.read_altitude())
		print 'Sealevel Pressure = \t{0:0.2f} KPa'.format(bmp280.read_sealevel_pressure()/1000)
		if (config.OLED_Present):
			Scroll_SSD1306.addLineOLED(display, 'Press= \t{0:0.2f} KPa'.format(bmp280.read_pressure()/1000))
			if (config.HTU21DF_Present == False):
				Scroll_SSD1306.addLineOLED(display, 'InTemp= \t{0:0.2f} C'.format(bmp280.read_temperature()))
	print "----------------- "

	print "----------------- "
	if (config.AM2315_Present == True):
		print " AM2315 Temperature/Humidity Sensor"
	else:
		print " AM2315 Temperature/Humidity  Sensor Not Present"
	print "----------------- "

	if (config.AM2315_Present):
    		temperature, humidity, crc_check = am2315.sense()
    		print "AM2315 temperature: %0.1f" % temperature
    		print "AM2315 humidity: %0.1f" % humidity
    		print "AM2315 crc: %s" % crc_check
	print "----------------- "

	print "----------------- "
	if (config.HTU21DF_Present == True):
		print " HTU21DF Temp/Hum"
	else:
		print " HTU21DF Temp/Hum Not Present"
	print "----------------- "

	# We use a C library for this device as it just doesn't play well with Python and smbus/I2C libraries
	if (config.HTU21DF_Present):
		HTU21DFOut = subprocess.check_output(["htu21dflib/htu21dflib","-l"])
		splitstring = HTU21DFOut.split()

		HTUtemperature = float(splitstring[0])	
		HTUhumidity = float(splitstring[1])	
		print "Temperature = \t%0.2f C" % HTUtemperature
		print "Humidity = \t%0.2f %%" % HTUhumidity
		if (config.OLED_Present):
			Scroll_SSD1306.addLineOLED(display,  "InTemp = \t%0.2f C" % HTUtemperature)
	print "----------------- "

	print "----------------- "
	if (config.AS3935_Present):
		print " AS3935 Lightning Detector"
	else:
		print " AS3935 Lightning Detector Not Present"
	print "----------------- "

	if (config.AS3935_Present):
		if (GPIO.event_detected(as3935pin)):
			respond_to_as3935_interrupt()

		print "Last result from AS3935:"

		if (as3935LastInterrupt == 0x00):
			print "----No Lightning detected---"
		
		if (as3935LastInterrupt == 0x01):
			print "Noise Floor: %s" % as3935LastStatus
			as3935LastInterrupt = 0x00

		if (as3935LastInterrupt == 0x04):
			print "Disturber: %s" % as3935LastStatus
			as3935LastInterrupt = 0x00

		if (as3935LastInterrupt == 0x08):
			print "Lightning: %s" % as3935LastStatus
			as3935LightningCount += 1
			Scroll_SSD1306.addLineOLED(display, '')
			Scroll_SSD1306.addLineOLED(display, '---LIGHTNING---')
			Scroll_SSD1306.addLineOLED(display, '')
			as3935LastInterrupt = 0x00

		print "Lightning Count = ", as3935LightningCount
	print "----------------- "
	
	print "----------------- "
	if (config.FRAM_Present):
		print " FRAM Test"
	else:
		print " FRAM Not Present"
	print "----------------- "

        if (config.FRAM_Present):
		print "writing first 3 addresses with random data"
		for x in range(0,3):
			value = random.randint(0,255)
                	print "address = %i writing value=%i" % (x, value)
                	fram.write8(x, value)
        	print "----------------- "

        	print "reading first 3 addresses"
        	for x in range(0,3):
                	print "address = %i value = %i" %(x, fram.read8(x))
        print "----------------- "
	print


	print "Sleeping 10 seconds"
	time.sleep(10.0)


