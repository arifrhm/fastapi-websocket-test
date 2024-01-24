# main.py

import asyncio
import random
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
import socketio
from fastapi.middleware.cors import CORSMiddleware

# import socketio_handlers

app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8778", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
        // Mock user credentials
        const username = 'atlet';
        const password = 'ArifRahman123';

        // Authenticate and obtain the token
        const loginFormData = new URLSearchParams({
            username: username,
            password: password,
        });

        fetch('http://localhost:8000/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: loginFormData,
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const userToken = data.access_token;
            console.log(userToken);

            var socket = io("http://localhost:8000/report", {
                auth: {
                    reconnectionDelayMax: 10000,
                    token: userToken,
                }
            });

            function sendHeartbeat() {
                var heartbeatData = Math.floor(Math.random() * (90 - 60 + 1) + 60);
                socket.emit('smartband_data', { heart_beat: heartbeatData, token: userToken });
            }

            setInterval(sendHeartbeat, 1000); // Send heartbeat every second
        });

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
           // Mock user credentials
const username = 'atlet';
const password = 'ArifRahman123';

// Authenticate and obtain the token
const loginFormData = new URLSearchParams({
    username: username,
    password: password,
});

fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: loginFormData,
})
    .then(response => response.json())
    .then(data => {
        const userToken = data.access_token;
        console.log(userToken);

        // Establish Socket.IO connection after successful login
        var socket = io("http://localhost:8000/report", {
            reconnectionDelayMax: 10000,
            auth: {
                token: userToken,
            },
        });

        socket.on('update_dashboard', function(data) {
            console.log(data);
            var messages = document.getElementById('messages');
            var message = document.createElement('li');
            var content = document.createTextNode("Received Heartbeat: " + data.heart_beat);
            message.appendChild(content);
            messages.appendChild(message);
        });

        // Continue with any additional Socket.IO event listeners or functionality
    })
    .catch(error => {
        console.error('Login failed:', error);
    });

        </script>
    </body>
</html>
"""

# @sio.event(namespace='/report')
# async def connect(sid, environ, data):
#     await socketio_handlers.connect(sid, environ, data)

# @sio.event(namespace='/report')
# async def disconnect(sid):
#     await socketio_handlers.disconnect(sid)

# @sio.event(namespace='/report')
# async def smartband_data(sid, data):
#     await socketio_handlers.smartband_data(sid, data)
@app.get('/sender')
async def sender():
    return HTMLResponse(html_sender)

@app.get('/receiver')
async def receiver():
    return HTMLResponse(html_receiver)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8778)
