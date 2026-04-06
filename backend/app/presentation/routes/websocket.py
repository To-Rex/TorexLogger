import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from starlette.websockets import WebSocketState

from app.infrastructure.redis.pubsub import get_redis_pubsub

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str, level: Optional[str]):
        await websocket.accept()
        key = f"{project_id}:{level or 'all'}"
        if key not in self.active_connections:
            self.active_connections[key] = set()
        self.active_connections[key].add(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str, level: Optional[str]):
        key = f"{project_id}:{level or 'all'}"
        if key in self.active_connections:
            self.active_connections[key].discard(websocket)
            if not self.active_connections[key]:
                del self.active_connections[key]

    async def send_message(self, message: str, project_id: str, level: Optional[str]):
        all_key = f"{project_id}:all"
        level_key = f"{project_id}:{level}"

        connections_to_send: Set[WebSocket] = set()
        if all_key in self.active_connections:
            connections_to_send.update(self.active_connections[all_key])
        if level_key in self.active_connections:
            connections_to_send.update(self.active_connections[level_key])

        logger.info(f"Sending to {len(connections_to_send)} connections. Message: {message[:100]}")

        for connection in connections_to_send:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(json.loads(message))
            except Exception as e:
                logger.error(f"Error sending message: {e}")


manager = ConnectionManager()


@router.websocket("/ws/logs")
async def websocket_logs(
    websocket: WebSocket,
    project_id: str = Query(...),
    level: Optional[str] = Query(None),
):
    await manager.connect(websocket, project_id, level)
    pubsub = await get_redis_pubsub()
    channel = f"logs:{project_id}"
    
    pubsub_client = await pubsub.get_client()
    is_using_redis = pubsub_client is not None and not pubsub._use_fallback
    
    queue: Optional[asyncio.Queue] = None
    ps: Any = None
    
    async def listener():
        try:
            logger.info(f"Subscribing to channel: {channel}")
            nonlocal ps, queue
            if is_using_redis and pubsub_client:
                ps = pubsub_client.pubsub()
                await ps.subscribe(channel)
                async for msg in ps.listen():
                    if msg and msg.get('type') == 'message':
                        data = msg.get('data')
                        logger.info(f"Received message from Redis: {data}")
                        if data:
                            if isinstance(data, bytes):
                                data = data.decode('utf-8')
                            await manager.send_message(data, project_id, level)
            else:
                queue = await pubsub.subscribe(channel)
                while True:
                    data = await queue.get()
                    logger.info(f"Received message from memory: {data}")
                    if data:
                        await manager.send_message(data, project_id, level)
        except Exception as e:
            logger.error(f"Error in listener: {e}")

    listener_task = asyncio.create_task(listener())

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        listener_task.cancel()
        try:
            if is_using_redis and ps:
                await ps.unsubscribe(channel)
                await ps.close()
            elif queue and pubsub._fallback:
                pubsub._fallback.unsubscribe(channel, queue)
        except Exception:
            pass
        manager.disconnect(websocket, project_id, level)