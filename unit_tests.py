import base64
import json
import requests
from unittest import mock

from app import app, MessageType, extract_text_from_image, solve_question

# Define some test data
IMAGE_DATA = base64.b64encode(b"test-image-data").decode("utf-8")
IMAGE_URL = ""
EXTRACTED_TEXT = ""
OPENAI_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": "",
                "id": "",
                "to": "",
            },
            "index": "",
            "logprobs": None,
            "text": "",
        }
    ],
    "created": "",
    "id": "",
    "model": "",
}

def test_upload_image():
    # Mock the S3 client
    with mock.patch("app.s3.put_object") as mock_s3_put_object:
        # Make a request to the endpoint
        response = app.test_client().post(
            "",
            data={
                "imageData": f"data:image/jpeg;base64,{IMAGE_DATA}",
            },
        )
        # Assert that the S3 client was called with the correct parameters
        mock_s3_put_object.assert_called_with(
            Bucket="gpt-trial",
            Key=mock.ANY,  # The key is generated dynamically, so we just check its type
            ContentType="image/jpeg",
            ContentEncoding="base64",
            Body=b"test-image-data",
        )
        # Assert that the response contains the expected image URL
        response_data = json.loads(response.data)
        assert response_data["imageUrl"].startswith("https://gpt-trial.s3.me-south-1.amazonaws.com/chat-images/")

def test_message_type():
    # Create a MessageType object and assert that its properties are set correctly
    message = MessageType(
        id="test-id",
        type="test-type",
        content="test-content",
        timestamp=1234567890,
        sender="test-sender",
    )
    assert message.id == " "
    assert message.type == " "
    assert message.content == " "
    assert message.timestamp == ""
    assert message.sender == ""
    # Test the to_dict() method
    assert message.to_dict() == {
        "id": "",
        "type": "",
        "content": "",
        "timestamp": "",
        "sender": "",
    }

@mock.patch("app.emit")
@mock.patch("app.openai.ChatCompletion.create")
def test_solve_question(mock_openai_chat_completion_create, mock_emit):
    # Mock the OpenAI API and emit() function
    mock_openai_chat_completion_create.return_value = OPENAI_RESPONSE
    # Call the solve_question() function with a MessageType object
    message_obj = MessageType(
        id="",
        type="",
        content="",
        timestamp="",
        sender="",
    )
    solve_question(message_obj)
    # Assert that the OpenAI API was called with the correct parameters
    mock_openai_chat_completion_create.assert_called_with(
        model="gpt-3.5-turbo",
        messages={
        "role": " ",
        "content": " ",
        })
