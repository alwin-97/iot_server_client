# IOT Server Client

## Server Configuration

Create virtual environment

    python -m venv venv

Install the system dependencies

    pip install -r requirements.txt

run the server app

    python server_app.py

Note: Server will run using the System IP.

API Docuemtation can be found at:

    http://localhost:5000/apidocs/

There are two main apis

    1. http://127.0.0.1:5000/api/data

    This API is used for sending data to the server. It is a post request with data in JSON format. Sample data goes as:
    {
        "timestamp": "2025-04-08T15:45:00",
        "userid": "user_01",
        "sensorid": "sensor_12",
        "value": 22.7
    }

    Response:
    {
        "data": {
            "sensorid": "sensor_12",
            "timestamp": "2025-04-08T15:45:00",
            "userid": "user_01",
            "value": 22.7
        },
        "status": "success"
    }

    
    2. http://127.0.0.1:5000/api/data/<user_id>

    This api is used go get the data entered by the user in the application. This is a get request with the response as:
    {
        "readings": [
            {
                "sensorid": "sensor_12",
                "timestamp": "2025-04-08T15:45:00",
                "userid": "user_01",
                "value": 22.7
            },
            {
                "sensorid": "sensor_12",
                "timestamp": "2025-04-08T15:45:00",
                "userid": "user_01",
                "value": 22.7
            },
            {
                "sensorid": "sensor_12",
                "timestamp": "2025-04-08T15:45:00",
                "userid": "user_01",
                "value": 22.7
            }
        ],
        "status": "success",
        "user": "user_01"
    }


## Client Configuration
