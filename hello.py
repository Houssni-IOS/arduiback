import asyncio
import websockets
import threading
import os
import serial
import requests  # Import the requests library for making HTTP requests

# Replace 'COMX' with the actual serial port of your Arduino
ser = serial.Serial('COM4', 115200)

data_from_arduino = ""
previous_data = ""

def read_serial_data():
    global data_from_arduino
    while True:
        data = ser.readline().decode('utf-8', errors='ignore').strip()
        data_from_arduino = data

# Start a separate thread to continuously read data from the Arduino
serial_thread = threading.Thread(target=read_serial_data)
serial_thread.daemon = True
serial_thread.start()

async def send_data(websocket, path):
    global data_from_arduino, previous_data
    while True:
        await asyncio.sleep(1)  # Adjust the interval (in seconds) as needed
        if data_from_arduino != previous_data:
            print("Received data:", data_from_arduino)
            # Save the data to the backend using an HTTP POST request
            save_data_to_backend(data_from_arduino)
            await websocket.send(data_from_arduino)
            previous_data = data_from_arduino

def save_data_to_backend(data):
    # Replace the URL with your actual backend API endpoint
    url = 'http://localhost:8080/api/spots/saveData'
    headers = {'Content-Type': 'application/json'}
    payload = {'data': data}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        print("Data saved to backend:", response_data)
    except requests.exceptions.RequestException as e:
        print("Error saving data to backend:", e)

start_server = websockets.serve(send_data, "localhost", 8087)

async def main():
    # Start the WebSocket server
    await start_server
    print("WebSocket server running on ws://localhost:8087")

try:
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    # Close the serial connection when the program is interrupted
    ser.close()
