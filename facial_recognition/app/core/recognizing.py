import cv2
import time
import math
import os, sys

BASE_FOLDER = 'app/static/assets/'
VIDEOS_FOLDER = BASE_FOLDER + 'videos/'
SCREENSHOTS_UPLOAD_FOLDER = BASE_FOLDER + 'screenshots/'
SUSPECTS_UPLOAD_FOLDER =  BASE_FOLDER + 'suspects/'
DATABASE_UPLOAD_FOLDER =  BASE_FOLDER + 'database/'

"""
    Recognizes the suspects that are in the database
"""
def recognize(filename):
    videoResult = {}
    try:
        suspects = {}

        print('RECOGNIZER> The recognition has begun.')
        # Classifier, currently using frontal image only
        faceClassifier = cv2.CascadeClassifier(
            "facial_recognition/app/cascades/haarcascade_frontalface_default.xml")

        # Reconizers, to use the other two, uncomment them and comment the ones left

        #recognizer = cv2.face.FisherFaceRecognizer_create()
        # recognizer.read("FisherClassifier.yml")
        # recognizer = cv2.face.EigenFaceRecognizer_create()
        # recognizer.read("EigenClassifier.yml")
        recognizer = cv2.face.LBPHFaceRecognizer_create(radius=4, threshold=125)
        recognizer.read("facial_recognition/LBPHClassifier.yml")

        imageWidth, imageHeight = 220, 220
        suspectName = ""
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL

        # Video input
        video_path = VIDEOS_FOLDER + filename
        print(video_path)
        capturedVideo = cv2.VideoCapture(video_path)

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
                frame = cv2.resize(
                    frame, (int(newVideoWidth), int(newVideoHeight)))

                # Prepare frame
                grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces in frame
                detectedFaces = faceClassifier.detectMultiScale(
                    grayFrame, scaleFactor=1.5, minSize=(30, 30))

                for (x, y, l, a) in detectedFaces:
                    # Resize face and predict who it is
                    face = cv2.resize(
                        grayFrame[y:y + a, x:x + l], (imageWidth, imageHeight))
                    faceId, confidence = recognizer.predict(face)

                    # If a known culprit its identified, compare its Id with database name
                    # (currently hardcoding the names...)
                    if faceId != -1:
                        suspectsIds = get_suspects_dict()
                        if faceId in suspectsIds:
                            suspectName = suspectsIds[faceId]
                        else:
                            continue

                        elapsedMiliseconds = math.trunc(
                            (time.time() - initialTime) * 1000)

                        if(suspectName in suspects):
                            suspect = suspects[suspectName]
                            print("RECOGNIZER> Suspect found: ", suspectName)
                            miliseconds = suspect['miliseconds']

                            if(suspect['records'] < 3):
                                suspectMoment = os.path.join(
                                    SCREENSHOTS_UPLOAD_FOLDER,
                                    '%i.%s.%i.png' % ( faceId, filename, suspect['records'] + 1))

                                cv2.imwrite(suspectMoment, frame)

                                miliseconds.append(elapsedMiliseconds)
                                suspects[suspectName] = {
                                    "miliseconds": miliseconds,
                                    "picture": suspectMoment,
                                    "records": suspect['records'] + 1
                                }
                        else:
                            suspectMoment = os.path.join(
                                SCREENSHOTS_UPLOAD_FOLDER,
                                '%i.%s.1.png' % ( faceId, filename))

                            cv2.imwrite(suspectMoment, frame)
                            miliseconds = []
                            miliseconds.append(elapsedMiliseconds)

                            suspects[suspectName] = {
                                "miliseconds": [elapsedMiliseconds],
                                "picture": suspectMoment,
                                "records": 1
                            }

            # Break the loop
            else:
                break

        # When everything is done, release the video capture object
        capturedVideo.release()

        # Closes all the frames
        cv2.destroyAllWindows()

        videoResult = {
            "suspects": suspects
        }
    except Exception as e:
        print('RECOGNIZER>', e, " at line ", sys.exc_info()[-1].tb_lineno)

    print('RECOGNIZER> Recognition executed successfully.')

    return videoResult


"""
    Retrieves all suspects and their respective ids
"""
def get_suspects_dict():
    result = {}
    for imgName in os.listdir(DATABASE_UPLOAD_FOLDER):
        suspectInfos = imgName.split('.')
        suspectId = int(suspectInfos[1])
        suspectName = suspectInfos[0]

        if(suspectId not in result):
            result[suspectId] = suspectName

    return result
