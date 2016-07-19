
#
# test scrolling OLED
#

import Adafruit_SSD1306

import Scroll_SSD1306
import time

RST = 24

# Note you can change the I2C address by passing an i2c_address parameter like:
display = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
# Initialize library.
display.begin()
display.clear()
display.display()


for i in range(0,30):
	Scroll_SSD1306.addLineOLED(display, "Hello there "+str(i))
	time.sleep(1)

