import cv2
import os
import numpy as np

# Recognizers: Eigen, Fisher and LBPH
eigenface = cv2.face.EigenFaceRecognizer_create(num_components=50)
fisherface = cv2.face.FisherFaceRecognizer_create(num_components=50)
lbph = cv2.face.LBPHFaceRecognizer_create(4,8,8,8,115)


# Retrieve faces images and the culprits id
def getImageAndId():
    imagePaths = [os.path.join('assets\\faces', f) for f in os.listdir('assets\\faces')]
    faces = []
    ids = []

    for path in imagePaths:
        face = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2GRAY)
        id = int(os.path.split(path)[-1].split('.')[1])
        ids.append(id)
        faces.append(face)
    return np.array(ids), faces

ids, faces = getImageAndId()
print("Training...")

eigenface.train(faces, ids)
eigenface.write('EigenClassifier.yml')

fisherface.train(faces, ids)
fisherface.write('FisherClassifier.yml')

lbph.train(faces, ids)
lbph.write('LBPHClassifier.yml')

print("Traning Done!")
