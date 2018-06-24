import sys
import Adafruit_DHT
from gpiozero import Button, LED, Button
import time
from time import sleep
import MySQLdb

pin = 4
yellowled = LED(26)
button = Button(5)

def ledToggle():
	yellowled.toggle()

try:
	db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
	curs = db.cursor()
	print("Successfully connected to database!")
except:
	print("Error connecting to mySQL database")


def atmosphere(temperature, humidity):
	try:
		sql = "INSERT into atmosphere (temperature, humidity) VALUES ('%s', '%s')" % (temperature, humidity)
		print(sql)
		curs.execute(sql)
		db.commit()
	except Exception:
		print(Exception)

initialtime = time.time()

while True:
	button.when_pressed = ledToggle
	humidity, temperature = Adafruit_DHT.read_retry(11, pin)
	atmosphere(temperature, humidity)
	sleep(5)