'''
    Copyright 2024 by its-mr-monday
    All rights reserved
    This file is part of the pythonipc library, and is released 
    under the "MIT License Agreement". Please see the LICENSE file that 
    should have been included as part of this package
'''

import asyncio
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import random
import string
from typing import Any, Callable

class PyIPC:
    """
    PyIPC class for inter-process communication using Socket.IO
    """

    def __init__(self, port: int = 5000):
        """
        Initialize a new PyIPC instance

        :param port: The port number to run the server on (default is 5000)
        :type port: int
        """
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        self.port = port
        self.handlers: dict[str, Callable] = {}
        self._thread = None
        self._running = False
        self.response_futures: dict[str, asyncio.Future] = {}

    def start(self) -> None:
        """
        Start the PyIPC server in a separate thread
        """
        if self._running:
            print("PyIPC already running!")
            return
        self._thread = asyncio.get_event_loop().run_in_executor(None, self.run_server)
        self._running = True

    def run_server(self) -> None:
        """
        Run the Socket.IO server (internal method)
        """
        self.socketio.run(self.app, port=self.port)

    def on(self, event: str) -> Callable:
        """
        Decorator to register a handler for a specific event

        :param event: The event to listen on
        :type event: str
        :return: Decorator function
        :rtype: Callable
        """
        def decorator(f: Callable) -> Callable:
            self.handlers[event] = f
            return f
        return decorator

    async def invoke(self, event: str, data: Any) -> Any:
        """
        Invoke a remote procedure and wait for its response

        :param event: The event name of the remote procedure
        :type event: str
        :param data: The data to send with the invocation
        :type data: Any
        :return: The response from the remote procedure
        :rtype: Any
        """
        response_id = self.generateUUID()
        future = asyncio.Future()
        self.response_futures[response_id] = future

        self.socketio.emit('message', {'event': event, 'data': data, 'response_id': response_id})
        return await future

    def generateUUID(self) -> str:
        """
        Generate a random 32-character string of alphabetic characters

        :return: A unique identifier string
        :rtype: str
        """
        return ''.join(random.choices(string.ascii_letters, k=32))

    def kill(self) -> None:
        """
        Stop the PyIPC server and clean up resources
        """
        if self._running:
            self.socketio.stop()
            self._thread.cancel()
            self._running = False