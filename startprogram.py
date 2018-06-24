from gpiozero import Button
from rpi_lcd import LCD

btn2 = Button(5, pull_up=False)
lcd = LCD()
lcd.clear()
while True:
	lcd.text("Press Red Button", 1)
	lcd.text("To Initiate...", 2)
	response = btn2.wait_for_press()
	if response is True:
		break

lcd.clear()
btn2.close()
import password