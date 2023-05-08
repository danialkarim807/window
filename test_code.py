import pytest
from flask_socketio import SocketIOTestClient

from app import app, socketio, handle_send_message


@pytest.fixture(scope='module')
def test_client():
    test_client = app.test_client()
    socketio_test_client = socketio.test_client(app)
    yield socketio_test_client
    socketio_test_client.disconnect()


def test_handle_send_message_text(test_client):
    message = {

    }
    handle_send_message(message)
    received_message = test_client.get_received()[0]['args'][0]
    assert received_message['id'] == ''
    assert received_message['type'] == ''
    assert received_message['content'] == ''
    assert received_message['timestamp'] == pytest.approx()


def test_handle_send_message_image(test_client):
    message = {"id": "1", "type": "image", "content": "https://example.com/image.jpg", "timestamp": 12345}
    handle_send_message(message)
    received_message = test_client.get_received()[0]['args'][0]
    assert received_message['id'] == ''
    assert received_message['type'] == ''
    assert 'solve this math problem' in received_message['content']
    assert received_message['timestamp'] == pytest.approx()


