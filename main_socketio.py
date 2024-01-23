import asyncio
import random
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
import socketio

app = FastAPI()

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
            var socket = io.connect("http://localhost:8000");

            function sendHeartbeat() {
                var heartbeatData = Math.floor(Math.random() * (90 - 60 + 1) + 60);
                socket.emit('heartbeat', { value: heartbeatData });
            }
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
            var socket = io.connect("http://localhost:8000");

            socket.on('report_dashboard', function(data) {
            console.log(data);
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode("Received Heartbeat: " + data.value);
                message.appendChild(content);
                messages.appendChild(message);
            });
        </script>
    </body>
</html>
"""

clients = {"sender": set(), "receiver": set()}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(token: str = Depends(oauth2_scheme)):
    # Perform authentication logic here, e.g., validate token
    # For simplicity, we'll use a dummy validation for illustration purposes
    if token != "dummy_token":
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def send_heartbeat(room: str, sio):
    while True:
        await asyncio.sleep(1)
        heartbeat_data = {"value": random.randint(60, 90)}
        sio.emit('heartbeat', heartbeat_data, room=room)


sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app.mount('/socket.io', socketio.ASGIApp(sio))

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_heartbeat("sender", sio))
    asyncio.create_task(send_heartbeat("receiver", sio))


@app.get("/sender")
async def sender():
    return HTMLResponse(html_sender)


@app.get("/receiver")
async def receiver():
    return HTMLResponse(html_receiver)


@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.event
async def heartbeat(sid, data):
    print(f"Heartbeat from {sid}: {data}")
    await sio.emit('report_dashboard', data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
