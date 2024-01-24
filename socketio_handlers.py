# socket_handlers.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def authenticate_user(token: str = Depends(oauth2_scheme)):
    # Perform authentication logic here, e.g., validate token
    # For simplicity, we'll use a dummy validation for illustration purposes
    if token != "dummy_token":
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

async def connect(sid, environ, data):
    token = data['token']
    if await authenticate_user(token):
        print(f"Client with {sid} connected")
        print(f"Client identity : {environ}")
    else:
        await disconnect(sid)

async def disconnect(sid):
    print(f"Client {sid} disconnected")

async def smartband_data(sid, data):
    from main_socketio import sio

    token = data['token']
    if await authenticate_user(token):
        print(f"Emitting smartband_data from {sid}: {data}")
        await sio.emit('update_dashboard', data, namespace='/report')
    else:
        await disconnect(sid)