from flask import Flask, request, jsonify

app_flask = Flask(__name__)

# Initialize sensor data
sensor_data = {'temperature': 0, 'humidity': 0}

@app_flask.route('/receive_data', methods=['POST', 'GET'])
def receive_data():
    global sensor_data

    if request.method == 'POST':
        received_data = request.get_json()
        print(f"Received data from other server: {received_data}")

        # Update sensor data
        sensor_data = received_data

        return "Data received successfully", 200
    elif request.method == 'GET':
        return jsonify(sensor_data)

if __name__ == '__main__':
    app_flask.run('0.0.0.0', port=5000)