import cv2

# Classifier, currently using frontal image only
faceClassifier = cv2.CascadeClassifier("app\\cascades\\haarcascade_frontalface_default.xml")

# Reconizers, to use the other two, uncomment them and comment the ones left

#recognizer = cv2.face.FisherFaceRecognizer_create()
#recognizer.read("FisherClassifier.yml")
#recognizer = cv2.face.EigenFaceRecognizer_create()
#recognizer.read("EigenClassifier.yml")
recognizer = cv2.face.LBPHFaceRecognizer_create(radius=4, threshold= 125)
recognizer.read("LBPHClassifier.yml")

imageWidth, imageHeight = 220, 220
suspectName = ""
font = cv2.FONT_HERSHEY_COMPLEX_SMALL

# Video input
capturedVideo = cv2.VideoCapture('assets\\videos\\all1.mov')

# Error Handling
if not capturedVideo.isOpened():
    print("Error opening video stream or file")

# Read until video is completed
while capturedVideo.isOpened():
    # Read video frame-by-frame
    videoReadSuccess, frame = capturedVideo.read()

    if videoReadSuccess:
        # Redefine videos size, for it to fit in the notebooks screen
        videoHeight, videoWidth, videoLayers = frame.shape
        newVideoHeight = int(videoHeight / 2)
        newVideoWidth = int(videoWidth / 2)
        frame = cv2.resize(frame, (int(newVideoWidth), int(newVideoHeight)))

        # Prepare frame
        grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in frame
        detectedFaces = faceClassifier.detectMultiScale(grayFrame, scaleFactor=1.5, minSize=(30, 30))

        for (x, y, l, a) in detectedFaces:
            # Resize face and predict who it is
            face = cv2.resize(grayFrame[y:y + a, x:x + l], (imageWidth, imageHeight))
            faceId, confidence = recognizer.predict(face)
            
            # If a known culprit its identified, compare its Id with database name
            # (currently hardcoding the names...)
            if faceId != -1:
                cv2.rectangle(frame, (x, y), (x + l, y + a), (0, 0, 255), 2)

                if faceId == 1:
                    suspectName = 'Breno'
                elif faceId == 2:
                    suspectName = 'Catarina'
                elif faceId == 3:
                    suspectName = 'Eduardo'
                elif faceId == 4:
                    suspectName = 'Gabriela'
                elif faceId == 5:
                    suspectName = 'Matheus'
                else:
                    suspectName = 'Gasparzinho'
                    
                cv2.putText(frame, suspectName, (x, y + (a + 30)), font, 2, (0, 0, 255))
                cv2.putText(frame, str(confidence), (x, y + (a + 50)), font, 1, (0, 0, 255))

        # Display the resulting frame
        cv2.resizeWindow('Frame', newVideoWidth, newVideoHeight)
        cv2.imshow('Frame', frame)

        # Press Q on keyboard to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            print("Error reading video stream or file")
            break

    # Break the loop
    else:
        break

# When everything is done, release the video capture object
capturedVideo.release()

# Closes all the frames
cv2.destroyAllWindows()
