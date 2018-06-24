import datetime
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
import MySQLdb

gevent.monkey.patch_all()

from flask import Flask, request, Response, render_template
from gpiozero import LED

led = LED(26)

def ledOn():
	led.on()
	return "Room Light is on."

def ledOff():
	led.off()
	return "Room Light is off"

def ledStatus():
	if led.is_lit:
		return 'On'
	else:
		return 'Off'

app = Flask(__name__)

@app.route("/")
def index():
	return render_template('index.html')


@app.route("/readLED/")
def readPin():
	response = ledStatus()
	templateData = {
		'title' : 'Status of LED: ',
		'response' : response
	}

	return render_template('pin.html', **templateData)

@app.route("/writeLED/<status>")
def writePin(status):
	if status == 'On':
		response = ledOn()
	else:
		response = ledOff()
	
	templateData = {
		'title' : 'Status of LED',
		'response' : response
	}

	return render_template('pin.html', **templateData)

@app.route("/viewAtmosphere/")
@app.route("/viewAtmosphere/realtime/")
def viewAtmosphereRT():
	try:
		db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
		curs = db.cursor()
		print("Successfully connected to database!")
	except:
		print("Error connecting to mySQL database")
		
	query = "SELECT datetimevalue, temperature, humidity FROM atmosphere ORDER BY datetimevalue DESC LIMIT 10"
	curs.execute(query)
	data = []
	
	for (datetimevalue, temperature, humidity) in curs:
		d = []
		d.append("{:%H:%M:%S}".format(datetimevalue))
		d.append(temperature)
		d.append(humidity)
		data.append(d)	 
	print(data)
	data_reversed = data[::-1]
	
	return render_template('atmosphere.html', data=data_reversed)


@app.route("/viewAtmosphere/historic/")
def viewAtmosphereHistoricRouter():
	return render_template('router.html')
	
@app.route("/viewAtmosphere/historic/<date>")
def viewAtmosphereHistoric(date):
	date = str(date)
	try:
		db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
		curs = db.cursor()
		print("Successfully connected to database!")
	except:
		print("Error connecting to mySQL dacon.tabase")
		
	query = "SELECT datetimevalue, temperature, humidity FROM atmosphere WHERE DATE(datetimevalue) = '%s' " % (date)
	print(query)
	curs.execute(query)
	data = []
	
	for (datetimevalue, temperature, humidity) in curs:
		d = []
		d.append("{:%H:%M:%S}".format(datetimevalue))
		d.append(temperature)
		d.append(humidity)
		data.append(d)	 
	print(data)
	data_reversed = data[::-1]
	
	return render_template('atmosphere.html', data=data_reversed)	
	
@app.route("/viewUserLogs/")
def viewUserLogs():
	try:
		db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
		curs = db.cursor()
		print("Successfully connected to database!")
	except:
		print("Error connecting to mySQL dacon.tabase")
		
	query = "SELECT u.Username, l.DateTime FROM Users u INNER JOIN UserLog l ON u.UserID = l.UserID;"
	print(query)
	curs.execute(query)
	data = []
	for (username, datetime) in curs:
		d = []
		d.append(username)
		d.append(datetime)
		data.append(d)	 
	print(data)
	data_reversed = data[::-1]
	
	return render_template('userlog.html', data=data_reversed)	
	
@app.route("/viewFailedEntryLogs/")
def viewFailedEntryLogs():
	try:
		db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
		curs = db.cursor()
		print("Successfully connected to database!")
	except:
		print("Error connecting to mySQL dacon.tabase")
		
	query = "SELECT DateTime, PictureID from FailedEntryLog;"
	curs.execute(query)
	data = []
	for (datetime, pictureid) in curs:
		d = []
		d.append(datetime)
		d.append(pictureid)
		data.append(d)
	print(data)
	data_reversed = data[::-1]
	
	return render_template('failedlogs.html', data=data_reversed)	

@app.route("/changePassword/")
def changePassword():
	return render_template('changepassword.html')
	
@app.route("/changePassword/<password>")
def changePasswordDB(password):
	password = int(password)
	print(password)
	try:
		db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
		curs = db.cursor()
		print("Successfully connected to database!")
	except:
		print("Error connecting to mySQL database")

	try:
		sql = "UPDATE Security SET Passcode = %d WHERE ID = 1;" % (password)
		print(sql)
		curs.execute(sql)
		db.commit()
		print('\nDatabase Modified')
	except MySQLdb.Error as e:
		print(e)
	return render_template('passwordchanged.html')

@app.route("/registerFace/")
def registerFaceForm():
	return render_template('facescan.html')

@app.route('/registerFace/<userid>/<username>')
def registerFace(userid, username):
	from faceid import face
	face(userid)
	
	try:
		db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
		curs = db.cursor()
		print("Successfully connected to database!")
	except:
		print("Error connecting to mySQL database")

	try:
		sql = "INSERT into Users(UserID, Username) VALUES ('%d', '%s')" % (int(userid), str(username))
		curs.execute(sql)
		db.commit()
		print('\nDatabase Modified')
	except MySQLdb.Error as e:
		print(e)
	
	return render_template('faceregistered.html')


@app.route("/changeFaceUnlockConfidence/")
def changeConfidence():
	return render_template('changeconfidence.html')
	
@app.route("/changeFaceUnlockConfidence/<value>")
def changeConfidenceDB(value):
	value = int(value)
	try:
		db = MySQLdb.connect("localhost", "assignmentuser", "joshsmartroom", "assignment")
		curs = db.cursor()
		print("Successfully connected to database!")
	except:
		print("Error connecting to mySQL database")

	try:
		sql = "UPDATE Security SET FaceScanConfidence = %d WHERE ID = 1;" % (value)
		print(sql)
		curs.execute(sql)
		db.commit()
		print('\nDatabase Modified')
	except MySQLdb.Error as e:
		print(e)
	return render_template('confidencechanged.html')

	
if __name__ == '__main__':
	try:
		http_server = WSGIServer(('0.0.0.0', 8001), app)
		app.debug = True
		http_server.serve_forever()
	except:
		print("Exception")