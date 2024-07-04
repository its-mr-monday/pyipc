from flask import Flask
from flask_socketio import SocketIO
import random, threading

class PyIPC:
    def __init__(self, port=5000):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(32))
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.port = port
        self.handlers = {}

        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')

        @self.socketio.on('message')
        def handle_message(data):
            channel = data.get('channel')
            payload = data.get('payload')
            if channel in self.handlers:
                self.handlers[channel](payload)

    def start(self):
        threading.Thread(target=self.run_server, daemon=True).start()

    def run_server(self):
        self.socketio.run(self.app, port=self.port)

    def on(self, channel, handler):
        self.handlers[channel] = handler

    def emit(self, channel, data):
        self.socketio.emit(channel, data)