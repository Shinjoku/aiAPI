"""This module will serve the api request."""
import os
import ast
import imp
import json
import datetime
import sys
from bson.json_util import dumps
from config import client
from app import app
from flask import request, jsonify, send_file, g, send_from_directory, url_for
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
BASE_FOLDER = './static/assets/'
DATABASE_UPLOAD_FOLDER = BASE_FOLDER + "database/"
SUSPECTS_UPLOAD_FOLDER = BASE_FOLDER + 'suspects/'
VIDEOS_UPLOAD_FOLDER = BASE_FOLDER + 'videos/'
FACES_UPLOAD_FOLDER = BASE_FOLDER + 'faces/'

# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')

# Select the database
db = client['api']
# Select the collection
usersCol = db['users']
suspectsCol = db['suspects']
resultsCol = db['results']
nextSuspectIdCol = db['nextSuspectId']


@app.route('/', methods=['GET'])
def mainPage():
    return jsonify({"message": "I'm alive."})


@app.route('/videos', methods=['GET'])
@login_required
def get_videos():
    try:
        userVideos = usersCol.distinct(
            "results.local", {"userid": g.user})
        if (userVideos == None):
            result = "User not found!"
        else:
            result = userVideos

        return jsonify(result), 200

    except Exception as e:
        print(e)
        return "Server Error", 500


@app.route('/video', methods=['POST'])
@login_required
def post_video():
    try:
        storedUser = usersCol.find_one({"userid": g.user})
        if 'file' not in request.files:
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

        return jsonify({"message": result}), 200
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
@login_required
def post_suspect():
    result = "standard"

    if 'user' not in request.form:
        return "Unauthorized", 401
    try:
        if ('files' in request.files and 'suspectName' in request.form):
            suspectName = request.form['suspectName']
            nextId = nextSuspectIdCol.find_one({})['nextId']

            newSuspect = {
                "suspectId": nextId,
                "name": suspectName,
                'local': [],
                "timestamp": datetime.datetime.utcnow()
            }

            i = 0
            for file in request.files.getlist('files'):

                print("nextId: ", nextId)
                fileExtension = file.filename.split('.')[-1]
                standardizedFileName = '%s.%s.%i.%s' % (
                    suspectName, nextId, i, fileExtension)

                saveFile = upload_file(file, standardizedFileName, "image")
                newSuspect['local'].append(standardizedFileName)
                i = i + 1

            if (saveFile == "Success"):
                suspectsCol.insert_one(newSuspect)
                nextSuspectIdCol.update({}, {"$set": {"nextId": nextId + 1}})
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


def static_filepath(local, filename):
    staticFolder = os.path.join('/static', 'assets')
    assetsFolder = os.path.join(staticFolder, local)
    full_filename = os.path.join(assetsFolder, filename)
    return full_filename


@app.route('/files/suspects/<filename>', methods=['GET'])
def get_suspect_image(filename):
    try:
        print(filename)
        path = static_filepath('database', filename)
        return '<img src="' + path + '">'
    except Exception as e:
        print(e, " at line ", sys.exc_info()[-1].tb_lineno)
        return jsonify({"message": "This file doesn`t exist"}), 500


@app.route('/files/screenshots/<filename>', methods=['GET'])
def get_screenshots_image(filename):
    try:
        print(filename)
        path = static_filepath('screenshots', filename)
        return '<img src="' + path + '">'
    except Exception as e:
        print(e, " at line ", sys.exc_info()[-1].tb_lineno)
        return jsonify({"message": "This file doesn`t exist"}), 500


@app.route('/files/videos/<filename>', methods=['GET'])
def get_suspect_video(filename):
    try:
        print(filename)
        extension = filename.split('.')[-1]
        path = static_filepath('videos', filename)
        return (
            ''' 
            <video controls=controls>
                <source src="''' + path + '''" type="video/''' + extension + '''">
            </video> 
        ''')
    except Exception as e:
        print(e, " at line ", sys.exc_info()[-1].tb_lineno)
        return jsonify({"message": "This file doesn`t exist"}), 500


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
