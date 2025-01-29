import numpy as np
import cv2
import face_recognition
import urllib.request
import json
import pickle

# Define constants
TOL = 0.37
NMS_THRESHOLD = 0.71
MIN_CONFIDENCE = 0.3

# YOLO configuration
labelsPath = 'yolo/coco.names'
LABELS = open(labelsPath).read().strip().split("\n")
weights_path = 'yolo/yolov4-tiny.weights'
config_path = 'yolo/yolov4-tiny.cfg'

model = cv2.dnn.readNetFromDarknet(config_path, weights_path)
layer_name = model.getLayerNames()
layer_name = [layer_name[i - 1] for i in model.getUnconnectedOutLayers()]

# Load Haar cascade classifier for face detection
cascPath = 'haarcascade_frontalface_default.xml'
haar_cascade_face = cv2.CascadeClassifier(cascPath)

# Define the functions
def get_enc(img):
    face = face_recognition.face_locations(img, number_of_times_to_upsample=2)  # Increased upsample factor
    print(f"Detected face locations: {face}")
    encode = face_recognition.face_encodings(img, known_face_locations=face, num_jitters=3, model="large")
    fc = face
    en = [f.tolist() for f in encode]
    return [en, fc]

def area_from_loc(loc):
    if len(loc):
        a = (loc[2] - loc[0]) * (loc[1] - loc[3])
        return a
    else:
        return 0

def load_image_from_file(file_path):
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Image not found or unable to load: {file_path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print(f"Loaded image shape: {img_rgb.shape}")
    return img_rgb

def load_image_from_url(url):
    resp = urllib.request.urlopen(url)
    img_array = np.asarray(bytearray(resp.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Image not found or unable to load from URL: {url}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print(f"Loaded image shape: {img_rgb.shape}")
    return img_rgb

def load_image(media_path):
    if media_path.startswith('http://') or media_path.startswith('https://'):
        return load_image_from_url(media_path)
    else:
        return load_image_from_file(media_path)

# Load the database from file
with open('face_database.pkl', 'rb') as f:
    database = pickle.load(f)

# New function `face_reg` which uses `get_enc`, `area_from_loc`, and YOLO object detection
def face_reg(media_path, database):
    img = load_image(media_path)
    d = get_enc(img)
    ma = 0
    dd = 0
    if len(d[0]) > 0:
        for x in range(0, len(d[0])):
            if area_from_loc(d[1][x]) > ma:
                ma = area_from_loc(d[1][x])
                dd = d

        face_enc = json.dumps(dd[0][0])
        face_loc = json.dumps(dd[1][0])
        print("Face Detected-ok")
        print(face_enc)
        print(face_loc)

        # YOLO object detection
        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        model.setInput(blob)
        layerOutputs = model.forward(layer_name)

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                if confidence > MIN_CONFIDENCE:
                    box = detection[0:4] * np.array([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])
                    (centerX, centerY, width, height) = box.astype("int")

                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    cv2.rectangle(img, (x, y), (x + int(width), y + int(height)), (0, 255, 0), 2)
                    text = "{}: {:.4f}".format(LABELS[classID], confidence)
                    cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("YOLO Object Detection", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Perform face matching
        test_face_encodings = d[0]  # Use the encodings obtained from the test image
        for name, database_face_encodings in database.items():
            for test_face_encoding in test_face_encodings:
                test_face_encoding_np = np.array(test_face_encoding)  # Convert list to numpy array
                database_face_encodings_np = np.array(database_face_encodings)  # Convert list to numpy array
                match = face_recognition.compare_faces([database_face_encodings_np], test_face_encoding_np, tolerance=TOL)
                if True in match:
                    print(f"Match found for {name}")
                    return
        print("No match found in the database")
    else:
        print("No face detected!")

# Example usage of `face_reg`
media_path = 'Ratan Tata.png'  # Can be a local file path or a URL
face_reg(media_path, database)
