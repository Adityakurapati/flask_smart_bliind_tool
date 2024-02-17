from flask import Flask, render_template, Response
import cv2
import numpy as np
import urllib.request
import time
import easyocr

app = Flask(__name__)

# Load text recognition model.
reader = easyocr.Reader(['en'], gpu=False)

# Object Detection Using MobileNEt
config_file = 'content/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
frozen_model = 'content/frozen_inference_graph.pb'
url_object_detection = 'http://192.168.57.15/1600x1200.jpg'
file_name = 'content/labels.txt'

model = cv2.dnn_DetectionModel(frozen_model, config_file)
model.setInputSize(320, 320)
model.setInputScale(1.0 / 127.5)
model.setInputMean((127.5, 127.5, 127.5))
model.setInputSwapRB(True)

classLabels = []
with open(file_name, 'rt') as fpt:
    classLabels = fpt.read().rstrip('\n').split('\n')

def object_detection():
    while True:
        img_response = urllib.request.urlopen(url_object_detection)
        img_array = np.array(bytearray(img_response.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)

        ClassIndex, confidence, bbox = model.detect(img, confThreshold=0.5)

        font_scale = 3
        font = cv2.FONT_HERSHEY_PLAIN

        for i in range(len(ClassIndex)):
            classInd = int(ClassIndex[i])
            conf = confidence[i]
            box = bbox[i]

            cv2.rectangle(img, box, (255, 0, 0), 2)
            cv2.putText(img, classLabels[classInd - 1], (box[0] + 10, box[1] + 40),
                        font, fontScale=font_scale, color=(0, 255, 0), thickness=3)

        _, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        time.sleep(1)

# Text Recognition Using OCR
url_text_recognition = 'http://192.168.57.15/1600x1200.jpg'

def text_recognition():
    while True:
        img_response = urllib.request.urlopen(url_text_recognition)
        img_array = np.array(bytearray(img_response.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)

        text_data = reader.readtext(img)

        for t in text_data:
            bbox, text, score = t
            pt1 = (int(bbox[0][0]), int(bbox[0][1]))
            pt2 = (int(bbox[2][0]), int(bbox[2][1]))

            cv2.rectangle(img, pt1, pt2, (255, 255, 0), 5)
            cv2.putText(img, text, pt1, cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 0, 0), 1)

        _, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        time.sleep(1)

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/object_detection')
def object_detection_route():
    return Response(object_detection(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/text_recognition')
def text_recognition_route():
    return Response(text_recognition(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)


# if __name__ "__main__":
#         aapp.run(debug=False,host='0.0.0.0')