from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import openai
import requests
import json
import boto3
import base64
import os
import time
import uuid


# Flask
app = Flask(__name__)

app.config["SECRET_KEY"] = "your_secret_key_here"
CORS(app)

# SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# OpenAI
openai.api_key = "..."

# AWS
AWS_ACCESS_KEY_ID = '...'
AWS_SECRET_ACCESS_KEY = '...'
AWS_REGION = 'me-south-1'

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


@app.route("/")
def index():
    return "Chat App Backend"
    

@app.route('/upload', methods=['POST'])
def upload_image():
    image_data = requests.form.get('imageData')
    buffer = base64.b64decode(image_data.split(',')[1])
    key = f'chat-images/{int(time.time())}.jpeg'
    bucket = 'gpt-trial'
    
    s3.put_object(
        Bucket=bucket,
        Key=key,
        ContentType='image/jpeg',
        ContentEncoding='base64',
        Body=buffer,
    )

    image_url = f'https://{bucket}.s3.me-south-1.amazonaws.com/{key}'
    return jsonify({'imageUrl': image_url})

class MessageType:
    def _init_(self, id, type, content, timestamp, sender):
        self.id = id
        self.type = type
        self.content = content
        self.timestamp = timestamp
        self.sender = sender

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "timestamp": self.timestamp,
            "sender": self.sender,
        }


@socketio.on("send_message")
def handle_send_message(message):
    message_obj = MessageType(
        id=message["id"],
        type=message["type"],
        content=message["content"],
        timestamp=message["timestamp"],
        sender="server",  # Set the sender property to 'server'
    )
    #emit("receive_message", message_obj.to_dict(), broadcast=True)
    solve_question(message_obj)
# [6:23 AM, 3/29/2023] Naila Cdlem: this is the second part as i couldn't fit all of it:

def solve_question(message_obj):
    content = message_obj.content

    # Check if the message type is an image
    if message_obj.type == 'image':
        image_url = content
        # Extract text from the image
        extracted_text = extract_text_from_image(image_url)
        content = f"solve this math problem (it's written in LATEX but please answer it in normal text): {extracted_text}"

    # Send the text message to the OpenAI API for a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI tutor who can solve any question in normal text."},
            {"role": "user", "content": content},
        ]
    )

    # Extract the generated text from the response
    ai_response = response.choices[0].message.content.strip()

    # Create a new message object for the AI response
    ai_message_obj = MessageType(
        id=str(uuid.uuid4()),
        type='text',
        content=ai_response,
        timestamp=int(time.time()),
        sender='server',
    )

    # Emit the AI response as a message_obj
    #print(f"{ai_message_obj.content}")
    emit("receive_message", ai_message_obj.to_dict(), broadcast=True)



# Extracting text from image using MathPix APIs [[[[TODO: not all images return with "latex_styles" so we need to edit that to use the normal text]]]]
def extract_text_from_image(image_url):
    r = requests.post("https://api.mathpix.com/v3/text",
        json={
            "src": image_url,
            "math_inline_delimiters": ["$", "$"],
            "formats": ["text", "data", "latex_styled"],
            "data_options": {
                "include_asciimath": True,
                "include_latex": True
            },
            "rm_spaces": True
        },
        headers={
            "app_id": "....",
            "app_key": "....",
            "Content-type": "application/json"
        }
    )

    #print(json.dumps(r.json(), indent=4, sort_keys=True))

    latex_styled = r.json().get("latex_styled")
    text = r.json().get("text")

    return latex_styled if latex_styled else text

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)