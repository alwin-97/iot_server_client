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

NodeMCU is used in this experiment to connect with Network and send the data from the sensor to the Server.

Configurations Needed in the code:

    - Wifi Name SSID / Name
    - Wifi Passoword

    - Server IP

Note: The Server and the IoT Device (NodeMCU) have to be on the same network to send the data to the server since the server is deployed on a local network.

## Things to Keep in Mind

Requirements:
1. Python
2. IOT Components: NodeMCU, DHT11, LED, Female to Female pin 5 Nos
3. Arduino IDE
4. Type B USB Cable

Python and the server_app.py code will setup the Flask Server in your laptop/desktop.
The code of aurdino needs to be updated on the NodeMCU.

---

The connection is as follows:  NodeMCU ESP8266 with DHT11 Sensor and LED – Connection Diagram

---

### 🔌 DHT11 Sensor Connections

| **DHT11 Pin** | **Connect to NodeMCU** | **Description**              |
|---------------|------------------------|------------------------------|
| VCC           | 3V3                    | Power supply (3.3V)          |
| DATA          | D2 (GPIO4)             | Data signal line             |
| GND           | GND                    | Ground                       |


---

### 💡 LED Connections

| **LED Pin**   | **Connect to NodeMCU**       | **Description**                        |
|---------------|------------------------------|----------------------------------------|
| Anode (+)     | D1 (GPIO5) via 220Ω Resistor | LED control pin (through resistor)     |
| Cathode (-)   | GND                          | Ground                                 |

---




## Application Side

The application have two routes associated. One for capturng the image of the user from an HTML page and the other one is to upload the data to the media folder. The program can be extended to send the image capture url to the user as a msg and the application can analyse the emotion from the uploaded image and take actions.

    127.0.0.1:8000/capture/

URL can be used to capture image and send it to the server now.

## Face Registration & Login
Register and Checkout!