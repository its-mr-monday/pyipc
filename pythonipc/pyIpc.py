from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import random, threading

class PyIPC:
    def __init__(self, port=5000):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(32))
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.port = port
        self.handlers = {}
        self._thread = None
        self._running = False

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
        if self._running:
            print(f"PyIPC already running!")
            return
        self._thread = threading.Thread(target=self.run_server, daemon=True)
        self._thread.start()
        self._running = True

    def run_server(self):
        try:
            self.socketio.run(self.app, port=self.port)
        except Exception as e:
            print(f"Exception occured in PyIPC server thread: {e}")
        return

    def on(self, channel, handler):
        self.handlers[channel] = handler
        
    def off(self, channel):
        if channel in self.handlers:
            del self.handlers[channel]

    def emit(self, channel, data):
        self.socketio.emit(channel, data)
        
    def kill(self):
        self.socketio.stop()
        if (self._thread):
            self._thread.join()
            self._thread = None
