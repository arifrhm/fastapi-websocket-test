import asyncio
import random
from fastapi import FastAPI, WebSocket, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

html_sender = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Sender</title>
    </head>
    <body>
        <h1>WebSocket Sender</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/sender");
            ws.onmessage = function(event) {
                // Handle received messages
                console.log(event.data);
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

html_receiver = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Receiver</title>
    </head>
    <body>
        <h1>WebSocket Receiver</h1>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/receiver");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def send_heartbeat(room: str):
    while True:
        heartbeat_data = random.randint(40, 90)
        for client in clients[room]:
            await client.send_text(f"Heartbeat: {heartbeat_data}")
        await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_heartbeat("sender"))
    asyncio.create_task(send_heartbeat("receiver"))


@app.get("/sender")
async def sender():
    return HTMLResponse(html_sender)


@app.get("/receiver")
async def receiver():
    return HTMLResponse(html_receiver)


@app.websocket("/ws/{client_type}")
async def websocket_endpoint(
    websocket: WebSocket, client_type: str, token: str = Depends(authenticate_user)
):
    await websocket.accept()
    clients[client_type].add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    finally:
        clients[client_type].remove(websocket)
