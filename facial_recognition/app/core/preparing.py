import cv2
import os
import numpy as np

def prepare(id):
    # .XML classifiers

    faceClassifier = cv2.CascadeClassifier('facial_recognition/app/cascades/haarcascade_frontalface_default.xml')
    eyeClassifier = cv2.CascadeClassifier('facial_recognition/app/cascades/haarcascade_eye.xml')

    # Global Variables ( :/ ) 
    imageWidth, imageHeight = 220, 220
    imageCount = 1
    imagePaths = [os.path.join('assets/suspects', f) for f in os.listdir('assets/suspects')]

    # Receive current suspect Id
    print('Suspect identifier: ', id)

    print("PREPARER> The preparation has begun.")
    # for each image path:
    for path in imagePaths:
        # read image, prepare it and detect faces
        image = cv2.imread(path)
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        detectedFaces = faceClassifier.detectMultiScale(grayImage, scaleFactor=1.5, minSize=(100, 100))

        # for each deteced face:
        for (x, y, l, a) in detectedFaces:
            # prepare image and detect eyes
            faceRegion = image[y:y + a, x:x + l]
            grayFaceRegion = cv2.cvtColor(faceRegion, cv2.COLOR_BGR2GRAY)
            detectedEyes = eyeClassifier.detectMultiScale(grayFaceRegion)

            # if there were detected eyes, save the face image
            if len(detectedEyes):
                faceImage = cv2.resize(grayImage[y:y + a, x:x + l], (imageWidth, imageHeight))
                cv2.imwrite("assets/faces/suspect." + str(id) + "." + str(imageCount) + ".jpg", faceImage)
                
                print("[ " + str(id) + " face " + str(imageCount) + " prepared ]")
                
                imageCount += 1

    print("PREPARER> Prepare executed successfully.")
