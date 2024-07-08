# PYTHONIPC

This project is solely used because I hate using js for IPC controls

Essentially this is a python port of electron IPC module

Instead of the renderer interacting with the main process, a socketio client is used to communicate with a python3 socketio server

A package for javascript client is available under the following git:

[JsIPC](https://github.com/its-mr-monday/jsipc)

## Installation

Simply install using pip or your favourite package manager

```console
    pip install pythonipc
```

# PYTHONIPC ocumentation

## Import

```python
from pythonipc import PyIPC
```

## Class: PyIPC

### Constructor

```python
PyIPC(port: int = 5000, logger = False)
```

Creates a new PyIPC instance.

- `port`: The port number to run the server on (default is 5000)

### Methods

#### start()

Starts the PyIPC server in a separate thread.

```python
ipc = PyIPC()
ipc.start()
```

#### on(event: str)

Decorator to register a handler for a specific event.

```python
@ipc.on('greet')
def greet_handler(data):
    return f"Hello, {data['name']}!"
```

#### off(event: str)

Removes a handler for a specific event.

```python
ipc.off('greet')
```

#### invoke(event: str, data: Any, timeout: float = 5.0) -> Any

Invokes a remote procedure and waits for its response.

```python
result = await ipc.invoke('greet', {'name': 'Alice'})
print(result)  # Outputs: Hello, Alice!
```

#### kill()

Stops the PyIPC server and cleans up resources.

```python
ipc.kill()
```

## Full Example

```python
from pythonipc import PyIPC

ipc = PyIPC(port=5000)

@ipc.on('greet')
def greet_handler(data):
    return f"Hello, {data['name']}!"

def main():
    ipc.start()
    
    try:
        result = ipc.invoke('greet', {'name': 'Alice'})
        print(result)  # Outputs: Hello, Alice!
    finally:
        ipc.kill()

main()
```

This example sets up a PyIPC server, registers a 'greet' handler, invokes it, and then shuts down the server.