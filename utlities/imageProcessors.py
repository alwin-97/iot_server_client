import os
import cv2
import base64
import numpy as np

CASCADE_XML = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(CASCADE_XML)
if face_cascade.empty():
    raise RuntimeError(f"Failed to load CascadeClassifier from {CASCADE_XML}")


def decode_image(data_url):
    if not data_url or "," not in data_url:
        print("decode_image: empty or malformed data_url")
        return None

    header, encoded = data_url.split(",", 1)
    try:
        data = base64.b64decode(encoded)
        arr  = np.frombuffer(data, np.uint8)
        img  = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print("decode_image error:", e)
        return None


def detect_face(img):
    if img is None:
        print("detect_face: received None")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # you can play with scaleFactor and minNeighbors
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,      # smaller → slower but more sensitive
        minNeighbors=4,       # smaller → more detections (including false positives)
        minSize=(40, 40),     # ignore tiny patches
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    if len(faces) == 0:
        print("detect_face: no faces found")
        return None
    if len(faces) > 1:
        print("detect_face: multiple faces found:", faces)
        return None

    x, y, w, h = faces[0]
    face_img = gray[y:y+h, x:x+w]

    # Optional: resize to a fixed size to improve recognizer stability
    face_img = cv2.resize(face_img, (200, 200))
    return face_img


def train_recognizer(MODEL_PATH, DATA_DIR):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, labels = [], []
    for uid in os.listdir(DATA_DIR):
        user_folder = os.path.join(DATA_DIR, uid)
        if not os.path.isdir(user_folder): continue
        for img_name in os.listdir(user_folder):
            path = os.path.join(user_folder, img_name)
            img  = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            faces.append(img)
            labels.append(int(uid))
    if faces:
        recognizer.train(faces, np.array(labels))
        recognizer.write(MODEL_PATH)