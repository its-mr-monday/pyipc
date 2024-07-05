from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, emit
import random, threading
from functools import wraps

class PyIPC:
    """
    PyIPC class for inter-process communication using Socket.IO
    """

    def __init__(self, port=5000):
        """
        Initialize a new PyIPC instance
        
        :param port: The port number to run the server on (default is 5000)
        :type port: int
        """
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(32))
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.port = port
        self.handlers = {}
        self.room_handlers = {}
        self._thread = None
        self._running = False

        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')

        @self.socketio.on('join')
        def on_join(data):
            room = data['room']
            join_room(room)
            print(f'Client {request.sid} joined room: {room}')

        @self.socketio.on('leave')
        def on_leave(data):
            room = data['room']
            leave_room(room)
            print(f'Client {request.sid} left room: {room}')

        @self.socketio.on('message')
        def handle_message(data):
            channel = data.get('channel')
            payload = data.get('payload')
            room = data.get('room')
            
            if room and room in self.room_handlers and channel in self.room_handlers[room]:
                self.room_handlers[room][channel](payload)
            elif channel in self.handlers:
                self.handlers[channel](payload)

        @self.socketio.on_any
        def catch_all(event, *args, **kwargs):
            if event in self.handlers:
                self.handlers[event](*args)

    def start(self):
        """
        Start the PyIPC server in a separate thread
        """
        if self._running:
            print(f"PyIPC already running!")
            return
        self._thread = threading.Thread(target=self.run_server, daemon=True)
        self._thread.start()
        self._running = True

    def run_server(self):
        """
        Run the Socket.IO server (internal method)
        """
        try:
            self.socketio.run(self.app, port=self.port)
        except Exception as e:
            print(f"Exception occurred in PyIPC server thread: {e}")
        return

    def on(self, channel):
        """
        Decorator to register a handler for a specific channel
        
        :param channel: The channel to listen on
        :type channel: str
        """
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                return f(*args, **kwargs)
            self.handlers[channel] = wrapped
            return wrapped
        return decorator

    def on_room(self, room, channel):
        """
        Decorator to register a handler for a specific room and channel
        
        :param room: The room to join
        :type room: str
        :param channel: The channel to listen on within the room
        :type channel: str
        """
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                return f(*args, **kwargs)
            if room not in self.room_handlers:
                self.room_handlers[room] = {}
            self.room_handlers[room][channel] = wrapped
            return wrapped
        return decorator
        
    def off(self, channel):
        """
        Remove a handler for a specific channel
        
        :param channel: The channel to stop listening on
        :type channel: str
        """
        if channel in self.handlers:
            del self.handlers[channel]

    def off_room(self, room, channel):
        """
        Remove a handler for a specific room and channel
        
        :param room: The room to leave
        :type room: str
        :param channel: The channel to stop listening on within the room
        :type channel: str
        """
        if room in self.room_handlers and channel in self.room_handlers[room]:
            del self.room_handlers[room][channel]

    def emit(self, channel, data, room=None):
        """
        Emit a message on a specific channel, optionally to a specific room
        
        :param channel: The channel to emit on
        :type channel: str
        :param data: The data to emit
        :type data: Any
        :param room: The room to emit to (if any), defaults to None
        :type room: str, optional
        """
        if room:
            self.socketio.emit('message', {'channel': channel, 'payload': data, 'room': room}, room=room)
        else:
            self.socketio.emit(channel, data)
        
    def kill(self):
        """
        Stop the PyIPC server and clean up resources
        """
        self.socketio.stop()
        if (self._thread):
            self._thread.join()
            self._thread = None