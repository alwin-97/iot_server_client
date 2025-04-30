import os
import cv2
import base64
import pickle

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, session, jsonify
)
from utlities import database
from datetime import datetime
from flasgger import Swagger
from datetime import datetime
from utlities.imageProcessors import decode_image, detect_face, train_recognizer

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret"
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
swagger = Swagger(app)

database.init_db()

MODEL_PATH  = os.path.join(app.root_path, "trainer.yml")
DATA_DIR    = os.path.join(app.root_path, "face_data")

@app.route('/api/data', methods=['POST'])
def receive_data():
    """
    Receive sensor data and store it in the database
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: SensorData
          required:
            - device_id
            - sensorid
            - value
          properties:
            timestamp:
              type: string
              description: ISO timestamp (optional)
            device_id:
              type: string
            sensorid:
              type: string
            value:
              type: number
    responses:
      200:
        description: Data received and stored successfully
    """
    data = request.get_json()

    try:
        # Extract the required fields
        timestamp = datetime.now().isoformat()
        data['timestamp'] = timestamp  # Add the current timestamp if not provided
        device_id = data['device_id']
        sensorid = data['sensorid']
        value = float(data['value'])

        database.store_data(timestamp, device_id, sensorid, value)

        return jsonify({"status": "success", "data": data}), 200
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/data/<device_id>', methods=['GET'])
def get_user_readings(device_id):
    """
    Get all sensor readings for a specific device_id
    ---
    parameters:
      - name: device_id
        in: path
        type: string
        required: true
        description: device_id ID to filter data
    responses:
      200:
        description: A list of readings for the device_id
        schema:
          type: object
          properties:
            status:
              type: string
            device_id:
              type: string
            readings:
              type: array
              items:
                type: object
                properties:
                  timestamp:
                    type: string
                  device_id:
                    type: string
                  sensorid:
                    type: string
                  value:
                    type: number
    """
    try:
        rows = database.get_user_readings(device_id)
        if not rows:
            return jsonify({"status": "error", "message": "No readings found for this user"}), 404
        
        data = [
            {"timestamp": row[0], "device_id": row[1], "sensorid": row[2], "value": row[3]}
            for row in rows
        ]

        return jsonify({"status": "success", "device_id": device_id, "readings": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/capture/')
def capture_page():
    return render_template('capture.html')

@app.route('/upload/', methods=['POST'])
def upload():
    data = request.json['image']
    header, encoded = data.split(",", 1)
    image_data = base64.b64decode(encoded)

    filepath = 'media/'+datetime.now().__str__().replace(':', '-').replace(' ', '_')+'.png'
    with open(filepath, 'wb') as f:
        f.write(image_data)

    return jsonify({"message": "Image received and saved!"})

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 1) grab the base64 string from form, not files
        data_url = request.form.get("image", "")
        img_bytes = decode_image(data_url)
        if img_bytes is None:
            flash("Could not read your photo. Please Snap again.", "error")
            return redirect(url_for("login"))

        # 2) detect & crop face
        face = detect_face(img_bytes)
        if face is None:
            flash("Show exactly one face.", "error")
            return redirect(url_for("login"))

        # 3) ensure model exists
        if not os.path.exists(MODEL_PATH):
            flash("No trained model—please register first.", "error")
            return redirect(url_for("login"))

        # 4) predict
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(MODEL_PATH)
        label, confidence = recognizer.predict(face)

        if confidence < 70:
            session["userid"] = label
            return redirect(url_for("dashboard"))
        else:
            flash("Face not recognized.", "error")
            return redirect(url_for("login"))

    return render_template("index.html")


@app.route('/register/', methods=['GET','POST'])
def register():
    if request.method == "POST":
        name     = request.form["name"]
        email    = request.form["email"]
        phone    = request.form["phone"]
        device_id = request.form["device_serial_number"]
        images = request.form.getlist("images")

        # decode & get embedding
        if len(images) < 10:
            flash("Please capture 10 face samples.")
            return redirect(url_for("register"))

        # save user
        userid = None
        try:
          userid = database.create_user(
                  name=name,
                  email=email,
                  phone=phone,
                  device_id=device_id,
              )
        except Exception:
            flash("That email is already registered.")
            return redirect(url_for("register"))
        
        user_dir = os.path.join(DATA_DIR, str(userid))
        os.makedirs(user_dir, exist_ok=True)

                # save each face crop
        for idx, data_url in enumerate(images):
            img = decode_image(data_url)
            face = detect_face(img)
            if face is None:
                flash("Ensure exactly one face per sample.")
                # cleanup partially saved folder
                for f in os.listdir(user_dir):
                    os.remove(os.path.join(user_dir,f))
                os.rmdir(user_dir)
                database.delete_user(userid)
                flash("Registration failed. Please try again.")
                return redirect(url_for("register"))

            cv2.imwrite(os.path.join(user_dir, f"{idx}.png"), face)

        # retrain on ALL data
        train_recognizer(MODEL_PATH, DATA_DIR)

        flash("Registered! Please log in via face.")
        return redirect(url_for("login"))
    return render_template('register.html')

@app.route('/dashboard/', methods=['GET'])
def dashboard():
    userid = session.get("userid")
    if not userid:
        flash("Please log in first.")
        return redirect(url_for("login"))
    
    print("userid:", userid)
    user = database.get_user(userid)
    print(user)

    if user is None:
        flash("User not found.")
        return redirect(url_for("login"))
    
    device_readings = database.get_user_readings(user["device_id"])

    return render_template('dashboard.html',user=user,device_readings=device_readings)

@app.route('/logout/')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)