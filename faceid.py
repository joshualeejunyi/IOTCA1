import cv2, os, string, MySQLdb, subprocess

def face(userid):
	subprocess.call(["sudo", "modprobe", "bcm2835-v4l2"])
	cam = cv2.VideoCapture(0)
	cam.set(3, 640) # set video width
	cam.set(4, 480) # set video height

	facedetector = cv2.CascadeClassifier('../haarcascades/haarcascade_frontalface_default.xml')

	print("\nInitializing Face Capture. Please look at the camera.")

	facecount = 0

	while(True):

		ret, img = cam.read()
		img = cv2.flip(img, -1) # flip video image vertically
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = facedetector.detectMultiScale(gray, 1.3, 5)

		for (x,y,w,h) in faces:

			cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
			facecount += 1
			progress = facecount / 30 * 100
			print("Progress: " + '{0:.2f}'.format(progress) +"%")

			# Save the captured image into the datasets folder
			cv2.imwrite("../data/UserID-" + str(userid) + '-' + str(facecount) + ".jpg", gray[y:y+h,x:x+w])
			
		k = cv2.waitKey(100) & 0xff
		if k == 27:
			break
		elif facecount >= 30:
			break

	print("\nCapture Complete")
	cam.release()
	cv2.destroyAllWindows()

	print("\nTraining Faces")
	import trainer