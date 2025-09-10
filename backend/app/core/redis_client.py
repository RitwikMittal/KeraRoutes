import redis.asyncio as redis
import logging
from app.core.config import settings

class RedisClient:
    redis_client: redis.Redis = None

redis_client = RedisClient()

async def get_redis_client():
   return redis_client.redis_client

async def connect_to_redis():
   """Create Redis connection"""
   try:
       redis_client.redis_client = redis.from_url(
           settings.REDIS_URL,
           db=settings.REDIS_DB,
           encoding="utf-8",
           decode_responses=True
       )
       
       # Test connection
       await redis_client.redis_client.ping()
       logging.info("Connected to Redis")
       
   except Exception as e:
       logging.error(f"Cannot connect to Redis: {e}")
       raise

async def close_redis_connection():
   """Close Redis connection"""
   if redis_client.redis_client:
       await redis_client.redis_client.close()
       logging.info("Disconnected from Redis")