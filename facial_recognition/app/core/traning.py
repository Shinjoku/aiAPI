import cv2
import os, sys
import numpy as np


def train():
    try:

        # Recognizers: Eigen, Fisher and LBPH
        eigenface = cv2.face.EigenFaceRecognizer_create(num_components=50)
        fisherface = cv2.face.FisherFaceRecognizer_create(num_components=50)
        lbph = cv2.face.LBPHFaceRecognizer_create(4, 8, 8, 8, 115)

        # Retrieve faces images and the culprits id
        def getImageAndId():
            imagePaths = [os.path.join('assets/faces', f)
                        for f in os.listdir('assets/faces')]
            faces = []
            ids = []

            for path in imagePaths:
                face = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2GRAY)
                id = int(os.path.split(path)[-1].split('.')[1])
                ids.append(id)
                faces.append(face)
            return np.array(ids), faces

        ids, faces = getImageAndId()
        print("TRAINER> The train has begun.")
        print("TRAINER> No of photos: ", len(faces))

        eigenface.train(faces, ids)
        eigenface.write('facial_recognition/EigenClassifier.yml')

        # fisherface.train(faces, ids)
        # fisherface.write('FisherClassifier.yml')

        lbph.train(faces, ids)
        lbph.write('facial_recognition/LBPHClassifier.yml')

        print("TRAINER> Train executed successfully.")

    except Exception as e:
        print(e, " at line ", sys.exc_info()[-1].tb_lineno)
