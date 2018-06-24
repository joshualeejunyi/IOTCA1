from gpiozero import Button, Buzzer, LED
from rpi_lcd import LCD
from time import sleep
import subprocess
import MySQLdb

subprocess.call(["sudo", "modprobe", "bcm2835-v4l2"])
lcd = LCD()
btn1 = Button(13, pull_up=False)
btn2 = Button(5, pull_up=False)
buzz = Buzzer(21)
greenled = LED(24)
redled = LED(18)

try:
	db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
	curs = db.cursor()
	print("Successfully connected to database!")
except:
	print("Error connecting to mySQL database")


sql = "SELECT Passcode FROM assignment.Security WHERE ID = 1"
curs.execute(sql)
result = curs.fetchall()
result = result[0][0]
password = [int(i) for i in str(result)]
print(password)
userpass = []


def buttonOne():
	print("Button 1 pressed")
	userPass(1)
	
def buttonTwo():
	print("Button 2 pressed")
	userPass(2)
	
def userPass(number):
	print("Number received: " + str(number))
	userpass.append(number)
	print(userpass)

def checkPass(userpass, password):
	#print("CHECKING PASSWORD: " + str(userpass))'
	if userpass == password:
		result = True
	else:
		result = False
		
	return result
	
while True:
	lcd.text('Please Enter \nPasscode!', 1)
	btn1.when_pressed = buttonOne
	btn2.when_pressed = buttonTwo
	
	if len(userpass) == len(password):
		lcd.clear()
		lcd.text('Authenticating...', 1)
		sleep(1)
		result = checkPass(userpass, password)
		
		if result is True:
			lcd.text('Passcode', 1)
			lcd.text('Correct!', 2)
			buzz.on()
			greenled.on()
			sleep(2)
			greenled.off()
			buzz.off()
			lcd.text('Initializing', 1)
			lcd.text('Face Scan...', 2)
			break
		else:
			lcd.text('Passcode', 1)
			lcd.text('Incorrect!', 2)
			buzz.on()
			redled.on()
			sleep(2)
			redled.off()
			buzz.off()
			userpass = []
	elif len(userpass) > len(password):
		lcd.clear()
		lcd.text('Please Try Again', 1)
		sleep(1)
		userpass = []
		
redled.close()
greenled.close()
buzz.close()
btn1.close()
btn2.close()
import faceunlock