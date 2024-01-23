import asyncio
import random
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

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
            var ws = new WebSocket("ws://localhost:8000/ws");
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
            var ws = new WebSocket("ws://localhost:8000/ws");
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

clients = []


async def send_heartbeat():
    while True:
        heartbeat_data = random.randint(40, 90)
        for client in clients:
            await client.send_text(f"Heartbeat: {heartbeat_data}")
        await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_heartbeat())


@app.get("/sender")
async def sender():
    return HTMLResponse(html_sender)


@app.get("/receiver")
async def receiver():
    return HTMLResponse(html_receiver)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    finally:
        clients.remove(websocket)
