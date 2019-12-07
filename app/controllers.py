"""This module will serve the api request."""
import os, ast, imp, json, datetime, sys
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

# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')

# Select the database
db = client['api']
# Select the collection
usersCol = db['users']
suspectsCol = db['suspects']
resultsCol = db['results']

@app.route('/', methods=['GET'])
def mainPage():
    return jsonify({"message": "I'm alive."})

@app.route('/videos', methods=['GET'])
@login_required
def get_videos():
    try:
        userVideos = usersCol.distinct("results.local", {"userid": authenticated_user})
        print(authenticated_user)
        if (userVideos == None):
            result  = "User not found!"
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
        storedUser = usersCol.find_one({"userid": authenticated_user})
        print(request.files)
        if 'file' not in request.files:
            print('POST_VIDEO> ERROR: File not received')
            return {'message': 'missing file'}, 400
        
        filename = request.files['file'].filename
        newVideo = {
            "title": filename,
            "local": str(os.path.join(VIDEOS_UPLOAD_FOLDER, filename)),
            "timestamp": datetime.datetime.utcnow()
        }

        saveFile = upload_file(request.files['file'], "video")
        
        recognizationResult = recognizer.recognize(filename)
        delete_suspects()

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
                usersCol.insert_one({"userid": authenticated_user, "videos": videosArr})
                result = "Success"
        else:
            result = saveFile

        return str(result), 200
    except Exception as e:
        print(e, " at line ", sys.exc_info()[-1].tb_lineno)
        return "Server Error", 500

@app.route('/results', methods=['GET'])
# @login_required
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
            result =  "Suspects not found!"
        else:
            return send_file(findSuspects, mimetype='image/jpg')

        return jsonify(result), 200
    except Exception as e:
        print(e)
        return "Server Error", 500

@app.route('/suspects', methods=['POST'])
@login_required
def post_suspects():
    try:
        if ('file' in request.files):

            for file in request.files.getlist('file'):

                storedSuspect = suspectsCol.find_one({})
                newSuspect = {
                    "title": file.filename,
                    "local": str(os.path.join(DATABASE_UPLOAD_FOLDER, file.filename)),
                    "timestamp": datetime.datetime.utcnow()
                }

                saveFile = upload_file(file, "image")

                if (saveFile == "Success"):
                    if(storedSuspect != None):
                        result = suspectsCol.update({"_id": storedSuspect['_id']},
                            {"$push": {"suspects": newSuspect}},
                            upsert=True)
                    else:
                        suspectsArr = []
                        suspectsArr.append(newSuspect)
                        result = suspectsCol.insert({"suspects": suspectsArr})
                else: 
                    result = saveFile

            # AI execution
            for suspectId in get_suspects_ids():
                print(suspectId)
                preparer.prepare(int(suspectId))
            trainer.train()

            return str(result), 200
        else:
            return "Missing Parameter", 400
    except Exception as e:
        print(e)
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

def upload_file(file, type):
    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if type == "video":
                uploadFolder = os.path.join(currentDir, VIDEOS_UPLOAD_FOLDER)
                try:
                    file.save(os.path.join(uploadFolder, filename))
                except:
                    os.mkdir(uploadFolder)
                    file.save(os.path.join(uploadFolder, filename))
            else:
                suspectsUploadFolder = os.path.join(currentDir, SUSPECTS_UPLOAD_FOLDER)
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
    return result
        
def delete_suspects():
    try:
        for filename in os.listdir(SUSPECTS_UPLOAD_FOLDER):
            sh.copy(SUSPECTS_UPLOAD_FOLDER + filename, DATABASE_UPLOAD_FOLDER + filename)
            os.remove(SUSPECTS_UPLOAD_FOLDER + filename)
    except:
        print('Creating suspects directory')
        os.mkdir(os.path.join(currentDir, SUSPECTS_UPLOAD_FOLDER))
    