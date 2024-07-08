'''
    Copyright 2024 by its-mr-monday
    All rights reserved
    This file is part of the pythonipc library, and is released 
    under the "MIT License Agreement". Please see the LICENSE file that 
    should have been included as part of this package
'''

import threading
import time
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
import random
import string
from typing import Any

class ThreadCancellationToken:
    """A simple token to allow for cancellation of a thread."""
    def __init__(self):
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

class PyIPC:
    """
    PyIPC class for inter-process communication using Flask-SocketIO.
    
    Attributes:
        port (int): The port on which the server will run.
        logger (bool): Flag to enable or disable logging.
    """
    def __init__(self, port: int = 5000, logger: bool = False):
        """
        Initialize the PyIPC server.
        
        Args:
            port (int): The port on which the server will run.
            logger (bool): Flag to enable or disable logging.
        """
        self.app = Flask(__name__)
        self.app.logger.setLevel(logging.ERROR)  # Suppress Flask logs
        CORS(self.app)  # Enable CORS for all routes

        # Initialize SocketIO with threading mode
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)
        
        self.port = port
        self.handlers = {}  # Store event handlers
        self._thread = None  # Thread for running the server
        self._running = False  # Flag to indicate if server is running
        self.responses = {}  # Store responses keyed by response_id
        self.response_locks = {}  # Locks for thread-safe access to responses
        self.logger = logger  # Enable or disable logging

        if self.logger:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            self.log = logging.getLogger(__name__)
        else:
            self.log = logging.getLogger(__name__)
            self.log.setLevel(logging.ERROR)

        @self.socketio.on('message')
        def handle_message(payload):
            """Handle incoming SocketIO messages."""
            if self.logger:
                self.log.info(f"Received message: {payload}")
            event = payload.get('event')
            data = payload.get('data')
            response_id = payload.get('response_id')
            
            if response_id and response_id in self.response_locks:
                # This is a response to a previous request
                if self.logger:
                    self.log.info(f"Resolving response for response_id: {response_id}")
                with self.response_locks[response_id]:
                    self.responses[response_id] = data
            elif event in self.handlers:
                # This is a new event to handle
                if self.logger:
                    self.log.info(f"Handling event: {event}")
                result = self.handlers[event](data)
                if response_id:
                    if self.logger:
                        self.log.info(f"Sending response for event: {event}")
                    self.socketio.emit('message', {'event': event, 'data': result, 'response_id': response_id})
            else:
                if self.logger:
                    self.log.warning(f"No handler found for event: {event}")

    def start(self):
        """Start the SocketIO server in a separate thread."""
        if self._running:
            if self.logger:
                self.log.warning("PyIPC already running!")
            return
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        self._running = True
        if self.logger:
            self.log.info(f"PyIPC Server started on port {self.port}")

    def _run_server(self):
        """Run the SocketIO server."""
        self.socketio.run(self.app, port=self.port, debug=False, log_output=False)

    def on(self, event):
        """
        Decorator to register event handlers.
        
        Args:
            event (str): The name of the event to handle.
        
        Returns:
            function: The decorator function.
        """
        def decorator(f):
            self.handlers[event] = f
            return f
        return decorator

    def invoke(self, event: str, data: Any, timeout: float = 15.0) -> Any:
        """
        Invoke a remote procedure and wait for its response.
        
        Args:
            event (str): The name of the event to invoke.
            data (Any): The data to send with the event.
            timeout (float): Maximum time to wait for a response, in seconds.
        
        Returns:
            Any: The response data from the remote procedure.
        
        Raises:
            TimeoutError: If no response is received within the timeout period.
        """
        if self.logger:
            self.log.info(f"Invoking event: {event} with data: {data}")
        response_id = self._generate_uuid()
        self.responses[response_id] = None
        self.response_locks[response_id] = threading.Lock()

        cancellation_token = ThreadCancellationToken()

        # Emit the event via SocketIO
        self.socketio.emit('message', {'event': event, 'data': data, 'response_id': response_id})

        start_time = time.time()
        while time.time() - start_time < timeout and not cancellation_token.is_cancelled:
            with self.response_locks[response_id]:
                if self.responses[response_id] is not None:
                    # Response received
                    result = self.responses[response_id]
                    del self.responses[response_id]
                    del self.response_locks[response_id]
                    if self.logger:
                        self.log.info(f"Received result for event {event}: {result}")
                    return result
            time.sleep(0.01)  # Short sleep to prevent busy-waiting

        # Timeout occurred
        del self.responses[response_id]
        del self.response_locks[response_id]
        if self.logger:
            self.log.error(f"Timeout waiting for response to event: {event}")
        raise TimeoutError(f"Timeout waiting for response to event: {event}")

    def kill(self):
        """Stop the SocketIO server and clean up."""
        if self._running:
            self.socketio.stop()
            self._thread.join()
            self._running = False
            if self.logger:
                self.log.info("PyIPC Server shut down")

    def _generate_uuid(self):
        """Generate a unique identifier for response tracking."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))