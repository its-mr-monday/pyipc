# PYIPC

This project is solely used because I hate using js for IPC controls

Essentially this is a python port of electron IPC module

Instead of the renderer interacting with the main process, a socketio client is used to communicate with a python3 socketio server

A package for javascript client is available under the following git:

[JsIPC](https://github.com/its-mr-monday/jsipc)

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
import JsIPC from '@its-mr-monday/jsipc';

const ipc = new JsIPC();

ipc.on('test', (data) => {
    console.log(data);
});

ipc.emit('test', 'Hello from js');
```

## Installation

Simply install using pip or your favourite package manager

```console
    pip install pyipc
```