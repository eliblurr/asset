from broadcaster import Broadcast
from pydantic import BaseModel
from config import REDIS_URL

class Publish(BaseModel):
    channel: str
    message: str

broadcast = Broadcast(REDIS_URL) 

async def chatroom_ws_receiver(websocket, channel):
    async for message in websocket.iter_text():
        await broadcast.publish(channel=channel, message=message)

async def chatroom_ws_sender(websocket, channel):
    async with broadcast.subscribe(channel=channel) as subscriber: # , history=100
        async for event in subscriber:
            await websocket.send_text(event.message)

async def send_message(publish:Publish):
    if broadcast._subscribers[publish.channel]:
        pass
        # if does not exist persist message # replace chatroom with tenant_id@user_id or replace numerical ids with UUIDs/ or send messages to email / or generate a socket_client_id for each user 
    await broadcast.publish(publish.channel, json.dumps([publish.message]))
    return publish