import numpy as np
import cv2
import face_recognition
import urllib.request
import json
import pickle

# Define the functions
def get_enc(img): 
    face = face_recognition.face_locations(img, number_of_times_to_upsample=1)
    encode = face_recognition.face_encodings(img, known_face_locations=face, num_jitters=3, model="large")
    fc = face
    en = [f.tolist() for f in encode]
    return [en, fc]

def load_image_from_file(file_path):
    img = cv2.imread(file_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb

def load_image_from_url(url):
    resp = urllib.request.urlopen(url)
    img_array = np.asarray(bytearray(resp.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb

def load_image(media_path):
    if media_path.startswith('http://') or media_path.startswith('https://'):
        return load_image_from_url(media_path)
    else:
        return load_image_from_file(media_path)

# New function to create a database
def create_database(images_with_names):
    database = {}
    for name, image_path in images_with_names.items():
        img = load_image(image_path)
        encodings, _ = get_enc(img)
        if encodings:
            database[name] = encodings[0]
        else:
            print(f"No face detected in the image for {name}")
    return database

# Example usage of `create_database`
images_with_names = {
    'Person1': 'Ratan Tata.png',
    'Person2': 'Virat.jpg',
    'Person3': 'Rohit.png',
    'Person4': 'Rishav.png',
    'Person5': 'Kumar.png',
    # Add more persons and their images as needed
}
database = create_database(images_with_names)

# Save the database to a file
with open('face_database.pkl', 'wb') as f:
    pickle.dump(database, f)

print("Database saved successfully!")
