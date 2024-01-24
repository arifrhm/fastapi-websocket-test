# main.py

import asyncio
import random
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
import socketio
import socketio_handlers

app = FastAPI()

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app.mount('/socket.io', socketio.ASGIApp(sio))


html_sender = """
<!DOCTYPE html>
<html>
    <head>
        <title>Socket.IO Sender</title>
        <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
    </head>
    <body>
        <h1>Socket.IO Sender</h1>
        <button onclick="sendHeartbeat()">Send Heartbeat</button>
        <script>
            var socket = io("http://localhost:8000/report", {
                auth: {
                    reconnectionDelayMax: 10000,
                    token: "dummy_token"
                }
            });

            function sendHeartbeat() {
                var heartbeatData = Math.floor(Math.random() * (90 - 60 + 1) + 60);
                socket.emit('smartband_data', { heart_beat: heartbeatData, token : "dummy_token" });
            }

            setInterval(sendHeartbeat, 1000); // Send heartbeat every second
        </script>
    </body>
</html>
"""

html_receiver = """
<!DOCTYPE html>
<html>
    <head>
        <title>Socket.IO Receiver</title>
        <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
    </head>
    <body>
        <h1>Socket.IO Receiver</h1>
        <ul id='messages'></ul>
        <script>
            var socket = io("http://localhost:8000/report", {
            reconnectionDelayMax: 10000,
    auth: {
        token: "dummy_token"
    }
});

            socket.on('update_dashboard', function(data) {
            console.log(data);
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode("Received Heartbeat: " + data.heart_beat);
                message.appendChild(content);
                messages.appendChild(message);
            });
        </script>
    </body>
</html>
"""

@sio.event(namespace='/report')
async def connect(sid, environ, data):
    await socketio_handlers.connect(sid, environ, data)

@sio.event(namespace='/report')
async def disconnect(sid):
    await socketio_handlers.disconnect(sid)

@sio.event(namespace='/report')
async def smartband_data(sid, data):
    await socketio_handlers.smartband_data(sid, data)
@app.get('/sender')
async def sender():
    return HTMLResponse(html_sender)

@app.get('/receiver')
async def receiver():
    return HTMLResponse(html_receiver)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
