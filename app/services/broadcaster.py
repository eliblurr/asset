from broadcaster import Broadcast
from pydantic import BaseModel
from config import REDIS_URL
from nm import Message

broadcast = Broadcast(REDIS_URL) 

async def chatroom_ws_receiver(websocket, channel):

    for message in Message.pop_messages(channel):
        await broadcast.publish(channel=channel, message=message)

    async for message in websocket.iter_text():
        await broadcast.publish(channel=channel, message=message)

async def chatroom_ws_sender(websocket, channel):
    try:
        async with broadcast.subscribe(channel=channel) as subscriber:
            async for event in subscriber:
                await websocket.send_text(event.message)
    except:
        if channel in broadcast._backend._subscribed:
            await broadcast._backend.unsubscribe(channel)
 
async def send_message(channel, message):
    if channel in broadcast._backend._subscribed:
        return await broadcast.publish(channel, json.dumps(message))
    Message.persist_message(channel, message, web_push_subscription=None)
