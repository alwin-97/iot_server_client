from flask import Flask, request, jsonify
from utlities import database
from datetime import datetime
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

database.init_db()


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
            - userid
            - sensorid
            - value
          properties:
            timestamp:
              type: string
              description: ISO timestamp (optional)
            userid:
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
        timestamp = data.get('timestamp', datetime.now().isoformat())
        userid = data['userid']
        sensorid = data['sensorid']
        value = float(data['value'])

        database.store_data(timestamp, userid, sensorid, value)

        return jsonify({"status": "success", "data": data}), 200
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/data/<userid>', methods=['GET'])
def get_user_readings(userid):
    """
    Get all sensor readings for a specific user
    ---
    parameters:
      - name: userid
        in: path
        type: string
        required: true
        description: User ID to filter data
    responses:
      200:
        description: A list of readings for the user
        schema:
          type: object
          properties:
            status:
              type: string
            user:
              type: string
            readings:
              type: array
              items:
                type: object
                properties:
                  timestamp:
                    type: string
                  userid:
                    type: string
                  sensorid:
                    type: string
                  value:
                    type: number
    """
    try:
        rows = database.get_user_readings(userid)
        if not rows:
            return jsonify({"status": "error", "message": "No readings found for this user"}), 404
        
        data = [
            {"timestamp": row[0], "userid": row[1], "sensorid": row[2], "value": row[3]}
            for row in rows
        ]

        return jsonify({"status": "success", "user": userid, "readings": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)