import asyncio
import json
import logging
from typing import Any, Dict, Optional, Set, Callable, Awaitable
from typing import TYPE_CHECKING

import redis.asyncio as redis

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class InMemoryPubSub:
    """Fallback in-memory pub/sub when Redis is unavailable"""
    
    def __init__(self):
        self._channels: Dict[str, Set[asyncio.Queue]] = {}
    
    def subscribe(self, channel: str) -> asyncio.Queue:
        if channel not in self._channels:
            self._channels[channel] = set()
        queue = asyncio.Queue()
        self._channels[channel].add(queue)
        return queue
    
    def unsubscribe(self, channel: str, queue: asyncio.Queue):
        if channel in self._channels:
            self._channels[channel].discard(queue)
    
    async def publish(self, channel: str, message: str):
        if channel in self._channels:
            for queue in self._channels[channel]:
                await queue.put(message)


class RedisPubSub:
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._fallback: Optional[InMemoryPubSub] = None
        self._use_fallback = False
    
    async def get_client(self) -> Optional[redis.Redis]:
        if self._use_fallback:
            return None
        if self._client is None:
            logger.info(f"Creating Redis client with URL: {settings.redis_url}")
            try:
                self._client = redis.from_url(settings.redis_url)
                await self._client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}. Using in-memory fallback.")
                self._use_fallback = True
                self._fallback = InMemoryPubSub()
                return None
        return self._client
    
    def _get_fallback(self) -> InMemoryPubSub:
        if self._fallback is None:
            self._fallback = InMemoryPubSub()
        return self._fallback

    async def publish(self, channel: str, message: Dict[str, Any]) -> int:
        client = await self.get_client()
        json_msg = json.dumps(message)
        
        if client and not self._use_fallback:
            logger.info(f"Publishing to Redis channel {channel}: {json_msg[:200]}")
            result = await client.publish(channel, json_msg)
            logger.info(f"Published to {result} subscribers")
            return result
        else:
            logger.info(f"Publishing to in-memory channel {channel}: {json_msg[:200]}")
            await self._get_fallback().publish(channel, json_msg)
            return 1

    async def subscribe(self, channel: str):
        client = await self.get_client()
        if client and not self._use_fallback:
            pubsub = client.pubsub()
            await pubsub.subscribe(channel)
            return pubsub
        else:
            return self._get_fallback().subscribe(channel)

    async def listen(self, pubsub):
        async for msg in pubsub.listen():
            if msg['type'] == 'message':
                yield msg['data']

    async def close(self):
        if self._client:
            await self._client.close()


redis_pubsub = RedisPubSub()


async def get_redis_pubsub() -> RedisPubSub:
    return redis_pubsub