# pip install flask
# flask run
import os
import cv2
import json
from flask import Flask, render_template, jsonify, Response, request, redirect, url_for
from werkzeug.utils import secure_filename
from templates.YOLOV8 import basic, testcount

DADOS_YOLO_PATH = "../ProjetoIntegradorV/templates/frontend/dados_yolo.json"
VIDEO_PATH = '../ProjetoIntegradorV/static/videos/parking1.mp4'
UPLOAD_FOLDER = '../ProjetoIntegradorV/static/videos'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
CLASSES_PATH = '../ProjetoIntegradorV/templates/YOLOV8/classes.txt'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template("frontend/tela.html")

@app.route('/dados_yolo')
def dados_yolo():
    with open(DADOS_YOLO_PATH) as f:
        yolo_data = json.load(f)
    return jsonify(yolo_data)

@app.route('/process_video', methods=['POST'])
def process_video():
    with open(CLASSES_PATH, "r") as classes_file:
        class_list_str = classes_file.read().split("\n")

    while True:
        video = cv2.VideoCapture(VIDEO_PATH)
        ret = True

        while ret:
            ret, frame = video.read()
            if not ret:
                break

            # processed_frame = basic.process_frame(frame, class_list_str)
            processed_frame = testcount.process_frame(frame, class_list_str)
            # basic.draw_area(processed_frame)
            # testcount.draw_area(processed_frame)
            
            _, jpeg = cv2.imencode('.jpg', processed_frame)
            frame_bytes = jpeg.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        video.release()

@app.route('/video_feed')
def video_feed():
    return Response(process_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            global VIDEO_PATH
            VIDEO_PATH = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            return redirect(url_for('index'))
    return render_template('frontend/upload.html')

if __name__ == '__main__':
    app.run(debug=True)
