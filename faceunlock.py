import cv2
import numpy as np
import os 
import MySQLdb
from rpi_lcd import LCD
from time import sleep
import string
from gpiozero import LED, Buzzer
import time, datetime
from picamera import PiCamera

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('../trainer/trainer.yml')
cascadePath = "../haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);

font = cv2.FONT_HERSHEY_SIMPLEX

#iniciate id counter
id = 0

def greenLED():
	greenled = LED(24)
	greenled.on()
	sleep(1)
	greenled.off()
	greenled.close()
def buzzer():
	buzz = Buzzer(21)
	buzz.on()
	sleep(1)
	buzz.off()
	buzz.close()
	

try:
	db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
	curs = db.cursor()
	print("Successfully connected to database!")
except:
	print("Error connecting to mySQL database")

sql = "SELECT Username FROM assignment.Users"
curs.execute(sql)
result = curs.fetchall()
userslist = ['None']

for x in result:
	userslist.append(result[0][0])

print(userslist)

sql = "SELECT FaceScanConfidence FROM assignment.Security"
curs.execute(sql)
result = curs.fetchall()
setconfidence = int(result[0][0])

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

lcd = LCD()
lcd.text('Scanning...', 1)
starttime = time.time()
while True:
	confidentint = 0
	ret, img =cam.read()
	img = cv2.flip(img, -1) # Flip vertically
	
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	faces = faceCascade.detectMultiScale( 
		gray,
		scaleFactor = 1.2,
		minNeighbors = 5,
		minSize = (int(minW), int(minH)),
		)
	
	for(x,y,w,h) in faces:
		cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
		id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
		
		# Check if confidence is less them 100 ==> "0" is perfect match 
		if (confidence < 100):
			id = userslist[id]
			confidentint = round(100 - confidence)
			print(confidentint)
			confidence = "  {0}%".format(round(100 - confidence))
		else:
			id = "unknown"
			confidence = "  {0}%".format(round(100 - confidence))
        
		cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
		cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  

	#cv2.imshow('camera',img) 
	if confidentint > setconfidence:
		lcd.text('Identity', 1)
		lcd.text('Confirmed!', 2)
		greenLED()
		buzzer()
		sleep(2)
		lcd.text('Welcome, {}!'.format(id),  1)
		sleep(1)
		lcd.text('Safe Room', 1)
		lcd.text('Unlocked!', 2)
		sleep(5)
		lcd.clear()				
		try:
			print(id)
			sql = "SELECT UserID FROM assignment.Users WHERE Username = '%s'" % (id)
			curs.execute(sql)
			result = curs.fetchall()
			for x in result:
				userid = x[0]
			sql = "INSERT into UserLog(UserID) VALUES (%d)" % (int(userid))
			print(sql)
			curs.execute(sql)
			db.commit()
			print('\nDatabase Modified')
			cam.release()
			cv2.destroyAllWindows()
		except MySQLdb.Error as e:
			print(e)
		break
		
	nowtime = time.time()
	timediff = nowtime - starttime
	print(timediff)
	if timediff > 30:
		cam.release()
		cv2.destroyAllWindows()
		lcd.text('Identity', 1)
		lcd.text('Unconfirmed!', 2)
		sleep(5)
		try:
			name = datetime.datetime.now()
			sql = "INSERT into FailedEntryLog(DateTime) VALUES ('%s')" % (name)
			print(sql)
			curs.execute(sql)
			db.commit()
			print('\nDatabase Modified')
			camera = PiCamera()
			camera.capture('../captures/{}.jpg'.format(name))
		except MySQLdb.Error as e:
			print(e)
		break

lcd.clear()
import startprogram