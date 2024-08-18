import random
import time
import requests

def simulate_sensor_data():
    while True:
        data = {
            'source': 'Room 2',  # Unique ID for this script
            'temperature': random.uniform(20.0, 30.0),
            'pressure': random.uniform(950, 1050),
            'humidity': random.uniform(30, 70)
        }
        try:
            response = requests.post('http://127.0.0.1:5000/data', json=data)
            print(f'Sent data: {data} - Response: {response.status_code}')
        except requests.exceptions.RequestException as e:
            print(f'Error sending data: {e}')
        time.sleep(5)  # Send data every 5 seconds

simulate_sensor_data()
