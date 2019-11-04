import cv2
import time
import math

def recognize(filename):

    videosBaseUrl = 'assets\\videos\\'
    suspects = {}

    print('RECOGNIZER> The recognition has begun.')
    # Classifier, currently using frontal image only
    faceClassifier = cv2.CascadeClassifier("facial_recognition\\app\\cascades\\haarcascade_frontalface_default.xml")

    # Reconizers, to use the other two, uncomment them and comment the ones left

    #recognizer = cv2.face.FisherFaceRecognizer_create()
    #recognizer.read("FisherClassifier.yml")
    # recognizer = cv2.face.EigenFaceRecognizer_create()
    # recognizer.read("EigenClassifier.yml")
    recognizer = cv2.face.LBPHFaceRecognizer_create(radius=4, threshold= 125)
    recognizer.read("facial_recognition/LBPHClassifier.yml")

    imageWidth, imageHeight = 220, 220
    suspectName = ""
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL

    # Video input
    capturedVideo = cv2.VideoCapture(videosBaseUrl + filename)

    # Error Handling
    if not capturedVideo.isOpened():
        print("Error opening video stream or file")

    frameNumber = 0
    initialTime = time.time()
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

                    elapsedMiliseconds = math.trunc((time.time() - initialTime) * 1000)

                    if(suspectName in suspects):
                        suspect = suspects[suspectName]
                        miliseconds = suspect['miliseconds']

                        if(suspect['records'] < 3):
                            miliseconds.append(elapsedMiliseconds)
                            suspects[suspectName] = {
                                "miliseconds": miliseconds,
                                "records": suspect['records'] + 1
                            }
                    else:
                        suspects[suspectName] = {
                            "miliseconds": [elapsedMiliseconds],
                            "records": 1
                        }

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

    videoResult = {
        "video": filename,
        "suspects": suspects
    }

    print('RECOGNIZER> Recognition executed successfully.')

    return videoResult
