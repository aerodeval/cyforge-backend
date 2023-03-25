
import base64
import re
import cv2
import json
from flask import Flask, request,jsonify
import numpy as np
import csv
import numpy as np
import speech_recognition as sr
import random
app = Flask(__name__)

@app.route('/process-image', methods=['POST'])
def process_image():
    image_data = request.get_json()['image']
    image = cv2.imdecode(np.frombuffer(base64.b64decode(image_data), np.uint8), cv2.IMREAD_UNCHANGED)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    cv2.imshow("hsv",hsv)
    # define range of blue color in HSV
    lower_white = np.array([0, 0, 231])
    upper_white = np.array([180, 8, 255])
    lower_green = np.array([36, 0, 200])
    upper_green = np.array([89, 155, 255
    ])
    # Create a mask. Threshold the HSV image to get only yellow colors
    mask1 = cv2.inRange(hsv, lower_white, upper_white)
    mask2 = cv2.inRange(hsv, lower_green, upper_green)
    # Bitwise-AND mask and original image
    result_sender = cv2.bitwise_and(image,image, mask= mask1)
    result_receiver = cv2.bitwise_and(image,image, mask= mask2)
    image=result_sender
    image_recv=result_receiver
    # Encode the processed image back to base64
    _, img_encodedrecv = cv2.imencode('.jpg', image_recv)
    _, img_encoded = cv2.imencode('.jpg', image)
    processed_image_data = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
    processed_image_data_recv = base64.b64encode(img_encodedrecv.tobytes()).decode('utf-8')

    return json.dumps({ 'image': processed_image_data,'image_recv':processed_image_data_recv })

@app.route('/convert',methods=['POST'])
def convert():
    file = request.files['file']
    suffix = random.randint(100000,999999)
    suffix = str(suffix)
    filename = f'audio_{suffix}.wav'
    file.save(filename)

    try:
        r = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            data = r.record(source)
            text = r.recognize_google(data)

    except:
        return  f"Some error occured"

    res = jsonify(text=text)
    return res
@app.route('/text',methods=['POST'])
def process_txt_file():
    # Get the uploaded file from the request
    file = request.files['file']
    
    # Read the contents of the file
    contents = file.read().decode('utf-8')
    
    # Split the contents into individual lines
    lines = contents.split('\n')
    
    # Initialize a dictionary to store the data for each sender
    senders = {}
    
    # Loop through each line and split it into the timestamp, sender name, and message text
    for line in lines:
        # Use a regular expression to match the timestamp and sender name
        match = re.match(r'(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}\s*[ap]m) - (.+?): (.+)', line)
        if match:
            timestamp = match.group(1)
            sender_name = match.group(2)
            message_text = match.group(3)
            
            # Check if the sender name already exists in the dictionary
            if sender_name in senders:
                # If it does, add the message to the sender's list of messages
                senders[sender_name].append({'timestamp': timestamp, 'message_text': message_text})
            else:
                # If it doesn't, create a new list for the sender and add the message to it
                senders[sender_name] = [{'timestamp': timestamp, 'message_text': message_text}]
    
    # Return the data for each sender as a JSON response
    return jsonify(senders)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

