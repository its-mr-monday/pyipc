# PYIPC

This project is solely used because I hate using js for IPC controls

Essentially this is a python port of electron IPC module

Instead of the renderer interacting with the main process, a socketio client is used to communicate with a python3 socketio server

## Usage

### Python Process

```py
from pyipc.pyipc import PyIPC

ipc = PyIPC()

@ipc.on('test')
def test(data):
    print(data)
    ipc.emit('test', 'Hello from python')

ipc.start()

```

### JS Process

```js
import JsIPC from 'jsipc';

const ipc = new JsIPC();

ipc.on('test', (data) => {
    console.log(data);
});

ipc.emit('test', 'Hello from js');
```

## Installation

The two projects require some dependencies

### Python
 1. flask
 2. flask\_socketio
 3. flask\_cors

### JS
 1. socket.io-client

Once you have these dependencies it should be as easy as the use case above!



