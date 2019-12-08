"""This module will serve the api request."""
import os
import ast
import imp
import json
import datetime
import sys
from bson.json_util import dumps
from config import client, authenticated_user
from app import app
from flask import request, jsonify, send_file
from datetime import date
from werkzeug.utils import secure_filename
from random import randrange
import shutil as sh
from .middlewares import login_required
import facial_recognition.app.core.preparing as preparer
import facial_recognition.app.core.traning as trainer
import facial_recognition.app.core.recognizing as recognizer


currentDir = os.getcwd()
print(currentDir)

# Allowed files extensions
ALLOWED_EXTENSIONS = set(["mov", "jpg", "png", "mp4"])

# Folder locations for uploads
DATABASE_UPLOAD_FOLDER = "assets/database/"
SUSPECTS_UPLOAD_FOLDER = "assets/suspects/"
VIDEOS_UPLOAD_FOLDER = "assets/videos/"
FACES_UPLOAD_FOLDER = "assets/faces/"

# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')

# Select the database
db = client['api']
# Select the collection
usersCol = db['users']
suspectsCol = db['suspects']
resultsCol = db['results']
number_of_suspects = db['suspectsNo']


@app.route('/', methods=['GET'])
def mainPage():
    return jsonify({"message": "I'm alive."})


@app.route('/videos', methods=['GET'])
@login_required
def get_videos():
    try:
        userVideos = usersCol.distinct(
            "results.local", {"userid": authenticated_user})
        print(authenticated_user)
        if (userVideos == None):
            result = "User not found!"
        else:
            result = userVideos

        return jsonify(result), 200

    except Exception as e:
        print(e)
        return "Server Error", 500


@app.route('/video', methods=['POST'])
# @login_required
def post_video():
    try:
        if 'user' not in request.form:
            return "Unauthorized", 401

        storedUser = usersCol.find_one({"userid": request.form['user']})
        if 'files' not in request.files:
            print('POST_VIDEO> ERROR: File not received')
            return {'message': 'missing file'}, 400

        filename = request.files['file'].filename
        newVideo = {
            "title": filename,
            "local": str(os.path.join(VIDEOS_UPLOAD_FOLDER, filename)),
            "timestamp": datetime.datetime.utcnow()
        }

        saveFile = upload_file(request.files['file'], filename, "video")

        recognizationResult = recognizer.recognize(filename)

        newVideo["result"] = recognizationResult

        if (saveFile == "Success"):
            if(storedUser != None):
                usersCol.update({"_id": storedUser['_id']},
                                {"$push": {"videos": newVideo}},
                                upsert=True)
                result = "Success"
            else:
                videosArr = []

                # Store on DB
                videosArr.append(newVideo)
                usersCol.insert_one(
                    {"userid": request.form['user'], "videos": videosArr})
                result = "Success"
        else:
            result = saveFile

        return str(result), 200
    except Exception as e:
        print(e, " at line ", sys.exc_info()[-1].tb_lineno)
        return "Server Error", 500


@app.route('/results', methods=['GET'])
@login_required
def get_results():
    try:
        user = usersCol.find_one({"userid": "12334"})
        videos = user['videos']
        return jsonify(videos), 200

    except Exception as e:
        print(e, " at line ", sys.exc_info()[-1].tb_lineno)
        return "Server Error", 500


@app.route('/suspects', methods=['GET'])
@login_required
def get_suspects():
    try:
        findSuspects = suspectsCol.distinct("suspects.local")
        if (findSuspects == None):
            result = "Suspects not found!"
        else:
            return send_file(findSuspects, mimetype='image/jpg')

        return jsonify(result), 200
    except Exception as e:
        print(e)
        return "Server Error", 500

@app.route('/suspect', methods=['POST'])
# @login_required
def post_suspect():
    result="standard"

    if 'user' not in request.form:
        return "Unauthorized", 401
    try:
        print(request.files)
        if ('files' in request.files and 'suspectName' in request.form):
            suspectName = request.form['suspectName']
            i = 0
                        
            for file in request.files.getlist('files'):
                storedSuspect = suspectsCol.find_one({})
                nextId = int(storedSuspect['newId'])
                
                print("nextId: ", nextId)
                fileExtension = file.filename.split('.')[-1]
                standardizedFileName = '%s.%s.%i.%s' %  (suspectName, nextId, i, fileExtension)
                print("NOME RESULTANTE: ", standardizedFileName)
                
                newSuspect = {
                    "name": suspectName,
                    "suspectId": nextId,
                    "local": standardizedFileName,
                    "timestamp": datetime.datetime.utcnow()
                }

                standardizedFileName
                saveFile = upload_file(file, standardizedFileName, "image")
                
                if (saveFile == "Success"):
                    if(storedSuspect != None):
                        suspectsCol.update({"_id": storedSuspect['_id']},
                            {
                                "$push": {
                                    "suspects": newSuspect
                                },
                                "$set": {
                                    "newId": nextId + 1
                                }
                            },
                            upsert=True)
                        result = "Success"
                    else:
                        suspectsArr = []
                        suspectsArr.append(newSuspect)
                        suspectsCol.insert({"suspects": suspectsArr})
                        suspectsCol.update({storedSuspect['_id']}, {"$set": {"newId": nextId + 1}})
                        result = "Success"
                else:
                    return "Failed saving an image", 500

            # AI execution
            for suspectId in get_suspects_ids():
                preparer.prepare(int(suspectId))
            trainer.train()
            delete_suspects()

            return jsonify({"message": result}), 200
        else:
            return "Missing Parameter", 400
    except Exception as e:
        print(e, " at line ", sys.exc_info()[-1].tb_lineno)
        return "Server Error", 500


@app.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    # Message to the user
    message = {
        "err":
            {
                "msg": "This route is currently not supported."
            }
    }
    # Making the message looks good
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 404
    # Returning the object
    return resp


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file, name, type):
    try:
        if file and allowed_file(name):
            filename = secure_filename(name)
            if type == "video":
                uploadFolder = os.path.join(currentDir, VIDEOS_UPLOAD_FOLDER)
                try:
                    file.save(os.path.join(uploadFolder, filename))
                except:
                    os.mkdir(uploadFolder)
                    file.save(os.path.join(uploadFolder, filename))
            else:
                suspectsUploadFolder = os.path.join(
                    currentDir, SUSPECTS_UPLOAD_FOLDER)
                try:
                    file.save(os.path.join(suspectsUploadFolder, filename))
                except:
                    os.mkdir(suspectsUploadFolder)
                    file.save(os.path.join(uploadFolder, filename))
            return 'Success'
        else:
            return 'Extension not allowed'
    except Exception as e:
        return e


def get_suspects_ids():
    result = []
    for imgName in os.listdir(SUSPECTS_UPLOAD_FOLDER):
        suspectId = imgName.split('.')[1]
        if(suspectId not in result):
            result.append(suspectId)
    print("IDS ENCONTRADOS: ", result)
    return result


def delete_suspects():
    try:
        for filename in os.listdir(SUSPECTS_UPLOAD_FOLDER):
            sh.copy(SUSPECTS_UPLOAD_FOLDER + filename,
                    DATABASE_UPLOAD_FOLDER + filename)
            os.remove(SUSPECTS_UPLOAD_FOLDER + filename)

        for filename in os.listdir(FACES_UPLOAD_FOLDER):
            os.remove(FACES_UPLOAD_FOLDER + filename)
    except:
        print('Creating suspects directory')
        os.mkdir(os.path.join(currentDir, SUSPECTS_UPLOAD_FOLDER))
