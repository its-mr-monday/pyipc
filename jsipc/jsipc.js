import io from 'socket.io-client';

class JsIPC {
    constructor(url = 'http://localhost:5000') {
        this.socket = io(url);
        this.handlers = {};

        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });

        this.socket.on('message', (data) => {
            const { channel, payload } = data;
            if (this.handlers[channel]) {
                this.handlers[channel](payload);
            }
        });
    }

    on(channel, handler) {
        this.handlers[channel] = handler;
        this.socket.on(channel, handler);
    }

    emit(channel, data) {
        this.socket.emit('message', { channel, payload: data });
    }
}

// Usage example
const ipc = new JsIPC();

ipc.on('response-channel', (data) => {
    console.log('Received on response-channel:', data);
});

ipc.emit('test-channel', 'Hello from JS!');

export default JsIPC;